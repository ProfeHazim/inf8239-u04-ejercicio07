# Incident simulation

> **Aviso:** simulacro didáctico sobre datos sintéticos. No corresponde a un daño real ni a personas reales. Se conserva el `detected_at` generado por `scripts/simulate_incident.py`.

- detected_at: 2026-10-25T15:09:51.276044+00:00
- signal: recall gap exceeded
- containment: REVIEW and safe baseline
- evidence: preserved report and model version
- communication: pendiente de cierre (ver §4)
- corrective actions, owners and dates: ver §5

**ID:** INC-2026-10-25-01 · **Severidad:** S2 (alto) · **Estado:** contenido, en seguimiento
**Sistema:** Territorial Review DSS — Synthetic v0.1.0 (regresión logística) · **Owner:** Dirección de Análisis Territorial

---

## 1. Cronología

| Hora (UTC) | Evento | Responsable |
|---|---|---|
| 15:09:51 | `lab13_governance.py` registra el estado del sistema. El gate agregado devuelve **GO** (recall global 0.717 ≥ 0.68). | Data Scientist |
| 15:10 | Revisión manual de `fairness_by_group.csv`: **recall de G1 = 0.653 < 0.68**. El gate no lo evalúa porque solo comprueba el agregado. | Data Scientist |
| 15:11 | Clasificación como **S2** (criterio: recall de un grupo bajo el mínimo). Se abre INC-2026-10-25-01. | Data Scientist |
| 15:15 | **Contención N1:** se congela la priorización; el sistema queda en REVIEW. No se autoriza producción. | ML Engineer |
| 15:20 | Evidencia preservada: reportes de LAB12, `deployment_decision.json`, hash del modelo, `uv.lock`. | ML Engineer |
| 15:30 | Se notifica al propietario institucional. Se mantiene la decisión **REVIEW / piloto con revisión humana**. | Institutional Owner |
| 15:40 | Se confirma que la brecha agregada (0.138) está dentro del gate, pero el criterio por grupo de `lab12_decision.yml` no se cumple. | Data Scientist |
| 15:45 | Se documenta la divergencia gate-vs-decisión en `MODEL_CARD.md` y en este postmortem. | Data Scientist |

## 2. Impacto

- **Casos afectados:** 160 casos del test temporal (simulación). En producción, el impacto se estima en los casos positivos de **G1 \| 45-59**, donde el recall es **0.588**: aproximadamente **4 de cada 10** personas con riesgo real no habrían sido priorizadas.
- **Grupos:** G1 (n=101) con recall 0.653; G2 (n=59) con recall 0.791. Brecha 0.138.
- **Duración:** 0 minutos de operación real — el incidente se detectó **antes** de cualquier despliegue.
- **Decisiones afectadas:** ninguna. El sistema nunca operó en producción.
- **Daño a personas:** **ninguno** (datos sintéticos, sin despliegue). El valor del simulacro es haber detectado el defecto de gobernanza antes del daño.

## 3. Causa raíz

**Causa inmediata.** El recall del grupo G1 (0.653) está por debajo del mínimo de 0.68 definido en el marco de gobernanza.

**Causa contribuyente (la más importante).** El gate automático `deployment_decision()` (`src/inf8239_u04/governance.py:14-23`) evalúa únicamente `metrics["recall"]` **global**. No existe una comprobación de recall por subgrupo, por lo que un sistema que excluye sistemáticamente a un grupo puede obtener **GO**. El `human_action` ("Document review and final decision") era el único control que cubría este hueco, y dependía de una revisión manual no formalizada.

**Causa de gobernanza.** El criterio por grupo estaba escrito en `student_inputs/lab12_decision.yml`, pero **no** en `configs/governance.yml`. Dos fuentes de verdad con distinto nivel de exigencia: la máquina aplicó la más laxa.

**Por qué no se detectó antes.** La auditoría de LAB12 sí identificó el hallazgo; lo que faltó fue **convertirlo en un gate ejecutable**. La lección: un hallazgo que no se codifica como verificación automática tiende a perderse.

## 4. Comunicación

| Audiencia | Acción | Estado |
|---|---|---|
| Propietario institucional | Notificación en ≤ 2 h con alcance y contención | ✅ 15:30 UTC |
| Equipo operativo | Briefing: no usar el puntaje como decisión; registrar cada caso | ✅ |
| Legal / DPO | No aplica: datos sintéticos, sin datos personales, sin despliegue | ✅ N/A documentado |
| Personas afectadas | No aplica en simulación. En un caso real: comunicación en ≤ 5 días hábiles con vía de apelación (10 días hábiles, revisor distinto) | ✅ N/A |
| Autoridad competente | No aplica | ✅ N/A |

**Mensaje interno emitido:** «El sistema permanece en REVIEW. El gate automático indica GO por recall global, pero el recall de G1 está bajo el mínimo. No se autoriza producción. La priorización se mantiene con revisión humana obligatoria y muestreo de control de la cola no priorizada.»

## 5. Acciones correctivas

| # | Acción | Responsable (R) | Accountable (A) | Fecha límite | Criterio de cierre verificable |
|---|---|---|---|---|---|
| A1 | Añadir verificación de **recall por subgrupo** y de brecha por subgrupo al gate de despliegue | Data Scientist | Institutional Owner | 2026-11-15 | Prueba automatizada que devuelve REVIEW cuando el recall de un grupo < 0.68 |
| A2 | Unificar el criterio de equidad en `configs/governance.yml` (una sola fuente de verdad) | Data Scientist | Institutional Owner | 2026-11-08 | `governance.yml` contiene `min_group_recall` y el pipeline lo consume |
| A3 | Intervención sobre **G1 \| 45-59**: ajuste de umbral o recalibración por grupo | Data Scientist | Institutional Owner | 2026-11-30 | Recall de G1 \| 45-59 ≥ 0.68 en una ventana temporal nueva |
| A4 | Reducir el **FPR de G2 \| 60+** (0.556) mediante umbral o recalibración | Data Scientist | Institutional Owner | 2026-11-30 | FPR de G2 \| 60+ ≤ 0.40 con evidencia antes/después |
| A5 | Formalizar el **muestreo de control** de la cola no priorizada (R02) | Operator | Institutional Owner | 2026-11-15 | Registro mensual de la muestra revisada y sus hallazgos |
| A6 | Implementar y probar la **apelación** de punta a punta (R07) | Operator | Institutional Owner | 2026-11-15 | Un caso simulado recorre solicitud → revisor distinto → respuesta ≤ 10 días |
| A7 | Medir la latencia en el entorno institucional (hoy solo en desarrollo) | ML Engineer | Institutional Owner | 2026-11-08 | Reporte de latencia p95 ≤ 500 ms en el entorno objetivo |

**Ninguna acción se cierra por declaración: se cierra con evidencia enlazada en `reports/lab13/actions.csv`.**

## 6. ¿Se cumple una condición de retiro?

**No.** El sistema nunca operó, no hay daño documentado y el recall de G1 es recuperable mediante umbral/recalibración. Se mantiene **REVIEW con revisión humana**, no se activa el retiro (N4). Si A3 no logra recall ≥ 0.68 en la próxima iteración, **se activará la condición de retiro** y se pasará a la línea base no predictiva (N3).

## 7. Qué funcionó y qué falló

**Funcionó.** La auditoría de LAB12 detectó el problema antes del despliegue; la preservación de evidencia fue inmediata; el propietario institucional pudo sostener REVIEW frente a un gate que decía GO; el costo de contención fue nulo.

**Falló.** El gate automático no cubría el criterio que realmente importaba; existían dos definiciones de equidad con distinta exigencia; el `human_action` no tenía un procedimiento escrito que obligara a revisar el desempeño por grupo.

**Riesgos del registro actualizados.** **R01** (sesgo histórico): confirmado material, sigue en residual alto. **R02** (automatización): se refuerza la necesidad del muestreo de control. **R07** (opacidad): la apelación sigue sin implementar (A6). **R03** (deriva): el monitoreo por grupo pasa a ser requisito del gate.

---

**Postmortem elaborado por:** Data Scientist (R) · **Aprobado por:** Institutional Owner (A) · **Fecha:** 2026-10-25 · **Próxima revisión:** 2026-11-15
