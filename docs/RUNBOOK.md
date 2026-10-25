# Incident Runbook — Territorial Review DSS (Synthetic)

**Sistema:** Territorial Review DSS — Synthetic · **Versión:** 0.1.0 · **Propietario:** Dirección de Análisis Territorial
**Vigencia:** 2026-10-25 → 2027-01-31 · **Ámbito:** piloto con revisión humana (REVIEW), sin producción.
**Regla de oro:** ante duda, **contener primero y analizar después**. Ningún indicador habilita a automatizar decisiones sobre personas.

---

## 1. Detection and classification

**Quién detecta**

| Señal | Fuente | Detector | Frecuencia |
|---|---|---|---|
| Recall global < 0.68 | `reports/lab12/*/global_metrics.json`, monitoreo de producción | Data Scientist (R) | Por lote / mensual |
| **Recall de G1 o G2 < 0.68** | `fairness_by_group.csv` | Data Scientist (R) | Mensual |
| Brecha de recall o FPR > 0.16 | `global_metrics.json` (differences) | Data Scientist (R) | Mensual |
| Deriva de distribución (PSI > 0.2 o cambio de esquema) | `validate_schema` + perfilado de datos | Data Engineer (R) | Semanal |
| FPR de G2 \| 60+ > 0.556 (baseline) | `fairness_intersectional.csv` | Data Scientist (R) | Mensual |
| Uso fuera de alcance observado | Reporte de operador o auditoría de acceso | Cualquier persona (deber de reporte) | Continuo |
| Incidente de privacidad o reidentificación | Revisión de logs / reclamo | Data Protection Officer (R) | Continuo |

**Canal de reporte:** formulario interno de incidentes de la unidad + correo al propietario institucional. **Todo reporte se acusa recibo en 4 horas hábiles.**

**Clasificación de severidad**

| Nivel | Criterio | Plazo de contención | Escalamiento |
|---|---|---|---|
| **S1 — Crítico** | Daño a personas ya ocurrido, reidentificación, decisión automatizada sobre una persona, uso fuera de alcance con efecto jurídico | **Inmediato** (≤ 2 h) | Propietario institucional + Legal + DPO en ≤ 2 h |
| **S2 — Alto** | Recall de un grupo < 0.68 sostenido 2 mediciones, brecha > 0.16, caída de recall global < 0.68 | ≤ 24 h | Propietario institucional + Data Scientist |
| **S3 — Medio** | Deriva de datos sin caída de métricas, latencia > 500 ms, tamaño > 1,024 KB | ≤ 72 h | Data Scientist + ML Engineer |
| **S4 — Bajo** | Falla cosmética, error de documentación, reclamo sin impacto | ≤ 5 días hábiles | Data Scientist |

**Detección automática:** `uv run python scripts/lab13_governance.py` produce `deployment_decision.json`. Un `status: REVIEW` con `failed` no vacío es un incidente **S2** como mínimo.

> **Advertencia de lectura del gate.** El gate automático solo evalúa el recall **global**. Un `GO` **no** cierra el caso si el recall por grupo está bajo 0.68: esa condición se verifica manualmente en `fairness_by_group.csv` y es la que hoy mantiene el sistema en REVIEW.

## 2. Containment authority

| Acción | Autoridad | Límite | Registro |
|---|---|---|---|
| Pausar la cola de priorización y volver a orden manual | **ML Engineer (R)** por indicación del Data Scientist | Inmediato, sin aprobación previa | Ticket de incidente |
| Congelar el modelo y prohibir reentrenamiento | **ML Engineer (R)** | Inmediato | Ticket + commit de respaldo |
| Suspender el servicio completo | **Institutional Owner (A)** | ≤ 2 h desde S1 | Decisión firmada |
| Retirar el sistema y activar la alternativa no predictiva | **Institutional Owner (A)**, con C de Legal | ≤ 24 h desde S1 | Decision record nuevo |
| Comunicación externa a afectados | **Institutional Owner (A)** + Legal (C) | Ver §4 | Copia en expediente |
| Restablecer el servicio | **Institutional Owner (A)** tras cierre de acciones | Ver §6 | Acta de restablecimiento |

**Principio de autoridad:** el operador puede **vetar casos individuales** en cualquier momento sin aprobación. La contención técnica (pausar, congelar) **no requiere** esperar al propietario; la **reanudación sí**.

**Nadie puede reanudar el servicio con un incidente S1 abierto.**

## 3. Evidence preservation

**Qué preservar (inmutable, antes de corregir):**

1. `reports/lab13/deployment_decision.json` y `reports/lab12/*/{global_metrics.json,fairness_by_group.csv,fairness_intersectional.csv}` del momento del incidente.
2. `reports/lab12/uncertainty.json` (versión vigente del bootstrap).
3. Modelo exacto: `models/logistic.joblib` + hash SHA-256 + `git rev-parse HEAD`.
4. `uv.lock` (versiones exactas de dependencias).
5. Extracto de logs de decisiones humanas del periodo afectado, **sin identificadores directos**.
6. Copia del formulario de reclamo o reporte que originó el incidente.

**Cómo:**

```bash
git rev-parse HEAD > reports/lab13/incident_<ID>/git_commit.txt
git status --porcelain > reports/lab13/incident_<ID>/working_tree.txt
sha256sum models/logistic.joblib > reports/lab13/incident_<ID>/model.sha256
cp -r reports/lab12 reports/lab13/incident_<ID>/lab12_snapshot
cp uv.lock reports/lab13/incident_<ID>/
```

**Reglas:** almacenar en carpeta `reports/lab13/incident_<ID>/` con permiso de solo lectura; **no** sobrescribir reportes originales; **no** incluir datos personales ni identificadores directos en la evidencia (usar `case_id`); retención mínima **5 años** o la exigida por Legal, la mayor.

**Cadena de custodia:** cada carpeta se acompaña de un archivo `custody.md` con fecha, responsable, hash y motivo del acceso.

## 4. Internal and affected-party communication

**Plazos y responsables**

| Audiencia | Plazo | Responsable | Canal | Contenido mínimo |
|---|---|---|---|---|
| Propietario institucional | ≤ 2 h (S1), ≤ 24 h (S2) | Detector | Correo + llamada | Qué se detectó, alcance, contención aplicada |
| Legal y DPO | ≤ 2 h (S1) | Institutional Owner | Correo formal | Riesgo jurídico, datos afectados, obligaciones |
| Equipo operativo | ≤ 4 h | Data Scientist | Briefing | Qué no hacer, cómo registrar decisiones |
| **Personas afectadas** | **≤ 5 días hábiles** desde la confirmación | Institutional Owner + Legal | Comunicación oficial en lenguaje claro | Qué pasó, qué se hizo, qué puede hacer (apelación), a quién contactar |
| Autoridad competente | Según plazo legal aplicable | Legal | Oficial | Según normativa vigente |

**Reglas de mensaje:** lenguaje claro, sin jerga técnica; **no** minimizar ni especular sobre causas antes del análisis; indicar siempre la vía de apelación (10 días hábiles, revisor distinto); no incluir datos de terceros.

**Prohibido:** comunicar que el sistema "es justo" o "está aprobado" mientras exista un gate de equidad incumplido.

## 5. Rollback or safe baseline

**Niveles de rollback (del menos al más invasivo)**

| Nivel | Acción | Tiempo objetivo | Autoridad |
|---|---|---|---|
| **N1 — Pausa** | Congelar la cola priorizada; operar con orden manual por fecha de recepción | ≤ 15 min | ML Engineer |
| **N2 — Versión anterior** | Restaurar el último modelo con gates aprobados (tag de git + `models/*.joblib` verificado por hash) | ≤ 2 h | ML Engineer + Data Scientist |
| **N3 — Línea base no predictiva** | **Muestreo aleatorio estratificado por distrito** con lista de verificación de infraestructura y exposición y prioridad por incidentes previos | ≤ 24 h | Institutional Owner |
| **N4 — Retiro** | Desactivar el servicio y ejecutar la condición de retiro del model card | ≤ 24 h | Institutional Owner + Legal |

**Procedimiento N2 (comandos):**

```bash
git tag rollback-$(date +%Y%m%d-%H%M)
git checkout <tag_ultima_version_aprobada>
uv sync --frozen
uv run pytest -q                      # debe estar 10/10 en verde
uv run python scripts/lab13_governance.py   # verificar gates
```

**Procedimiento N3 (línea base segura):** sustituir el puntaje por la regla no predictiva descrita en `student_inputs/lab11_impact.yml`; el operador registra la decisión caso por caso; **no** se usa ningún modelo mientras dure.

**Criterio de elección:** N1 si el incidente es de proceso; N2 si hay una versión previa con gates aprobados; **N3 por defecto ante cualquier S1**, porque no requiere puntuar personas; N4 si se cumple una condición de retiro.

**Verificación post-rollback:** `pytest` 10/10, `deployment_decision.json` regenerado, `fairness_by_group.csv` revisado **por grupo** (no solo el agregado), y confirmación escrita del propietario.

## 6. Postmortem, owner and due date

**Obligatorio para S1 y S2.** Plazo: **5 días hábiles** desde la contención.

**Estructura del postmortem** (`reports/lab13/INCIDENT_<ID>_POSTMORTEM.md`):

1. Cronología con marcas de tiempo (detección → contención → comunicación → rollback → cierre).
2. Impacto cuantificado: casos afectados, grupos, duración, decisiones revisadas.
3. Causa raíz (técnica, de proceso y de gobernanza; usar los "5 porqués").
4. Qué funcionó y qué falló en los controles existentes (referencia a R01–R08 del registro de riesgos).
5. Acciones correctivas con **responsable, fecha y criterio de cierre verificable**.
6. ¿Se cumple una condición de retiro? Sí/No y decisión.
7. Actualización de `risk_register.csv`, `MODEL_CARD.md` y este runbook.

**Cultura:** postmortem **sin culpa** (*blameless*). Se analizan sistemas y decisiones, no personas. Ocultar un incidente es una falta grave.

**Seguimiento:** las acciones se registran en `reports/lab13/actions.csv` y se revisan en la reunión mensual de gobernanza. Una acción vencida sin cierre **bloquea la reanudación** del servicio.

| Rol | Responsabilidad en el postmortem |
|---|---|
| **Institutional Owner (A)** | Aprueba el informe y las acciones; decide reanudación o retiro |
| **Data Scientist (R)** | Redacta el análisis técnico y la causa raíz |
| **ML Engineer (R)** | Aporta evidencia de contención, rollback y versiones |
| **Legal (C)** | Valida obligaciones de comunicación y retención |
| **DPO (C)** | Valida impacto en privacidad y necesidad de notificación |
| **Affected representatives (I)** | Reciben el resumen en lenguaje claro y el resultado de su apelación |

---

**Ejecución de referencia:** `reports/lab13/INCIDENT_POSTMORTEM.md` (simulacro del 2026-10-25, señal "recall gap exceeded", contención REVIEW + línea base segura).
