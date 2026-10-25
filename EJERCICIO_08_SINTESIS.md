# Ejercicio 08 — Síntesis de gobernanza operativa y DSS responsable

**Unidad 04 · Gobernanza y DSS responsable · INF-8239**
Consolidación de las evidencias de LAB13 (privacidad, monitoreo, respuesta a incidentes y Green AI).

| Campo | Valor |
|---|---|
| Sistema evaluado | Territorial Review DSS — Synthetic v0.1.0 |
| Autor | Jesús Miguel Díaz Hazim |
| Fecha de cierre | 2026-10-25 |
| Propietario institucional (A) | Dirección de Análisis Territorial |
| Gate automático | **GO** — 5/5 checks en verde |
| **Decisión final (humana)** | **REVIEW — piloto con revisión humana, sin producción** |
| Artefactos | `docs/MODEL_CARD.md`, `docs/RUNBOOK.md`, `student_inputs/raci.csv`, `reports/lab13/` |
| Tag de cierre | `u04-lab13` |

> **Nota de alcance.** Este expediente integra LAB13. La evaluación ética (LAB11) y la auditoría de equidad (LAB12) se consolidaron en `EJERCICIO_07_SINTESIS.md`, que se cita como evidencia y no se duplica aquí.

---

## Resumen ejecutivo

El sistema prioriza casos sintéticos de riesgo territorial para revisión humana. LAB13 añade la capa operativa que faltaba: inventario y minimización de datos, model card trazable, matriz RACI extendida, monitoreo con umbrales, runbook de incidentes con cuatro niveles de rollback y un simulacro con postmortem.

**El hallazgo central de esta fase es una divergencia de gobernanza:** el gate automático devuelve **GO** porque evalúa solo el recall **global** (0.717 ≥ 0.68), mientras que el recall del grupo protegido **G1 es 0.653**, por debajo del mínimo. La decisión humana —y ética— es **REVIEW**. El gate es condición **necesaria, no suficiente**, y el simulacro demostró que el sistema detecta el problema antes de cualquier daño.

**Evidencia Green AI:** 3.56 KB de modelo, ≈0.05 ms por caso de inferencia (0.040–0.051 ms entre corridas), ~0.08–0.10 s de entrenamiento, sin GPU. El modelo elegido es a la vez el más barato y el más justo en el agregado: no hay *trade-off* entre sostenibilidad y utilidad.

---

## 1. Inventario, minimización y retención

### 1.1 Inventario de datos

| Elemento | Contenido | Naturaleza |
|---|---|---|
| `data/territorial_risk_synthetic.csv` | 640 filas × 9 columnas | **Sintético**, semilla fija, sin personas, lugares ni tasas reales |
| `reports/lab11/`, `reports/lab12/` | Riesgos, interesados, métricas, bootstrap | Derivados agregados, sin identificadores |
| `reports/lab13/` | Decisión de despliegue, fairness, postmortem | Evidencia de gobernanza |
| `models/*.joblib` | Modelo entrenado | Artefacto binario, **excluido de Git** (`.gitignore`) |
| `configs/governance.yml` | Gates y usos prohibidos | Política versionada |

**Columnas del dataset y su uso:**

| Columna | Uso | ¿Entra al modelo? |
|---|---|---|
| `case_id` | Trazabilidad del caso | **No** |
| `received_date` | Split temporal | **No** (solo partición) |
| `zone` | Feature | Sí (one-hot) |
| `protected_group` | **Solo auditoría de equidad** | **No** |
| `age_band` | Feature | Sí (one-hot) |
| `previous_incidents` | Feature | Sí (escalado) |
| `infrastructure_score` | Feature | Sí (escalado) |
| `exposure` | Feature | Sí (escalado) |
| `target` | Etiqueta de evaluación | **No** (variable objetivo) |

### 1.2 Minimización aplicada

1. **Exclusión de identificadores directos, verificada en código.** `validate_schema()` (`src/inf8239_u04/data.py:12-17`) rechaza `name`, `document_number`, `email` y `phone` con excepción explícita. La prueba `tests/test_privacy.py` lo verifica: añadir `name` hace fallar la validación. **No es una recomendación: es un contrato ejecutable.**
2. **Exclusión de `protected_group` como feature.** El atributo sensible se usa **solo** para medir brechas, nunca para predecir. Se reconoce la limitación de que puede filtrarse por `zone` y `age_band`, y por eso la auditoría se hace sobre predicciones.
3. **`case_id` y `received_date` fuera del modelo.** El identificador no aporta señal y la fecha solo define la partición temporal.
4. **Reducción de columnas en la interfaz.** El dashboard muestra métricas agregadas por grupo; no expone microdatos ni identificadores.
5. **Evidencia sin personas.** Los reportes de incidentes usan `case_id`, nunca datos personales.
6. **Modelo no versionado como binario.** Se excluye `*.joblib` de Git: se reconstruye desde `uv.lock`, evitando distribuir artefactos opacos.

### 1.3 Retención

**Implementado hoy:**

- Dataset sintético versionado en Git (repositorio académico, sin datos personales).
- Evidencia de incidentes en `reports/lab13/incident_<ID>/` con **retención mínima de 5 años** o la exigida por Legal, la mayor (`docs/RUNBOOK.md` §3).
- `models/*.joblib` excluidos del repositorio.

**Política propuesta para un despliegue real (pendiente de aprobación, no implementada):**

| Dato | Retención | Base | Borrado |
|---|---|---|---|
| Casos individuales | ≤ 24 meses desde el cierre del caso | Necesidad operativa | Automático al vencer |
| Registro de decisiones humanas | 5 años | Rendición de cuentas y apelaciones | Revisión anual |
| Métricas agregadas | Indefinida | No contienen datos personales | N/A |
| Evidencia de incidentes | 5 años | Obligación legal y auditoría | Solo por orden de Legal |
| Identificadores directos | **No se almacenan** | Minimización en origen | N/A |

**Principio:** si un dato no es necesario para la decisión ni para rendir cuentas, **no se recoge**. La retención por defecto es la mínima viable, y toda excepción requiere justificación del propietario institucional.

---

## 2. Datasheet y Model Card trazables

### 2.1 Datasheet

`docs/DATASET_CARD.md` declara: dataset **sintético** generado con semilla fija, **sin personas, ubicaciones, tasas ni estadísticas oficiales reales**; destinado a practicar contratos de datos, evaluación temporal, auditoría de subgrupos y gobernanza. **Prohibido:** perfilamiento operativo o inferencia sobre poblaciones reales.

Esto acota el riesgo de privacidad de forma radical: no hay titulares de datos que puedan ser reidentificados. Cualquier uso con datos reales queda **fuera del alcance** y exigiría DPIA, base legal y validación externa (ver Model Card).

### 2.2 Model Card

`docs/MODEL_CARD.md` (107 líneas), con siete secciones:

| Sección | Contenido clave |
|---|---|
| **Intended use** | Priorizar la cola de revisión; decisión y acción humanas |
| **Out-of-scope use** | Intervenciones, elegibilidad, emergencia, vigilancia, evidencia única |
| **Data and split** | 640 casos; 480 entrenamiento (hasta 2026-09-24) / 160 prueba (desde 2026-09-25) |
| **Global and subgroup evaluation** | Logístico vs árbol; G1 0.653 vs G2 0.791; G1\|45-59 0.588; G2\|60+ FPR 0.556; bootstrap |
| **Green AI evidence** | 3.56 KB · ≈0.05 ms/caso · 0.079 s entrenamiento · sin GPU |
| **Limitations, human oversight and appeal** | Datos sintéticos, test pequeño, deriva no medida, apelación 10 días |
| **Owner and review date** | Dirección de Análisis Territorial · revisión 2027-01-31 |

**Trazabilidad.** Cada afirmación de la Model Card remite a un archivo verificable:

| Afirmación | Evidencia | Verificación |
|---|---|---|
| Métricas globales y brechas | `reports/lab12/logistic/global_metrics.json` | `uv run python scripts/lab12_audit.py --model logistic` |
| Métricas por grupo | `reports/lab12/logistic/fairness_by_group.csv` | ídem |
| Interseccional | `reports/lab12/logistic/fairness_intersectional.csv` | ídem |
| Incertidumbre | `reports/lab12/uncertainty.json` | `uv run python scripts/lab12_uncertainty.py` |
| Gates y decisión | `reports/lab13/deployment_decision.json` | `uv run python scripts/lab13_governance.py` |
| Green AI | `resources` en el mismo JSON | ídem |
| Incidente | `reports/lab13/INCIDENT_POSTMORTEM.md` | simulación documentada |

**Cómo accede el usuario a la Model Card.**

1. **Equipo interno y evaluadores:** archivo `docs/MODEL_CARD.md` en el repositorio, bajo control de versiones (`git log -- docs/MODEL_CARD.md` muestra su evolución). Está enlazado desde este expediente y desde `EJERCICIO_07_SINTESIS.md`.
2. **Operadores:** la Model Card es parte del material de incorporación antes de usar el sistema; el runbook la referencia en la revisión de límites.
3. **Personas afectadas:** solicitan la información en lenguaje claro y la revisión de su caso mediante el formulario de la unidad, con respuesta en **10 días hábiles** a cargo de un revisor distinto del que priorizó.
4. **Limitación reconocida:** el dashboard **no** publica todavía un enlace a la Model Card. Es una mejora pendiente y de bajo costo.

---

## 3. RACI y traspaso entre roles

### 3.1 Matriz ampliada

Se partió de 4 actividades y se completó a **8**, incorporando las que LAB13 exige (privacidad, monitoreo, apelación y retiro). Cada actividad tiene **exactamente un Accountable (A)** y **al menos un Responsible (R)**, verificado programáticamente.

| Actividad | R | **A** | C | I |
|---|---|---|---|---|
| Data quality | Data Engineer | Product Owner | Data Scientist | Affected representatives |
| Model validation | Data Scientist | Product Owner | Data Engineer | Affected representatives |
| Deployment | ML Engineer | Product Owner | Data Scientist | Users |
| **Incident response** | ML Engineer | **Institutional Owner** | Legal; Data Scientist | Affected representatives |
| **Privacy and DPIA** | Data Protection Officer | **Institutional Owner** | Legal; Data Scientist | Affected representatives |
| **Monitoring and drift alerts** | Data Scientist | **Institutional Owner** | ML Engineer | Operator |
| **Appeal and human review** | Operator | **Institutional Owner** | Legal | Affected representatives |
| **Decommissioning** | ML Engineer | **Institutional Owner** | Data Scientist; Legal | Affected representatives; Users |

### 3.2 Quién responde y quién retira

- **Accountable de la respuesta a incidentes: el Institutional Owner.** Ninguna reanudación del servicio puede ocurrir con un incidente S1 abierto. El ML Engineer **contiene** (pausa, congela) sin esperar aprobación; el Institutional Owner **decide** la reanudación.
- **Accountable del retiro del modelo: el Institutional Owner**, con C de Legal y R de ML Engineer. La ejecución técnica del retiro (N4) es del ML Engineer; la **decisión** es del propietario.
- **El operador conserva poder de veto** sobre casos individuales sin aprobación: es el rol con menos poder formal pero con capacidad de protección inmediata de la persona.

### 3.3 Traspaso entre roles (handover)

| Paso | De → A | Entregable | Plazo |
|---|---|---|---|
| Detección | Data Scientist → ML Engineer | Ticket de incidente con severidad | ≤ 4 h acuse |
| Contención | ML Engineer → Institutional Owner | Estado congelado + evidencia preservada (hash) | ≤ 2 h en S1 |
| Decisión | Institutional Owner → Legal / DPO | Decisión firmada (continuar, revisar, retirar) | ≤ 2 h en S1 |
| Comunicación | Institutional Owner → afectados | Mensaje en lenguaje claro + vía de apelación | ≤ 5 días hábiles |
| Cierre | Data Scientist → Institutional Owner | Postmortem con acciones, dueños y fechas | ≤ 5 días hábiles |

**Riesgo detectado en la propia matriz (autocrítica).** El Institutional Owner es **A en 5 de 8 actividades**, incluida toda la cadena de incidentes y retiro. Esa concentración crea un **punto único de fallo**: vacaciones, rotación o conflicto de interés pueden paralizar la respuesta. **Mitigación recomendada:** designar un *deputy* formal con autoridad delegada documentada y un plazo máximo de respuesta. Hoy no está implementado; queda registrado como acción de gobernanza.

---

## 4. Monitoreo, runbook y simulacro

### 4.1 Monitoreo

| Señal | Umbral | Frecuencia | Responsable |
|---|---|---|---|
| Recall global | < 0.68 | Por lote / mensual | Data Scientist |
| **Recall por grupo (G1, G2)** | **< 0.68** | Mensual | Data Scientist |
| Brecha de recall / FPR | > 0.16 | Mensual | Data Scientist |
| FPR de G2 \| 60+ | > 0.556 (baseline) | Mensual | Data Scientist |
| Deriva de datos | PSI > 0.2 o cambio de esquema | Semanal | Data Engineer |
| Uso fuera de alcance | Cualquier indicio | Continuo | Cualquier persona |
| Privacidad / reidentificación | Cualquier indicio | Continuo | DPO |

**Punto clave:** la señal de **recall por grupo** existe en el monitoreo **aunque no exista en el gate automático**. Esa asimetría es precisamente lo que el simulacro expuso.

### 4.2 Runbook — estructura y tiempos

`docs/RUNBOOK.md` (150 líneas) define seis bloques operativos:

| Bloque | Contenido | Tiempos |
|---|---|---|
| 1. Detección y clasificación | Señales, detectores, severidades **S1–S4** | S1 ≤ 2 h · S2 ≤ 24 h · S3 ≤ 72 h · S4 ≤ 5 días |
| 2. Autoridad de contención | Quién puede pausar, congelar, suspender, retirar | Pausa inmediata **sin aprobación**; reanudación **solo** con el A |
| 3. Preservación de evidencia | Reportes, hash del modelo, commit, `uv.lock`, cadena de custodia | Inmediato, antes de corregir |
| 4. Comunicación | Interna, Legal/DPO, afectados, autoridad | Afectados ≤ **5 días hábiles** |
| 5. Rollback / línea base | **N1** pausa (15 min) · **N2** versión previa (2 h) · **N3** línea base no predictiva (24 h) · **N4** retiro (24 h) | Ver columna |
| 6. Postmortem | Cronología, causa raíz, acciones con dueño y fecha | ≤ **5 días hábiles** |

**Principio operativo:** ante duda, **contener primero y analizar después**. **N3 por defecto ante cualquier S1**, porque no requiere puntuar personas.

### 4.3 Simulacro de incidente

**INC-2026-10-25-01 · Severidad S2 · Contenido, en seguimiento.**
Postmortem: `reports/lab13/INCIDENT_POSTMORTEM.md`.

**Secuencia real del simulacro:**

1. `lab13_governance.py` devuelve **GO** con 5/5 checks en verde.
2. La revisión manual de `fairness_by_group.csv` detecta **recall de G1 = 0.653 < 0.68**.
3. Se clasifica como **S2**, se activa contención **N1** y el sistema queda en **REVIEW**.
4. Se preserva evidencia y se notifica al propietario institucional.
5. No se cumple ninguna condición de retiro; se abre seguimiento con **7 acciones correctivas** con dueño, fecha y criterio de cierre verificable.

**El hallazgo de gobernanza (el más importante de la fase).**

> El gate automático `deployment_decision()` (`src/inf8239_u04/governance.py:14-23`) evalúa **solo** `metrics["recall"]` global. Un sistema que excluye sistemáticamente a un grupo puede obtener **GO**. El criterio por grupo existía en `student_inputs/lab12_decision.yml`, pero **no** en `configs/governance.yml`: dos fuentes de verdad con distinta exigencia, y la máquina aplicó la más laxa.

**Causa raíz en tres niveles:**

| Nivel | Causa |
|---|---|
| Inmediata | Recall de G1 (0.653) bajo el mínimo de 0.68 |
| Contribuyente | El gate no comprueba recall por subgrupo; el `human_action` dependía de una revisión manual no formalizada |
| **De gobernanza** | Criterio de equidad definido en un archivo que el pipeline no consume |

**Lo que funcionó:** la auditoría detectó el defecto **antes** de cualquier despliegue; la contención no tuvo costo; el propietario pudo sostener REVIEW frente a un gate que decía GO.

**Lo que falló:** un hallazgo que no se codifica como verificación automática tiende a perderse.

**Acciones correctivas destacadas:** A1 (añadir recall por subgrupo al gate, 2026-11-15), A2 (unificar criterio en `governance.yml`, 2026-11-08), A3 (recuperar G1 \| 45-59, 2026-11-30), A6 (apelación de punta a punta, 2026-11-15).

### 4.4 Green AI

| Indicador | Valor | Gate | Margen |
|---|---|---|---|
| Tamaño | **3.56 KB** | ≤ 1,024 KB | 0.35% del límite |
| Latencia | **0.045 ms/caso** (0.040–0.051 entre corridas) | ≤ 500 ms | más de **10,000×** por debajo |
| Entrenamiento | **0.08–0.10 s** | — | Sin GPU |
| Arquitectura | Regresión logística + one-hot | — | Sin red neuronal |

El logístico es 2.2× más pequeño y 1.5× más rápido de entrenar que el árbol, **y además** obtiene mejor exactitud, precisión y brechas. La elección sostenible coincide con la elección justa: no hay compromiso.

---

## 5. Decisión final

### 5.1 El hecho

El sistema arrojó **GO**. Los cinco checks del gate están en verde:

| Check | Valor | Gate | Resultado |
|---|---|---|---|
| Recall | 0.717 | ≥ 0.68 | ✅ |
| Brecha de recall | 0.138 | ≤ 0.16 | ✅ |
| Brecha de FPR | 0.125 | ≤ 0.16 | ✅ |
| Latencia | 0.045 ms | ≤ 500 ms | ✅ |
| Tamaño | 3.56 KB | ≤ 1,024 KB | ✅ |

### 5.2 Por qué la decisión es REVIEW de todos modos

**1. El gate mide el promedio, no la equidad.** Un recall global de 0.717 puede convivir con un grupo en 0.653. De hecho, eso es exactamente lo que ocurre. Un sistema que pierde **un tercio de los casos positivos de G1** no puede operar sin red de seguridad, aunque su promedio sea aceptable.

**2. El criterio más estricto ya estaba decidido.** `student_inputs/lab12_decision.yml` exige recall **por grupo** ≥ 0.68. Ese criterio es posterior y más específico que el gate agregado; ignorarlo sería *elegir la métrica que conviene*, no gobernar.

**3. La incertidumbre impide afirmar equidad.** El bootstrap da una brecha de recall con IC95 **[-0.041, 0.321]** y **P(recall G1 < 0.68) = 64.5%**. El límite superior del intervalo duplica el gate. No hay base estadística para declarar el sistema seguro.

**4. El daño es de falsos negativos y se concentra.** **G1 \| 45-59** tiene recall **0.588**: ~4 de cada 10 personas con riesgo real no serían priorizadas. Es el daño más grave posible en un sistema de triaje, porque es silencioso: nadie reclama por una revisión que nunca ocurrió.

**5. Hay un daño estructural que ningún modelo disponible corrige.** **G2 \| 60+** tiene FPR **0.556**, idéntico en logístico y árbol. El sesgo vive en los datos y en el umbral, no en la forma funcional.

**6. R02 y R07 siguen abiertos.** El sesgo de automatización (prioridad 9) y la opacidad (prioridad 8) están diseñados como controles, pero **no ejecutados**. Desplegar en producción con ambos abiertos contradice la propia condición de retiro de LAB11.

**7. La proporcionalidad exige la opción menos intrusiva.** El beneficio del modelo es **eficiencia de triaje**, no capacidad nueva. La alternativa no predictiva (muestreo estratificado) sigue disponible y no puntúa personas.

### 5.3 El principio de gobernanza

> **Un gate verde es una condición necesaria, no una autorización.** La decisión final la firma una persona accountable, y esa persona debe poder decir "no" cuando la métrica agregada oculta un daño distribuido.

Esto no es un fallo del sistema: es el sistema funcionando. El `human_action` del gate ("Document review and final decision") existe precisamente para este caso. El simulacro demostró que el control humano **detecta lo que el gate no ve**.

### 5.4 Condiciones para pasar a producción

1. Recall de **G1 ≥ 0.68**, con prioridad en **G1 \| 45-59**.
2. Brechas ≤ 0.16 verificadas en **una ventana temporal adicional**.
3. FPR de **G2 \| 60+** reducido con evidencia antes/después.
4. Apelación (R07) **implementada y probada** de punta a punta.
5. Registro de decisiones y muestreo de control (R02) **en operación**.
6. Latencia medida **en el entorno institucional** (hoy solo en desarrollo).
7. Gate de despliegue con **recall por subgrupo** (acción A1) y criterio unificado (A2).
8. *Deputy* formal del Accountable designado (mitigación de la concentración en la RACI).

### 5.5 Condiciones de detención

Recall < 0.68 sostenido; brecha > 0.16; ausencia de capacidad humana de revisión; incidente de daño documentado; pérdida del propietario institucional o de la base legal. En cualquiera de estos casos se activa **N3/N4** y se retorna a la alternativa no predictiva.

### 5.6 Vigencia

La decisión caduca al cierre de la siguiente iteración de medición o el **2027-01-31**, lo que ocurra primero, y debe revisarse antes de cualquier uso con datos no sintéticos.

---

## 6. Declaración de uso responsable de IA

**Herramienta.** Asistente de IA (DeepSeek V4.1 Flash 1017, en el entorno OpenCode), usado como apoyo técnico y de redacción durante LAB11, LAB12 y LAB13.

### 6.1 Tabla de uso

| Área | Intervención de la IA |
|---|---|
| **Codificación** | Corrección de dos scripts del proyecto base que no compilaban; generación de `scripts/lab12_uncertainty.py` (bootstrap, 107 líneas) |
| **Corrección de bugs** | `scripts/lab11_impact.py`: `SyntaxError: unterminated string literal` (comillas simples en texto multilínea) → string triple. `scripts/simulate_incident.py`: `SyntaxError: unterminated f-string` → f-string triple |
| **Hallazgo de gobernanza** | Detección de la divergencia entre el gate agregado (**GO**) y el recall por grupo (**G1 = 0.653 < 0.68**), y de que `deployment_decision()` no evalúa subgrupos |
| **Análisis estadístico** | Bootstrap de 2,000 réplicas, intervalos de Wilson y probabilidad de cruzar el gate |
| **Redacción** | Borradores de `EJERCICIO_07_SINTESIS.md`, `EJERCICIO_08_SINTESIS.md`, Model Card, Runbook, postmortem y registros de decisión |
| **Mitigación R02** | Aviso visual en el dashboard: el estado real es REVIEW aunque el gate diga GO |
| **Pruebas y validación** | Ejecución de `pytest`, validadores, health check de Streamlit y verificación de que las cifras citadas coinciden con los reportes |

### 6.2 Verificaciones humanas

La **interpretación normativa**, la elección del daño prioritario, la métrica principal, la tolerancia, las condiciones de retiro y la **decisión final (REVIEW / piloto con revisión humana)** fueron revisadas y validadas por el estudiante. Las cifras se contrastaron contra los archivos de evidencia del repositorio.

### 6.3 Errores de la IA detectados y corregidos

1. **Dos `SyntaxError` en el proyecto base**, ambos del mismo patrón (texto multilínea con comillas simples). Sin corregirlos, LAB11 y LAB13 eran inválidos.
2. **Truncación accidental de la síntesis del Ej. 07.** La IA cometió con `git add .` un archivo al que le faltaban las últimas 5 líneas (firma incluida). Se detectó al revisar `git status` y se restauró byte a byte (blob `74d07a5`, idéntico al original) en un commit correctivo.
3. **Falsa alarma estadística.** Dos probabilidades bootstrap coincidían exactamente; se verificó con otras semillas y se confirmó como artefacto del generador, no como error de cálculo.
4. **Inconsistencia del dashboard.** La app mostraba "GO" sin contexto, reforzando el riesgo R02. Corregido con un aviso explícito de estado REVIEW y la métrica "Decisión (humana)".

### 6.4 Límites de la asistencia

La IA no sustituye la validación con datos reales, la revisión jurídica ni la decisión del propietario institucional. Los datos son sintéticos y **los resultados no se generalizan** a población real. Toda cifra es reproducible con los comandos del Anexo A.

---

## Anexo A — Reproducibilidad

```bash
uv sync --frozen
uv run python scripts/lab13_governance.py
uv run python scripts/simulate_incident.py
uv run python scripts/lab12_uncertainty.py
uv run pytest -q
uv run streamlit run app.py
```

`uv run pytest -q` → **10 pruebas aprobadas**. Estado esperado de la app: aviso rojo **REVIEW** con `G1 = 0.653`, caption con gate **GO**.

## Anexo B — Inventario de artefactos LAB13

| Archivo | Contenido |
|---|---|
| `docs/MODEL_CARD.md` | Model Card completa con evaluación, Green AI y límites |
| `docs/RUNBOOK.md` | Runbook de incidentes: S1–S4, evidencia, comunicación, N1–N4 |
| `student_inputs/raci.csv` | Matriz RACI de 8 actividades |
| `reports/lab13/deployment_decision.json` | Gate automático (GO) con métricas, brechas y recursos |
| `reports/lab13/fairness_by_group.csv` | Recall y FPR por grupo |
| `reports/lab13/INCIDENT_POSTMORTEM.md` | Simulacro INC-2026-10-25-01 con 7 acciones correctivas |
| `app.py` | Dashboard con aviso de estado real REVIEW |

## Anexo C — Limitaciones del expediente

1. **Datos sintéticos:** no representan personas ni territorios reales.
2. **Prueba de 160 casos** con una sola ventana temporal; brechas con intervalos amplios.
3. **Latencia medida en desarrollo**, no en el entorno institucional.
4. **Retención:** la política para datos reales está **propuesta**, no implementada; hoy solo aplica la retención de evidencia (5 años).
5. **Concentración de accountability** en un solo rol (A en 5 de 8 actividades), sin *deputy* designado.
6. **R02 y R07** diseñados pero no ejecutados; el piloto es su mecanismo de prueba.
7. **Sin técnicas de mitigación** aplicadas (reweighting, equalized odds, calibración por grupo).
8. **La Model Card no está enlazada desde el dashboard.**

---

**Firma:** Dirección de Análisis Territorial · **Fecha:** 2026-10-25 · **Estado:** REVIEW — piloto con revisión humana · **Tag:** `u04-lab13`
