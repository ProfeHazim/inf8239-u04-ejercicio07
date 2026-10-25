# Decision Record — LAB11 · Evaluación de impacto ético

| Campo | Valor |
|---|---|
| Sistema | Territorial Review DSS — Synthetic |
| Unidad | INF-8239 · Unidad 04 · Gobernanza y DSS responsable |
| Fecha | 2026-10-25 |
| Propietario | Dirección de Análisis Territorial (rol institucional) |
| Insumos | `student_inputs/lab11_impact.yml`, `stakeholders.csv`, `risk_register.csv` |
| Evidencia generada | `reports/lab11/risk_register_scored.csv`, `stakeholders.csv`, `rmf_summary.json` |
| Estado de la medición | LAB12 **pendiente**: aún no existen métricas de equidad ni de desempeño |

## 1. Alcance evaluado

El sistema prioriza casos **sintéticos** de riesgo territorial para que un analista humano decida cuáles revisar primero. No decide intervenciones, elegibilidad ni declaratorias de emergencia. La decisión asistida es el **orden de una cola de revisión**; la decisión y la acción son humanas y deben quedar registradas.

Población afectada: personas y comunidades representadas en los casos; en un despliegue real, hogares de los distritos Norte, Sur, Este y Oeste, incluidos los grupos protegidos G1 y G2 y las personas de 60+.

## 2. Análisis de los tres riesgos prioritarios

Prioridad = probabilidad (1–4) × impacto (1–4), según `score_risks`.

### R02 — Sesgo de automatización · prioridad 9 (L3 × I3) · residual **medio**

El analista podría aceptar el orden del modelo sin revisar el caso, con lo que el puntaje decidiría de hecho y los casos al final de la cola no se mirarían nunca.

- **Afectados:** personas con puntaje bajo, que quedan postergadas sin revisión efectiva.
- **Control:** revisión obligatoria de una muestra aleatoria de casos no priorizados; interfaz que muestra incertidumbre y no permite acciones automáticas; registro de la decisión humana por caso.
- **Evidencia disponible:** ningún registro de decisiones todavía (no hay despliegue).
- **Incertidumbre:** no se conoce la tasa real de aceptación ciega del operador; depende de la interfaz y de la carga de trabajo.
- **Responsable:** Operator + supervisión.

### R01 — Sesgo histórico reproducido · prioridad 8 (L2 × I4) · residual **alto**

Los datos muestran tasas base distintas por grupo protegido (G2 0.639 vs G1 0.497 sobre 640 casos). Un modelo que aprenda de ellos puede priorizar por pertenencia al grupo en lugar de por necesidad, ampliando la ventaja existente.

- **Afectados:** personas de G1 y G2, en especial G2, por priorización basada en grupo y no en exposición o infraestructura.
- **Control:** auditoría de equidad en LAB12 con brechas de recall y de falsos positivos ≤ 0.16 (`configs/governance.yml`); comparación contra línea base sin features sensibles; revisión de la variante que excluye `protected_group`.
- **Evidencia disponible:** solo la tasa base descriptiva; **aún no hay métricas por subgrupo**.
- **Incertidumbre:** alta. Sin LAB12 no se sabe si el modelo amplifica, mantiene o reduce la brecha; el resultado puede cambiar el veredicto.
- **Responsable:** Data team + Institutional owner.

### R07 — Opacidad e impugnación · prioridad 8 (L2 × I4) · residual **alto**

Una persona afectada podría no entender por qué su caso quedó atrás ni tener una vía efectiva de reclamo, sin traza del motivo de la priorización.

- **Afectados:** personas y comunidades sin explicación ni mecanismo real de apelación.
- **Control:** registro de decisión por caso con las variables usadas; explicación en lenguaje claro; apelación con plazo de 10 días hábiles atendida por un revisor distinto.
- **Evidencia disponible:** el mecanismo está **documentado** en `lab11_impact.yml`, pero no implementado ni probado.
- **Incertidumbre:** media; el riesgo no es técnico sino operativo y depende de que la unidad sostenga el plazo de respuesta.
- **Responsable:** Institutional owner + Operator.

## 3. Riesgos secundarios

R03 (deriva temporal, 6), R06 (uso fuera de alcance, 6), R04 (reidentificación, 4), R05 (fallo operativo, 4) y R08 (restricción de despliegue, 3) están documentados con control y responsable en `risk_register_scored.csv`. Ninguno queda en residual alto.

## 4. Recomendación formal

> **REVISAR** — continuar a la medición de LAB12, **sin despliegue operativo**.

**Justificación.** Dos de los tres riesgos prioritarios (R01 y R07) mantienen residual **alto**, y el riesgo de mayor prioridad (R02) es de naturaleza humana, no técnica. La evaluación ética está completa y es trazable, pero el criterio de medición está explícitamente pendiente (`rmf_summary.json`: `MEASURE: LAB12 pending`). Autorizar un GO ahora implicaría afirmar un desempeño equitativo que todavía no se ha medido; detener el proyecto sería prematuro, porque no existe aún evidencia de daño y los controles están definidos.

### Condiciones para pasar de REVISAR a CONTINUAR

1. LAB12 reporta recall ≥ 0.68 y brechas de recall y FPR entre G1 y G2 ≤ 0.16.
2. Se documenta el resultado de la variante sin `protected_group` y se justifica la elegida.
3. El mecanismo de apelación (R07) queda implementado y probado con al menos un caso simulado de punta a punta.
4. Existe registro de decisión por caso y muestreo de control de casos no priorizados (R02).
5. Latencia ≤ 500 ms y tamaño ≤ 1024 KB verificados.

### Condiciones de detención inmediata

Se aplican las de `withdrawal_condition`: recall < 0.68, brecha > 0.16, ausencia de capacidad humana de revisión, incidente de daño documentado, o pérdida del propietario institucional o de la base legal.

### Vigencia

Esta decisión caduca al cerrar LAB12 o el **2027-01-31**, lo que ocurra primero. Debe revisarse antes de cualquier uso con datos no sintéticos.

---

**Firma:** Dirección de Análisis Territorial · **Fecha:** 2026-10-25 · **Estado:** REVISAR
