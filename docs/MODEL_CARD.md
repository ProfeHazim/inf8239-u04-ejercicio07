# Model Card — Territorial Review DSS (Synthetic)

**Sistema:** Territorial Review DSS — Synthetic · **Versión:** 0.1.0 (regresión logística) · **Unidad:** INF-8239, Unidad 04 · **Fecha:** 2026-10-25
**Propietario:** Dirección de Análisis Territorial · **Estado:** piloto con revisión humana (REVIEW), sin despliegue en producción.

## Intended use

Ordenar una cola de **casos sintéticos** de riesgo territorial para que un analista humano decida cuáles revisar primero. El modelo produce un puntaje de prioridad; **la decisión y la acción son humanas** y deben quedar registradas por caso.

- Decisión asistida: priorización de la cola de revisión.
- Usuarios: analistas de la unidad de análisis territorial y su supervisión; equipo de datos que opera el modelo.
- Población afectada (en un despliegue real): hogares de los distritos Norte, Sur, Este y Oeste, incluidos los grupos protegidos **G1** y **G2** y personas de **60+**.
- Autoridad final: el propietario institucional firma el decision record; el operador puede vetar casos individuales.

## Out-of-scope use

Prohibido usar el puntaje para:

- decidir intervenciones sobre personas o territorios;
- determinar elegibilidad de beneficios;
- sustentar declaratorias de emergencia;
- asignar recursos de forma vinculante;
- vigilar o perfilar poblaciones reales;
- operar como **evidencia única** de una decisión.

También prohibido: usar el modelo con datos personales reales sin DPIA, base legal y validación externa. El sistema **no autoriza decisiones automáticas sobre personas**.

## Data and split

- **Fuente:** `data/territorial_risk_synthetic.csv` — 640 casos sintéticos, semilla fija, sin personas, lugares ni estadísticas reales (ver `docs/DATASET_CARD.md`).
- **Split temporal** (no aleatorio): 480 casos de entrenamiento hasta **2026-09-24**; 160 casos de prueba desde **2026-09-25**.
- **Composición del test:** G1 = 101 (49 positivos, 52 negativos); G2 = 59 (43 positivos, 16 negativos).
- **Features:** `zone`, `age_band`, `previous_incidents`, `infrastructure_score`, `exposure`.
- **Excluidas:** `case_id`, `received_date`, `protected_group`, `target`.
- **Contrato de datos:** `validate_schema` rechaza columnas faltantes, identificadores directos (`name`, `document_number`, `email`, `phone`) y un `target` no binario.
- **Advertencia:** excluir `protected_group` del modelo **no elimina** el riesgo de sesgo; la pertenencia puede filtrarse por `zone` y `age_band`. Por eso la auditoría se hace sobre las predicciones.

## Global and subgroup evaluation

Auditoría con Fairlearn sobre el test temporal (160 casos). Detalle en `reports/lab12/` y `reports/lab12/uncertainty.json`.

| Métrica | Logístico (elegido) | Árbol (descartado) | Gate |
|---|---|---|---|
| Exactitud | **0.719** | 0.706 | — |
| Recall | 0.717 | 0.717 | ≥ 0.68 ✅ |
| Precisión | **0.776** | 0.759 | — |
| FPR | **0.279** | 0.309 | — |
| Brecha de recall | **0.138** ✅ | 0.181 ❌ | ≤ 0.16 |
| Brecha de FPR | **0.125** ✅ | 0.168 ❌ | ≤ 0.16 |

| Grupo | n | Recall | FPR |
|---|---|---|---|
| G1 | 101 | **0.653** | 0.250 |
| G2 | 59 | 0.791 | 0.375 |

**Hallazgos críticos.**

1. **G1 queda bajo el recall mínimo (0.653 < 0.68)**, aunque el recall global (0.717) lo supere. El gate automático evalúa solo el agregado; el criterio de `student_inputs/lab12_decision.yml` exige además recall por grupo ≥ 0.68.
2. **G1 | 45-59** es la peor celda con soporte: exactitud 0.600, recall **0.588**, FPR 0.389. Es el daño prioritario (falsos negativos: ~4 de cada 10 positivos no llegan a revisión).
3. **G2 | 60+** tiene FPR **0.556** — casi el doble del agregado — con recall 0.765. El valor es **idéntico en ambos modelos**, por lo que el sesgo es estructural (datos/umbral), no de forma funcional.
4. Celdas con **n < 15** (G2 | 45-59 n=8; G2 | 18-29 n=11; G2 | 30-44 n=14) se excluyen del análisis por falta de soporte.

**Incertidumbre (bootstrap, 2,000 réplicas, semilla 42).** Brecha de recall del logístico 0.138, IC95 **[-0.041, 0.321]**; brecha de FPR 0.125, IC95 **[-0.125, 0.396]**. Recall de G1 IC95 **[0.513, 0.771]** y **P(recall G1 < 0.68) = 64.5%**. Los intervalos cruzan cero y llegan al doble del gate: **"pasar el gate" no demuestra equidad**.

**Divergencia documentada entre el gate automático y la decisión humana.** `scripts/lab13_governance.py` devuelve **GO** (`reports/lab13/deployment_decision.json`) porque `deployment_decision()` evalúa `metrics["recall"]` **global**. El propietario institucional sostiene **REVIEW** aplicando el criterio adicional por grupo. El gate es condición **necesaria, no suficiente**; la decisión final es humana (`human_action`). Esta divergencia es un hallazgo de gobernanza, no un error de cálculo.

## Green AI evidence

| Indicador | Valor | Gate | Estado |
|---|---|---|---|
| Tamaño del modelo | **3.56 KB** | ≤ 1,024 KB | ✅ 0.35% del límite |
| Latencia de inferencia | **0.040 ms/caso** | ≤ 500 ms | ✅ ~12,500× por debajo |
| Tiempo de entrenamiento | **0.079 s** (logístico) · 0.116 s (árbol) | — | ✅ |
| Consumo de cómputo | Modelo lineal + one-hot; sin GPU ni red neuronal | — | ✅ |

El logístico es 2.2× más pequeño y 1.5× más rápido de entrenar que el árbol, con mejor desempeño: **no existe un trade-off de sostenibilidad frente a utilidad**. La elección del modelo más simple es a la vez la más barata y la más justa en el agregado. Medición de latencia: `src/inf8239_u04/pipeline.py:10` (por caso, sobre 160 casos).

## Limitations, human oversight and appeal

**Limitaciones.**

1. Datos **sintéticos**: no representan personas ni territorios reales; los hallazgos son didácticos y no se generalizan.
2. Test de **160 casos** con una **sola** ventana temporal; G2 tiene solo 16 negativos. Intervalos de confianza amplios por construcción.
3. **Sin validación externa** ni datos de otro periodo que confirmen la estabilidad de las brechas.
4. **Deriva no medida**: existe split temporal, pero no monitoreo en operación.
5. **Sin técnicas de mitigación** aplicadas (reweighting, equalized odds, calibración por grupo); el expediente audita y decide, no corrige.
6. El sesgo en **G2 | 60+** no se resuelve cambiando de modelo.
7. La **latencia** se midió en el entorno de desarrollo, no en el entorno institucional de despliegue.

**Supervisión humana (obligatoria).**

- El operador revisa el caso y registra su decisión; el puntaje **no** ejecuta acciones.
- Se revisa una **muestra aleatoria de casos no priorizados** para contrarrestar el sesgo de automatización (R02).
- El operador puede vetar cualquier caso individual.
- El propietario institucional aprueba todo cambio de alcance y firma el decision record.

**Apelación.** Toda persona o comunidad afectada puede solicitar revisión humana mediante el formulario de la unidad, con respuesta en **10 días hábiles**, atendida por un analista **distinto** del que priorizó y registrada en el expediente del caso.

**Condiciones de retiro.** Recall < 0.68; brecha de recall o FPR > 0.16; ausencia de capacidad humana de revisión; incidente de daño documentado; pérdida del propietario institucional o de la base legal. En cualquiera de estos casos se retorna a la alternativa no predictiva (muestreo estratificado por distrito).

## Owner and review date

- **Propietario:** Dirección de Análisis Territorial (rol institucional).
- **Responsable técnico:** equipo de datos (R en RACI para monitoreo).
- **Última revisión:** 2026-10-25.
- **Próxima revisión obligatoria:** al cierre de la siguiente iteración de medición o el **2027-01-31**, lo que ocurra primero.
- **Disparadores de revisión extraordinaria:** incidente de daño, cambio de esquema o de distribución de datos, cambio de base legal, o cualquier uso propuesto fuera del alcance declarado.
