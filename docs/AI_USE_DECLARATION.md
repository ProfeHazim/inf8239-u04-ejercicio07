# Declaración de uso de IA

**Ejercicio 07 · Unidad 04 · Gobernanza y DSS responsable · INF-8239**
Documento complementario de `EJERCICIO_07_SINTESIS.md` (sección 5). Cierra el campo pendiente de esta plantilla.

## Declaración de uso responsable de IA

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
| Redacción de `EJERCICIO_07_SINTESIS.md` | Borrador completo |

**Verificaciones humanas.** La interpretación normativa, la elección del daño prioritario, la métrica principal, la tolerancia y la **decisión final (piloto con revisión humana, sin producción)** fueron revisadas y validadas por el estudiante. Las cifras del documento se contrastaron contra los archivos de evidencia del repositorio.

**Errores detectados y corregidos.**

1. **Bug real del proyecto base:** `scripts/lab11_impact.py` no compilaba (`SyntaxError: unterminated string literal`) porque el `write_text` del decision record usaba comillas dobles para un texto de tres líneas. Se corrigió con un string triple. Sin esta corrección, la validación de LAB11 era imposible.
2. **Riesgo de sobrescritura:** el mismo script regenera `reports/lab11/DECISION_RECORD.md` con un placeholder en cada ejecución. Se documentó el orden correcto (script primero, decisión después) para evitar perder el registro firmado.
3. **Falsa alarma verificada:** la coincidencia exacta de dos probabilidades bootstrap se contrastó con otras semillas y se confirmó como artefacto del generador, no como error de cálculo.

**Límites de la asistencia.** La IA no sustituye la validación con datos reales ni la revisión jurídica. Los datos son sintéticos y los resultados **no se generalizan** a población real. Toda cifra de este expediente es reproducible con los comandos del Anexo A de `EJERCICIO_07_SINTESIS.md`.
