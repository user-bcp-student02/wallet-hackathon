---
name: security-review
description: "Use when auditing frontend or backend security, vulnerabilities, secrets, validation, authentication, authorization, API boundaries, errors, dependencies, or deployment configuration."
---

# Security Review

## Propósito y alcance

Emitir una evaluación de seguridad trazable, basada en evidencia del código y la configuración actuales. El análisis es de solo lectura: identifica debilidades, explica el riesgo y recomienda validaciones seguras, pero no modifica código ni ejecuta pruebas activas.

Por defecto, revisar ambos proyectos y sus interacciones:

- `frontend/`: interfaz React, TypeScript, Vite y consumo de la API.
- `backend/`: API FastAPI, esquemas Pydantic, persistencia SQLAlchemy/SQLite y configuración Python.

Confirma primero la estructura y las tecnologías vigentes; no des por sentada esta descripción si el repositorio cambió. Si una capa no está en alcance o no existe, explica la limitación y no inventes controles.

## Procedimiento

1. **Establece el alcance y los activos.** Lee la solicitud o el issue, los archivos afectados y la documentación arquitectónica relevante. Identifica datos sensibles, usuarios, operaciones, límites de confianza y flujos desde la interfaz hasta la API y la persistencia.
2. **Inspecciona fuentes de verdad.** Revisa código fuente, manifiestos y archivos de configuración pertinentes. Prefiere manifiestos y lockfiles a paquetes instalados o artefactos generados. Consulta pruebas existentes como evidencia de cobertura, no como demostración automática de seguridad.
3. **Analiza frontend y backend por separado y de extremo a extremo.** Aplica las listas de control siguientes solo cuando correspondan; verifica cada sospecha en el contexto del código y su configuración.
4. **Valida la evidencia.** Localiza el flujo completo y las salvaguardas existentes. Distingue hechos de hipótesis, explica precondiciones y no infieras autenticación, despliegue, exposición o impacto sin evidencia.
5. **Prioriza los hallazgos.** Asigna severidad y confianza justificadas por explotabilidad e impacto. Consolida causas comunes sin ocultar efectos diferenciados por capa.
6. **Entrega resultados accionables.** Cita rutas relativas al workspace, símbolos y líneas. Por hallazgo, indica proyecto(s), evidencia, condiciones de explotación, impacto, activos afectados y cómo validar de forma segura. Registra brechas de cobertura y limitaciones.

## Controles de frontend

- **Entradas y renderizado:** rastrea datos de formularios, API, URL y almacenamiento del navegador; comprueba validación de formato y límites, renderizado de contenido no confiable, uso de HTML directo, construcción de URL y posibles redirecciones. Considera el escape automático del framework y confirma si se elude.
- **Autoridad de la validación:** determina si los controles de UI se tratan incorrectamente como protección. Las restricciones del cliente no sustituyen la validación, autenticación ni autorización del backend; comprueba si una llamada directa a la API puede eludirlas.
- **Secretos y datos:** verifica que variables expuestas al bundle (por ejemplo, prefijos `VITE_`), código fuente, mapas de fuentes, almacenamiento local/sesión, estado de UI, consola y mensajes de error no expongan credenciales, tokens o datos sensibles.
- **Consumo de API:** revisa destinos/orígenes, transporte, credenciales, manejo de errores, respuestas y datos mostrados. Evalúa riesgos de CORS en conjunto con la configuración del servidor; considera CSRF si se usan credenciales enviadas automáticamente, como cookies.
- **Configuración y dependencias:** distingue configuración de desarrollo de producción; verifica evidencia disponible de CSP y otros encabezados en el servidor o plataforma de despliegue, y revisa manifiestos/lockfiles para dependencias y scripts relevantes.
- **Interacción accesible y segura:** comprueba que las acciones sensibles no dependan solo de elementos deshabilitados u ocultos, y que el flujo de UI no revele datos de otros usuarios ni resultados que el servidor debería restringir.

## Controles de backend

- **Autenticación y autorización:** verifica identidad, permisos por operación y alcance por recurso/propietario en cada ruta. Antes de reportar ausencia de autenticación, establece con evidencia si el sistema o endpoint debe restringirse; que el frontend o la API no muestren una función no constituye control.
- **Validación de entradas:** inspecciona esquemas, tipos, enumeraciones, límites de longitud/tamaño/cantidad, fechas, valores numéricos y campos opcionales. Verifica que las reglas de negocio se apliquen en servidor también para llamadas directas.
- **API y exposición de datos:** revisa métodos, códigos y errores, límites de consultas/lotes, campos aceptados en escrituras, respuestas y controles de acceso a identificadores. Detecta asignación masiva, filtración de datos, enumeración y respuestas excesivas cuando haya evidencia.
- **Persistencia:** verifica consultas parametrizadas/uso seguro del ORM, transacciones, consistencia, restricciones y gestión de conexiones. Evalúa las rutas y permisos de la base de datos, especialmente si SQLite usa un archivo local.
- **Abuso y disponibilidad:** busca operaciones costosas o sin límites, lotes excesivos, falta de límites temporales o de tamaño y otras vías concretas de agotamiento de recursos. No clasifiques riesgos hipotéticos sin una ruta alcanzable e impacto sustentado.
- **Configuración y manejo de errores:** busca modo debug, CORS permisivo, secretos en configuración o logs, trazas/detalles internos en respuestas, configuración insegura por defecto y exposición de servicios. Considera CSRF cuando la autenticación use cookies y CORS solo como control del navegador, no como autorización.
- **Dependencias y pruebas:** revisa manifiestos/lockfiles y pruebas de rutas críticas (permisos, validación, errores y límites). Anota los casos no cubiertos; no declares seguridad basándote solo en que las pruebas existentes pasan.

## Controles entre frontend y backend

- Traza cada operación sensible desde su control de UI hasta ruta, esquema, lógica y almacenamiento.
- Verifica que las reglas de negocio y los permisos se validen en el backend y que los contratos API no permitan cambiar estado o consultar recursos fuera del alcance autorizado.
- Comprueba coherencia de tipos, campos requeridos/opcionales, límites y estados entre frontend y backend; un tipo TypeScript no valida la entrada recibida por el servidor.
- Revisa exposición y tratamiento de datos sensibles en solicitudes, respuestas, errores y logs en todas las capas.
- No uses CORS como sustituto de autenticación/autorización. Evalúa CSRF de acuerdo con el mecanismo real de autenticación y credenciales.

## Seguridad y límites del análisis

- No explotes sistemas, no accedas a servicios externos ni uses payloads destructivos o datos reales.
- No ejecutes cambios, mutaciones ni pruebas activas. Recomienda validaciones reproducibles en entorno aislado y con datos sintéticos; aclara cuando no sea posible ejecutarlas con las herramientas disponibles.
- No reproduzcas secretos detectados. Indica archivo, tipo de exposición y riesgo de forma redactada.
- No inventes vulnerabilidades, CVE, impacto, controles requeridos ni condiciones de despliegue.
- Separa hallazgos confirmados por evidencia de hipótesis; explica la evidencia faltante y evita duplicados.
- No apruebes por ausencia de evidencia. Si la cobertura es insuficiente, indica qué falta para concluir.

## Severidad y confianza

Asigna severidad según impacto y condiciones plausibles de explotación, usando la escala del agente solicitante. La confianza representa cuán directamente la evidencia sustenta el hallazgo, no la severidad. Justifica ambas; no uses puntuaciones sin explicar el fundamento.

## Decisión de revisión

Incluye una decisión general y justifícala:

- `approved`: la cobertura del alcance es suficiente y no hay candidatos sustentados pendientes de revisión.
- `changes_requested`: existe al menos un candidato sustentado que requiere evaluación o remediación.
- `blocked`: faltan alcance, evidencia o acceso a fuentes necesarios para concluir de forma responsable.

No uses `approved` cuando la cobertura sea insuficiente. La decisión no sustituye la clasificación humana de cada hallazgo candidato.

## Formato de cada hallazgo

```text
Título
Proyecto(s) afectado(s)
Severidad
Confianza
Evidencia
Condiciones de explotación
Impacto
Activos o contratos potencialmente afectados
Cómo validarlo de forma segura
Estado: CANDIDATO
```

Al finalizar, resume por separado la cobertura de `backend/` y `frontend/`, las áreas que no aplicaron y las limitaciones de evidencia. Detente después del análisis: una persona debe clasificar cada candidato como `CONFIRMADO`, `NECESITA MÁS EVIDENCIA` o `DESCARTADO`; solo los confirmados pueden avanzar a remediación.
