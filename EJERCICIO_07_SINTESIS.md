# Ejercicio 07 — Síntesis de gobernanza y auditoría de equidad

**Unidad 04 · Gobernanza y DSS responsable · INF-8239**
Consolidación de las evidencias de LAB11 (evaluación de impacto ético) y LAB12 (auditoría de equidad con Fairlearn).

| Campo | Valor |
|---|---|
| Sistema evaluado | Territorial Review DSS — Synthetic |
| Autor | Jesús Miguel Díaz Hazim |
| Fecha de cierre | 2026-10-25 |
| Propietario institucional | Dirección de Análisis Territorial (rol) |
| Alcance | Priorización de casos sintéticos para revisión humana |
| Decisión final | **REVISAR — piloto con revisión humana; sin despliegue en producción** |
| Modelo recomendado | **Regresión logística** (árbol descartado) |
| Evidencia | `reports/lab11/`, `reports/lab12/{logistic,tree}/`, `reports/lab12/uncertainty.json` |

> **Nota de alcance.** Este documento integra LAB11 y LAB12. LAB13 (runbook de incidentes, model card final y Green AI) corresponde al Ejercicio 08 y queda fuera de este expediente.

---

## Resumen ejecutivo

El sistema ordena una cola de casos sintéticos de riesgo territorial para que un analista humano decida cuáles revisar primero. No decide intervenciones, elegibilidad ni declaratorias de emergencia.

La evaluación ética (LAB11) documentó propósito, cuatro interesados, una alternativa no predictiva viable y ocho riesgos con control, responsable y evidencia. La auditoría (LAB12) comparó una regresión logística contra un árbol de decisión sobre un split temporal de 160 casos.

**La regresión logística domina al árbol en todas las dimensiones medidas** — mayor exactitud (0.719 vs 0.706), igual recall (0.717), mejor precisión (0.776 vs 0.759), menor tasa de falsos positivos (0.279 vs 0.309), brechas más pequeñas (recall 0.138 vs 0.181; FPR 0.125 vs 0.168), 2.2× menos tamaño (3.56 KB vs 7.87 KB) y 1.5× menos tiempo de entrenamiento (0.079 s vs 0.116 s). El árbol **incumple ambos gates** de brecha del marco de gobernanza.

Sin embargo, el logístico **no está certificado como equitativo**:

1. Su recall en **G1 es 0.653**, por debajo del gate de 0.68, y el bootstrap estima **64.5% de probabilidad** de que el recall real de G1 esté bajo ese umbral.
2. Las brechas agregadas pasan el gate (0.138 y 0.125), pero sus intervalos de confianza al 95% son **[-0.041, 0.321]** y **[-0.125, 0.396]**: compatibles tanto con equidad perfecta como con un incumplimiento severo.
3. Las dos celdas interseccionales con daño relevante son **G1 | 45-59** (recall 0.588) y **G2 | 60+** (FPR 0.556). Esta última es **idéntica en ambos modelos**, lo que indica que el daño es estructural y no se corrige cambiando el algoritmo.

**Conclusión:** el logístico es el único candidato defendible, pero solo en **piloto con revisión humana obligatoria**. No hay base estadística para autorizar producción.

---

## 1. Finalidad, interesados y proporcionalidad (LAB11)

### 1.1 Propósito y decisión asistida

**Propósito.** Priorizar casos sintéticos de riesgo territorial para revisión humana, de modo que los analistas ordenen su carga de trabajo por probabilidad estimada de incidente. El sistema **no decide** intervenciones sobre personas ni territorios: solo ordena una cola.

**Decisión asistida.** El modelo produce un puntaje de prioridad; el analista decide si abre o no una revisión territorial y deja constancia de su decisión. La autoridad decisoria es humana e identificable.

**Población afectada.** Personas y comunidades representadas en los casos; en un despliegue real, hogares de los distritos Norte, Sur, Este y Oeste, incluidos los grupos protegidos **G1 y G2** y las personas de **60 años o más**.

**Propietario.** Dirección de Análisis Territorial, responsable del propósito, de la base legal de los datos y de la decisión de retirar el sistema.

### 1.2 Alternativa no predictiva y proporcionalidad

La alternativa evaluada es una **revisión por muestreo aleatorio estratificado por distrito**, con lista de verificación de infraestructura y exposición y una regla simple que prioriza los casos con más incidentes previos. Exige más esfuerzo humano por caso, pero no puntúa personas ni requiere datos sensibles.

El análisis de proporcionalidad se sostiene en cuatro elementos:

| Criterio | Evaluación |
|---|---|
| **Intrusión** | Baja: el sistema reordena una cola; no aplica sanciones ni asigna beneficios. |
| **Necesidad** | Discutible: la alternativa no predictiva es viable y ya existe como línea base. El beneficio del modelo es eficiencia de triaje, no capacidad nueva. |
| **Beneficio esperado** | Moderado: reduce tiempo de triaje y homogeneiza criterios entre analistas. |
| **Daño potencial** | Exclusión de revisión para quien queda al final de la cola; estigma por grupo o edad; opacidad ante la persona afectada. |

**Veredicto de proporcionalidad.** El sistema es proporcional **solo** si el daño se acota con revisión humana efectiva, muestreo de control de la cola no priorizada y una vía de apelación operativa. Sin esos tres controles, la alternativa no predictiva es preferible porque obtiene un beneficio comparable sin puntuar personas.

### 1.3 Interesados

| Interesado | Beneficio | Daño | Poder | Participación |
|---|---|---|---|---|
| **Persona afectada** | Revisión más oportuna de su caso | Priorización opaca; estigma por G1/G2 o edad; quedar sin revisión | Bajo | Solicita revisión humana y presenta queja; no participa en el diseño |
| **Operador (analista)** | Cola ordenada, menos triaje manual, criterios homogéneos | Sobreconfianza en el puntaje; carga de justificar cada caso | Medio | Calibración, registro de incidentes, veto de casos individuales |
| **Propietario institucional** | Mejor uso del presupuesto, trazabilidad, rendición de cuentas | Responsabilidad legal y reputacional; presión por automatizar de más | Alto | Aprueba propósito, riesgos y retiro; firma el decision record |
| **Equipo de datos** | Pipeline reproducible, métricas auditables | Presión por relajar controles; deuda técnica y fallos silenciosos | Medio | Opera el pipeline, monitorea deriva, latencia y tamaño |

**Asimetría crítica.** El interesado con **menor poder** (la persona afectada) es quien concentra el **mayor daño potencial** y el único que no participa en el diseño. Los tres controles de la sección 1.2 existen precisamente para compensar esa asimetría; por eso su ausencia operativa es un hallazgo, no un detalle.

### 1.4 Usos prohibidos, retiro y apelación

**Prohibido:** decidir intervenciones, elegibilidad de beneficios, declaratorias de emergencia o asignación vinculante de recursos; vigilancia o perfilamiento de poblaciones reales; usar el puntaje como evidencia única de una decisión.

**Retiro del sistema si:** el recall cae por debajo de 0.68; la brecha de recall o de FPR entre G1 y G2 supera 0.16; no existe capacidad humana para revisar la cola; se documenta un incidente de daño atribuible al puntaje; o se pierde el propietario institucional o la base legal.

**Apelación:** toda persona o comunidad puede solicitar revisión humana mediante el formulario de la unidad, con respuesta en **10 días hábiles**, atendida por un analista **distinto** del que priorizó y registrada en el expediente.

---

## 2. Riesgos críticos y mitigación según NIST AI RMF

### 2.1 Correspondencia con las funciones del marco

| Función | Implementación en este expediente | Evidencia |
|---|---|---|
| **GOVERN** | Propietario nombrado, usos prohibidos, condiciones de retiro, decision record firmado | `lab11_impact.yml`, `configs/governance.yml`, `reports/lab11/DECISION_RECORD.md` |
| **MAP** | Contexto, población afectada, interesados y ocho riesgos con afectado y escenario | `student_inputs/stakeholders.csv`, `risk_register.csv` |
| **MEASURE** | Métricas globales, por grupo e interseccionales; bootstrap de incertidumbre; recursos | `reports/lab12/`, `reports/lab12/uncertainty.json` |
| **MANAGE** | Controles por riesgo, piloto con revisión humana, condiciones de producción y de detención, retorno a la alternativa no predictiva | `reports/lab11/DECISION_RECORD.md`, `lab12_decision.yml` |

### 2.2 Registro de riesgos (8 escenarios)

Prioridad = probabilidad (1–4) × impacto (1–4).

| ID | Escenario | Prioridad | Residual |
|---|---|---|---|
| R02 | Sesgo de automatización: el analista acepta el orden sin revisar | **9** | Medio |
| R01 | Sesgo histórico reproducido por grupo protegido | **8** | **Alto** |
| R07 | Opacidad e impugnación sin traza ni vía efectiva | **8** | **Alto** |
| R03 | Deriva temporal: el recall cae bajo el umbral | 6 | Medio |
| R06 | Uso fuera de alcance (elegibilidad, emergencia) | 6 | Medio |
| R04 | Reidentificación en un despliegue no sintético | 4 | Medio |
| R05 | Fallo operativo del pipeline | 4 | Bajo |
| R08 | Restricción de despliegue (latencia o tamaño) | 3 | Bajo |

### 2.3 Los tres riesgos prioritarios y lo que LAB12 cambió

**R02 — Sesgo de automatización (prioridad 9, residual medio).**
El analista podría aceptar el orden del modelo sin revisar, con lo que el puntaje decidiría de hecho y la cola final nunca se miraría. *Control:* muestreo aleatorio obligatorio de casos no priorizados, interfaz que expone la incertidumbre, registro de la decisión humana. *Estado tras LAB12:* **no medido**. No existe aún registro de decisiones, porque no hay piloto. Sigue siendo el riesgo de mayor prioridad y es de naturaleza humana, no algorítmica.

**R01 — Sesgo histórico reproducido (prioridad 8, residual alto).**
Las tasas base difieren entre grupos (G2 0.639 vs G1 0.497). LAB12 **confirma que el riesgo es material**: el logístico alcanza recall 0.791 en G2 frente a 0.653 en G1. *Lo que LAB12 aporta:* la brecha agregada (0.138) queda dentro del gate, pero el recall de G1 queda por debajo de 0.68 y el intervalo de confianza de la brecha llega hasta 0.321. *Conclusión:* el riesgo **no se cierra**, solo se acota; sigue en residual alto.

**R07 — Opacidad e impugnación (prioridad 8, residual alto).**
La persona afectada no puede entender ni impugnar por qué su caso quedó atrás. *Control:* registro por caso, explicación en lenguaje claro, apelación con plazo atendida por un revisor distinto. *Estado tras LAB12:* **documentado pero no implementado**. El mecanismo existe en el papel; no se ha probado de punta a punta.

### 2.4 Riesgos que la auditoría modifica

- **R03 (deriva):** el split temporal se ejecutó correctamente (entrenamiento hasta 2026-09-24, prueba desde 2026-09-25), pero con **una sola ventana**, por lo que la deriva no está medida; el monitoreo mensual sigue pendiente.
- **R08 (restricción de despliegue):** el tamaño se cumple con holgura (3.56 KB frente a 1,024 KB), pero **la latencia de inferencia no se midió**; solo se registró tiempo de entrenamiento. El gate de 500 ms queda sin evidencia.

---

## 3. Resultados de la auditoría de equidad (LAB12)

### 3.1 Diseño de evaluación

- **Split temporal** (no aleatorio): 480 casos de entrenamiento hasta 2026-09-24; **160 casos de prueba** desde 2026-09-25.
- **Features del modelo:** `zone`, `age_band`, `previous_incidents`, `infrastructure_score`, `exposure`.
- **Excluidas explícitamente:** `case_id`, `received_date`, `protected_group`, `target`.
- **Composición del test:** G1 = 101 casos (49 positivos, 52 negativos); G2 = 59 casos (43 positivos, 16 negativos).
- **Métricas:** exactitud, selection rate, recall (TPR), precisión y FPR, globales, por grupo e interseccionales (`protected_group × age_band`).

Excluir `protected_group` del modelo **no elimina el riesgo**: la pertenencia puede filtrarse por `zone` y `age_band`. Por eso la auditoría se hace sobre las predicciones, no sobre las features.

### 3.2 Métricas globales

| Métrica | Logístico | Árbol | Gate |
|---|---|---|---|
| Exactitud | **0.719** | 0.706 | — |
| Recall | 0.717 | 0.717 | ≥ 0.68 ✅ |
| Precisión | **0.776** | 0.759 | — |
| FPR | **0.279** | 0.309 | — |
| Selection rate | **0.531** | 0.544 | — |
| Tamaño | **3.56 KB** | 7.87 KB | ≤ 1,024 KB ✅ |
| Entrenamiento | **0.079 s** | 0.116 s | — |
| Latencia de inferencia | **no medida** | no medida | ≤ 500 ms ❓ |

Ambos modelos empatan en recall global; el logístico gana en todo lo demás. El árbol no aporta ninguna ventaja que compense su peor comportamiento por grupo.

### 3.3 Métricas por grupo

| Grupo | n | Exactitud | Recall | Precisión | FPR |
|---|---|---|---|---|---|
| **Logístico — G1** | 101 | 0.703 | **0.653** | 0.711 | 0.250 |
| **Logístico — G2** | 59 | 0.746 | **0.791** | 0.850 | 0.375 |
| **Árbol — G1** | 101 | 0.683 | **0.633** | 0.689 | 0.269 |
| **Árbol — G2** | 59 | 0.746 | **0.814** | 0.833 | 0.438 |

| Brecha entre grupos | Logístico | Árbol | Gate |
|---|---|---|---|
| Recall | **0.138** ✅ | 0.181 ❌ | ≤ 0.16 |
| FPR | **0.125** ✅ | 0.168 ❌ | ≤ 0.16 |
| Exactitud | 0.043 | 0.063 | — |
| Selection rate | 0.232 | 0.266 | — |

El árbol **incumple los dos gates de brecha**; el logístico los cumple. Pero conviene leer la tabla con cuidado: el gate se cumple por **0.022 de margen** en recall y por **0.035** en FPR, sobre muestras de 49 y 43 positivos. Es un aprobado estrecho, no una garantía.

### 3.4 Análisis interseccional

Se aplicó un criterio de **soporte mínimo n ≥ 15** por celda. Se excluyen por insuficiencia: **G2 | 45-59 (n=8)**, **G2 | 18-29 (n=11)** y **G2 | 30-44 (n=14)**. Sus valores extremos (recall 1.0 y FPR 0.0 en una celda de 8 casos) son artefactos de muestra, no hallazgos.

**Celdas con soporte suficiente:**

| Celda | n | Logístico: exact. / recall / FPR | Árbol: exact. / recall / FPR |
|---|---|---|---|
| G1 \| 18-29 | 18 | 0.833 / 0.750 / 0.143 | 0.778 / 0.750 / 0.214 |
| G1 \| 30-44 | 24 | 0.667 / 0.563 / 0.125 | 0.625 / 0.625 / 0.375 |
| G1 \| 45-59 | 35 | **0.600 / 0.588 / 0.389** | 0.686 / 0.647 / 0.278 |
| G1 \| 60+ | 24 | 0.792 / 0.833 / 0.250 | 0.667 / 0.583 / 0.250 |
| G2 \| 60+ | 26 | **0.654 / 0.765 / 0.556** | **0.654 / 0.765 / 0.556** |

### 3.5 Hallazgo 1 — Falsos positivos en adultos mayores (G2 | 60+)

En **G2 | 60+**, ambos modelos clasifican como positivo al **55.6% de los casos negativos** (FPR 0.556), con exactitud 0.654 y recall 0.765. Es la FPR más alta entre las celdas con soporte, y **casi el doble** de la FPR global del logístico (0.279).

Dos observaciones que cambian la interpretación:

1. **El daño es estructural.** Las predicciones son **idénticas** en logístico y árbol para esta celda (mismos valores en las seis métricas). Cambiar de algoritmo **no corrige** este sesgo, porque no proviene de la forma funcional sino de cómo las features disponibles (`exposure`, `infrastructure_score`, `age_band`) separan a este subgrupo.
2. **El daño es de sobrepriorización.** Un FPR alto en un sistema de triaje significa que personas mayores de G2 reciben **revisión innecesaria**: consume capacidad humana limitada y puede estigmatizar al subgrupo como "sospechoso por defecto". No es el daño más grave en abstracto, pero compite por el mismo recurso que necesitan los casos de G1 que hoy se pierden.

**Implicación de gobernanza:** este hallazgo no se resuelve eligiendo entre los dos modelos existentes. Requiere intervención sobre los datos o sobre el umbral de decisión, y debe entrar al piloto como objetivo explícito de monitoreo.

### 3.6 Hallazgo 2 — Recall bajo en G1 | 45-59

En **G1 | 45-59** el logístico alcanza el peor desempeño entre las celdas con soporte: exactitud **0.600**, recall **0.588** y FPR 0.389. Es decir, **cuatro de cada diez casos positivos de este subgrupo no se priorizan** y quedan al final de la cola.

Este es el daño prioritario del expediente, porque es un **falso negativo**: la persona con riesgo real no llega a revisión humana. El promedio de G1 (recall 0.653) ya estaba bajo el gate; la desagregación interseccional muestra que **la banda 45-59 es la que arrastra ese promedio**, mientras G1 | 60+ alcanza 0.833.

Aquí sí hay una diferencia relevante entre modelos: el árbol obtiene mejor recall en esta celda (0.647 vs 0.588), pero **a costa de una brecha global peor** (0.181) y de un FPR más alto en G1 | 30-44 (0.375 vs 0.125). No compensa: el árbol mejora una celda y empeora el agregado y otras celdas.

### 3.7 Incertidumbre: bootstrap sobre el conjunto de prueba

Se remuestreó el test **2,000 veces con reemplazo** (sin reentrenar), con semilla 42, para estimar la estabilidad de las brechas. Script reproducible: `scripts/lab12_uncertainty.py`; salida: `reports/lab12/uncertainty.json`.

| Estimación | Logístico | Árbol |
|---|---|---|
| Recall G1 (IC95 Wilson) | 0.653 **[0.513, 0.771]** | 0.633 **[0.493, 0.753]** |
| Recall G2 (IC95 Wilson) | 0.791 [0.648, 0.886] | 0.814 [0.674, 0.903] |
| Brecha de recall (IC95) | 0.138 **[-0.041, 0.321]** | 0.181 **[-0.006, 0.352]** |
| Brecha de FPR (IC95) | 0.125 **[-0.125, 0.396]** | 0.168 **[-0.116, 0.462]** |
| P(brecha de recall > 0.16) | **39.1%** | **57.8%** |
| P(brecha de FPR > 0.16) | **39.1%** | **53.2%** |
| P(recall G1 < 0.68) | **64.5%** | **74.0%** |
| P(recall G2 < 0.68) | 4.1% | 2.0% |

**Cómo leer estas cifras.** Ningún intervalo de confianza de las brechas excluye el cero: los datos **no permiten afirmar** que exista una brecha, ni tampoco que no la haya. Lo que sí permiten afirmar es que **un incumplimiento severo es perfectamente compatible con lo observado** (el límite superior de la brecha de recall del logístico es 0.321, el doble del gate).

La probabilidad de que el recall real de G1 esté bajo 0.68 es **64.5%** en el logístico y **74.0%** en el árbol. Es la razón técnica por la que la recomendación es piloto y no producción: el gate no está demostrado, está **apenas aprobado en la muestra**.

Un detalle de transparencia metodológica: en la corrida con semilla 42, `P(brecha recall > 0.16)` y `P(brecha FPR > 0.16)` resultaron exactamente iguales (0.3905) para el logístico. Se verificó con las semillas 7, 99 y 2026 — donde difieren (≈0.41 vs 0.38) — y se confirmó que fue una **coincidencia del generador aleatorio**, no un error del cálculo.

---

## 4. Decisión final y justificación

### 4.1 Por qué el modelo logístico

**1. Domina en utilidad sin costo en recall.** Igual recall global (0.717), mayor exactitud (0.719 vs 0.706) y mayor precisión (0.776 vs 0.759). No hay escenario medido en el que el árbol sea preferible en el agregado.

**2. Es el único que cumple los gates de brecha.** Brecha de recall 0.138 y de FPR 0.125, ambas bajo 0.16. El árbol incumple las dos (0.181 y 0.168). En términos de probabilidad bootstrap de incumplir, el logístico es 39.1% vs 57.8% (recall) y 39.1% vs 53.2% (FPR): **el árbol es sustancialmente más probable que incumpla**.

**3. Menor probabilidad de violar el recall mínimo de G1.** 64.5% vs 74.0%. Ninguno lo garantiza, pero el logístico es la opción menos mala.

**4. Es más barato y más simple.** 3.56 KB frente a 7.87 KB; 0.079 s frente a 0.116 s de entrenamiento; menos parámetros y mayor interpretabilidad para efectos de explicación y apelación (R07).

**5. Complejidad no justificada.** El árbol añade capacidad expresiva que no se traduce en mejor desempeño, pero sí en mayor varianza entre celdas pequeñas (por ejemplo, FPR 0.375 en G1 | 30-44 frente a 0.125 del logístico). En un dominio donde el daño es la exclusión, la varianza alta es un pasivo, no un activo.

### 4.2 Por qué solo piloto con revisión humana

**1. El gate de recall de G1 no está demostrado.** El recall puntual es 0.653 < 0.68, con 64.5% de probabilidad de que el valor real esté bajo el umbral. Un sistema que pierde un tercio de los casos positivos de un grupo protegido no puede operar sin red de seguridad.

**2. Las brechas agregadas son un aprobado estadísticamente frágil.** Los IC95 cruzan cero y llegan hasta 0.321 (recall) y 0.396 (FPR). Afirmar equidad con estos datos sería una extrapolación, no un hallazgo.

**3. El daño prioritario es de falsos negativos y se concentra en G1 | 45-59** (recall 0.588). La revisión humana de la cola **no priorizada** —no solo de la priorizada— es el control que convierte ese daño en recuperable.

**4. Dos riesgos de residual alto siguen abiertos.** R01 (sesgo) está acotado pero no cerrado; R07 (opacidad) está documentado pero no implementado. Desplegar en producción con R07 abierto contradice la propia condición de retiro del LAB11.

**5. El daño en G2 | 60+ no se corrige con ningún modelo disponible.** Un FPR de 0.556 idéntico en ambos modelos exige intervención sobre datos o umbral, y ese trabajo no existe todavía.

**6. La alternativa no predictiva sigue disponible.** Si el piloto no mejora el recall de G1 en la siguiente iteración, el retorno al muestreo estratificado no produce una pérdida de capacidad, solo de eficiencia.

### 4.3 Condiciones para pasar de piloto a producción

1. Recall de G1 ≥ 0.68, con prioridad explícita en la banda **G1 | 45-59**.
2. Brechas de recall y FPR ≤ 0.16, verificadas con **una ventana temporal adicional** (no la misma partición).
3. FPR de **G2 | 60+** reducido mediante ajuste de umbral o recalibración, con evidencia antes/después.
4. Mecanismo de apelación (R07) **implementado y probado** de punta a punta con al menos un caso simulado.
5. Registro de decisión por caso y muestreo de control de la cola no priorizada (R02) en operación.
6. Latencia de inferencia medida y ≤ 500 ms (hoy sin evidencia).

### 4.4 Condiciones de detención inmediata

Recall < 0.68 sostenido; brecha > 0.16 en cualquier métrica de daño; ausencia de capacidad humana de revisión; incidente de daño documentado; pérdida del propietario institucional o de la base legal. En cualquiera de estos casos se activa el retorno a la alternativa no predictiva.

### 4.5 Vigencia

La decisión caduca al cierre de la siguiente iteración de medición o el **2027-01-31**, lo que ocurra primero. Debe revisarse antes de cualquier uso con datos no sintéticos.

---

## 5. Declaración de uso responsable de IA

**Herramienta.** Asistente de IA (DeepSeek V4.1 Flash 1017, ejecutado en el entorno OpenCode) utilizado como apoyo técnico y de redacción durante las fases LAB11 y LAB12.

**Finalidad y fragmentos afectados.**

| Área | Intervención de la IA |
|---|---|
| Estructura del expediente | Organización de secciones, tablas y correspondencia con NIST AI RMF |
| `student_inputs/lab11_impact.yml`, `stakeholders.csv`, `risk_register.csv` | Borrador de contenido a partir del propósito y del marco de gobernanza |
| `student_inputs/lab12_decision.yml` | Redacción de la decisión con las cifras de la auditoría |
| `reports/lab11/DECISION_RECORD.md` | Borrador del registro de decisión |
| `scripts/lab12_uncertainty.py` y `reports/lab12/uncertainty.json` | **Generación íntegra** del análisis de bootstrap e intervalos de confianza |
| Pruebas y validación | Generación del script de incertidumbre, ejecución de `pytest` y del validador de decisión, y verificación de que las cifras citadas coinciden con los reportes |
| Redacción de esta síntesis | Borrador completo |

**Verificaciones humanas.** La interpretación normativa, la elección del daño prioritario, la métrica principal, la tolerancia y la **decisión final (piloto con revisión humana, sin producción)** fueron revisadas y validadas por el estudiante. Las cifras del documento se contrastaron contra los archivos de evidencia del repositorio.

**Errores detectados y corregidos.**

1. **Bug real del proyecto base:** `scripts/lab11_impact.py` no compilaba (`SyntaxError: unterminated string literal`) porque el `write_text` del decision record usaba comillas dobles para un texto de tres líneas. Se corrigió con un string triple. Sin esta corrección, la validación de LAB11 era imposible.
2. **Riesgo de sobrescritura:** el mismo script regenera `reports/lab11/DECISION_RECORD.md` con un placeholder en cada ejecución. Se documentó el orden correcto (script primero, decisión después) para evitar perder el registro firmado.
3. **Falsa alarma verificada:** la coincidencia exacta de dos probabilidades bootstrap se contrastó con otras semillas y se confirmó como artefacto del generador, no como error de cálculo.

**Límites de la asistencia.** La IA no sustituye la validación con datos reales ni la revisión jurídica. Los datos son sintéticos y los resultados **no se generalizan** a población real. Toda cifra de este expediente es reproducible con los comandos del Anexo A.

---

## Anexo A — Reproducibilidad

```bash
uv sync --frozen
uv run python scripts/describe_dataset.py
uv run python scripts/lab11_impact.py
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/lab12_uncertainty.py
uv run python scripts/validate_lab12_decision.py
uv run pytest -q
```

`uv run pytest -q` → **10 pruebas aprobadas**. El script de incertidumbre usa semilla 42 y 2,000 réplicas, por lo que sus cifras son deterministas.

## Anexo B — Inventario de evidencia

| Archivo | Contenido |
|---|---|
| `reports/lab11/DECISION_RECORD.md` | Decisión formal de LAB11 (REVISAR) con condiciones |
| `reports/lab11/risk_register_scored.csv` | 8 riesgos con prioridad calculada |
| `reports/lab11/stakeholders.csv` | Interesados con beneficio, daño, poder y participación |
| `reports/lab11/rmf_summary.json` | Resumen GOVERN / MAP / MEASURE / MANAGE |
| `reports/lab12/logistic/` | Métricas globales, por grupo e interseccionales del logístico |
| `reports/lab12/tree/` | Métricas globales, por grupo e interseccionales del árbol |
| `reports/lab12/uncertainty.json` | Bootstrap: IC95, Wilson y probabilidad de cruzar el gate |
| `student_inputs/lab11_impact.yml` | Propósito, decisión asistida, usos prohibidos, retiro y apelación |
| `student_inputs/lab12_decision.yml` | Daño prioritario, métrica, tolerancia, evidencia, limitación y recomendación |
| `configs/governance.yml` | Gates y usos prohibidos del sistema |

## Anexo C — Limitaciones del expediente

1. **Datos sintéticos.** No representan personas, territorios ni estadísticas reales; los hallazgos son didácticos.
2. **Test pequeño y una sola partición.** 160 casos, G2 con solo 16 negativos. Los intervalos de confianza son amplios por construcción.
3. **Latencia no medida.** El gate de 500 ms está sin evidencia; solo se midió tiempo de entrenamiento.
4. **Sin validación externa.** No hay datos de otro periodo ni de otra fuente que confirme la estabilidad de las brechas.
5. **R02 y R07 no medidos en operación.** Los controles están diseñados, no ejecutados; el piloto es precisamente el mecanismo para probarlos.
6. **No se aplicaron técnicas de mitigación** (reweighting, equalized odds, calibración por grupo). El expediente audita y decide; la mitigación corresponde a la siguiente iteración.