import streamlit as st
from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config
from inf8239_u04.pipeline import run
st.set_page_config(page_title="Governed Green DSS",layout="wide")
st.title("DSS territorial sintético · Gobernanza y Green AI")
st.warning("Demostración educativa con datos sintéticos. No autoriza decisiones automáticas ni representa estadísticas reales.")
cfg=load_config(); gates=cfg["gates"]; result=run(load_data(),gates)
by_group=result["by_group"]; gate_status=result["decision"]["status"]
below=[(g,float(row["recall"])) for g,row in by_group.iterrows() if float(row["recall"])<gates["min_recall"]]
state="REVIEW" if (gate_status!="GO" or below) else "GO"
if state=="REVIEW":
    detalle=", ".join(f"{g} = {r:.3f}" for g,r in below)
    st.error(
        f"ESTADO REAL: {state} — piloto con revisión humana obligatoria. "
        f"El gate automático indica {gate_status} porque evalúa solo el recall global "
        f"({result['metrics']['recall']:.3f} >= {gates['min_recall']}), pero el recall por grupo está bajo el mínimo: "
        f"{detalle}. No uses el puntaje como decisión."
    )
else:
    st.success(f"Estado: {state} — todos los gates, incluido el recall por grupo, se cumplen.")
st.subheader("Propósito y autoridad"); st.write(cfg["purpose"]); st.write("Usos prohibidos:",", ".join(cfg["prohibited_uses"]))
c1,c2,c3=st.columns(3)
c1.metric("Accuracy",f"{result['metrics']['accuracy']:.3f}")
c2.metric("Recall global",f"{result['metrics']['recall']:.3f}")
c3.metric("Decisión (humana)",state,help="El gate automático es condición necesaria; la decisión final la firma el propietario institucional.")
st.caption(f"Gate automático: {gate_status} · fallos: {result['decision']['failed'] or 'ninguno'} · latencia: {result['resources']['latency_ms']:.3f} ms · tamaño: {result['resources']['model_kb']:.2f} KB")
st.subheader("Métricas por grupo"); st.dataframe(by_group,width="stretch")
st.subheader("Puertas de calidad"); st.json(result["decision"])
st.info("Acción humana: revisar evidencia, documentar la decisión y activar apelación o rollback cuando corresponda.")
