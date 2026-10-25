"""Bootstrap de incertidumbre para la auditoría de equidad de LAB12.

Remuestrea el conjunto de prueba (no reentrena) para estimar cuán estables son
las brechas entre grupos. No sustituye la auditoría de lab12_audit.py: la
complementa, porque el test temporal tiene solo 160 casos.
"""
import json
from pathlib import Path

import numpy as np

from inf8239_u04.data import features, load_data, temporal_split
from inf8239_u04.model import build_model

N_BOOT = 2000
GATE_GAP = 0.16
GATE_RECALL = 0.68


def rates(frame, group):
    sub = frame[frame.protected_group == group]
    pos = sub.target == 1
    neg = ~pos
    tp = int(((sub.pred == 1) & pos).sum())
    fn = int(((sub.pred == 0) & pos).sum())
    fp = int(((sub.pred == 1) & neg).sum())
    tn = int(((sub.pred == 0) & neg).sum())
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")
    return recall, fpr, int(pos.sum()), int(neg.sum()), tp


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return [float((c - h) / d), float((c + h) / d)]


def main():
    df = load_data()
    train, test = temporal_split(df)
    rng = np.random.default_rng(42)
    out = {"n_test": int(len(test)), "n_bootstrap": N_BOOT, "models": {}}

    for kind in ("logistic", "tree"):
        model = build_model(kind).fit(features(train), train.target)
        scored = test.assign(pred=model.predict(features(test))).reset_index(drop=True)
        groups = sorted(scored.protected_group.unique())

        cells = {}
        for g in groups:
            recall, fpr, n_pos, n_neg, tp = rates(scored, g)
            cells[g] = {
                "n": int((scored.protected_group == g).sum()),
                "n_pos": n_pos,
                "n_neg": n_neg,
                "recall": float(recall),
                "recall_wilson95": wilson(tp, n_pos),
                "fpr": float(fpr),
            }

        rec_gap, fpr_gap = [], []
        rec_by_group = {g: [] for g in groups}
        for _ in range(N_BOOT):
            idx = rng.integers(0, len(scored), len(scored))
            sample = scored.iloc[idx]
            boot = {g: rates(sample, g) for g in groups}
            for g in groups:
                rec_by_group[g].append(boot[g][0])
            rec_gap.append(boot["G2"][0] - boot["G1"][0])
            fpr_gap.append(boot["G2"][1] - boot["G1"][1])

        rec_gap = np.asarray(rec_gap, dtype=float)
        fpr_gap = np.asarray(fpr_gap, dtype=float)
        out["models"][kind] = {
            "groups": cells,
            "recall_gap": {
                "point": float(cells["G2"]["recall"] - cells["G1"]["recall"]),
                "ci95": [float(np.percentile(rec_gap, 2.5)), float(np.percentile(rec_gap, 97.5))],
                "p_exceeds_gate": float((rec_gap > GATE_GAP).mean()),
            },
            "fpr_gap": {
                "point": float(cells["G2"]["fpr"] - cells["G1"]["fpr"]),
                "ci95": [float(np.percentile(fpr_gap, 2.5)), float(np.percentile(fpr_gap, 97.5))],
                "p_exceeds_gate": float((fpr_gap > GATE_GAP).mean()),
            },
            "recall_below_gate": {
                g: {
                    "point": float(cells[g]["recall"]),
                    "p_below_gate": float((np.asarray(rec_by_group[g]) < GATE_RECALL).mean()),
                }
                for g in groups
            },
        }

    path = Path("reports/lab12/uncertainty.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
