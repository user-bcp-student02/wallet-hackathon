# Hallazgos de Discovery — conciliación

**Alcance:** flujo de conciliación de extremo a extremo: historia, backend,
contrato API y frontend.

**Estado del análisis:** Discovery en revisión humana. Los hallazgos confirmados
no autorizan por sí solos cambios de implementación; deben convertirse en
requisitos y aprobarse antes de crear tareas.
No se ejecutaron pruebas, build ni la aplicación; la evidencia se obtuvo por
inspección estática de código, configuración y pruebas existentes.

**Fuentes:** [historia de conciliación](./hu-operations-transaction-reconciliation.sp.md),
[épica del MVP](./epic-peru-wallet-mvp.sp.md), `backend/app/`,
`backend/tests/`, `frontend/src/`, `frontend/package.json` y README de backend y
frontend. El SDD se consultó solo como contexto, no como requisito aprobado.
No se encontraron `HALLAZGOS.md` previos, `docs/ENDPOINTS.md` ni
`docs/TESTING.md`; no se consultó GitHub ni Project ReqFlow.

## Matriz de criterios de aceptación

| Criterio | Cobertura observada | Evidencia |
|---|---|---|
| CA-01 — Comparar wallet, proveedor y ledger | **Cubierto en el MVP con registros normalizados; no se demuestra integración con fuentes reales.** | `backend/app/reconciliation.py::build_reconciliation`, `POST /api/v1/records/{source}` y `POST /api/v1/reconciliations` en `backend/app/main.py`; el frontend carga lotes JSON y ejecuta conciliaciones en `frontend/src/App.tsx`. Pruebas de comparación en `backend/tests/test_reconciliation_api.py`. |
| CA-02 — Identificar cada descalce con referencia, tipo y estado | **Cubierto en backend, API y UI.** | Modelo `Discrepancy`, `DiscrepancyResponse`, detalle y actualización del estado; `ReportCard` muestra referencia, tipo, detalle y estado. Pruebas de detección y resolución en `backend/tests/test_reconciliation_api.py`. |
| CA-03 — Filtrar por fecha y canal | **Cubierto en backend y consumido por la UI; sin prueba frontend observada.** | `GET /api/v1/reconciliations` acepta fecha y canal; `App.tsx::refresh` consulta reportes y resumen al cambiar filtros. `test_filters_reports_and_aggregates_daily_summary_across_channels`. |
| CA-04 — Resumen diario de conciliados, no conciliados y resueltos | **Cubierto en API y UI con unidades separadas.** | `resolved_count` cuenta transacciones resueltas y `resolved_discrepancy_count` cuenta incidencias resueltas; la UI presenta ambas métricas. Ver `backend/app/reconciliation.py::summarize`, `backend/app/schemas.py::ReconciliationSummary`, `frontend/src/App.tsx` y `test_summary_separates_resolved_transactions_and_discrepancies`. |

## Hallazgos candidatos

### H-01 — No se puede repetir una corrida para la misma fecha y canal

- **Estado:** DESCARTADO
- **Cobertura:** COMPORTAMIENTO ACTUAL ACORDADO
- **Evidencia:** `backend/app/models.py::ReconciliationRun` impone unicidad por fecha y canal. `backend/app/main.py::create_reconciliation` devuelve `409` si la corrida ya existe. La carga de registros agrega datos; no reemplaza ni deduplica lotes. `backend/tests/test_reconciliation_api.py::test_rejects_missing_provider_status_and_duplicate_daily_run` verifica el rechazo repetido.
- **Impacto:** el proceso aprobado permite ejecutar fechas históricas que todavía no tengan corrida, pero no repetir fecha+canal una vez creada la corrida. No se considera brecha frente al criterio actual.
- **Prioridad propuesta:** No aplica tras la decisión operativa.
- **Contrato potencialmente afectado:** CA-01 y CA-04; `POST /api/v1/reconciliations`.
- **Cómo validarlo:** el test existente comprueba que una segunda corrida idéntica devuelve `409`; queda como regresión del comportamiento acordado.
- **Decisión de Operaciones:** se permite conciliar días anteriores cerrados si todavía no existe una corrida para esa fecha y canal. Una corrida existente no se repite.

### H-02 — `PENDING` se registra como descalce inmediatamente

- **Estado:** DESCARTADO
- **Cobertura:** COMPORTAMIENTO ACTUAL ACORDADO
- **Evidencia:** `backend/app/reconciliation.py::build_reconciliation` clasifica cualquier estado de proveedor distinto de `SUCCESS` como `PROVIDER_NOT_SUCCESSFUL`. `backend/tests/test_reconciliation_api.py::test_reports_all_discrepancy_types_with_reference_and_open_status` espera un descalce para `PENDING`. La historia menciona estados asíncronos, pero no fija la regla de clasificación ni un SLA.
- **Impacto:** la decisión de Producto/Operaciones es crear el descalce inmediatamente, por lo que el comportamiento observado no constituye una brecha de requisito.
- **Prioridad propuesta:** No aplica tras la decisión operativa.
- **Contrato potencialmente afectado:** CA-01 y CA-04; estado del proveedor y resumen.
- **Cómo validarlo:** el test existente espera `PROVIDER_NOT_SUCCESSFUL` cuando recibe `PENDING`; conservar esta verificación como comportamiento acordado.
- **Decisión de Producto/Operaciones:** `PENDING` genera incidencia inmediatamente. No se ha definido un SLA temporal.

### H-03 — El esquema OpenAPI no expresa la obligatoriedad condicional de `status`

- **Estado:** DESCARTADO
- **Cobertura:** PARCIAL
- **Evidencia:** `backend/app/schemas.py::SourceRecordInput.status` es opcional en el modelo compartido. Se generó el OpenAPI desde `create_app().openapi()`: `SourceRecordInput.required` incluye referencia, fecha, canal, importe y moneda, pero no `status`; la propiedad declara nullable y su descripción indica la obligatoriedad condicional. `backend/app/main.py::load_source_records` impone en ejecución que proveedor tenga estado y que wallet/ledger no lo envíen. `backend/tests/test_reconciliation_api.py::test_rejects_missing_provider_status_and_duplicate_daily_run` verifica proveedor sin estado.
- **Impacto:** un consumidor que genere validaciones solo desde el esquema puede interpretar `status` como opcional para todas las fuentes; el endpoint documenta y aplica una validación adicional.
- **Prioridad propuesta:** Baja; la regla está descrita en prosa y validada en ejecución.
- **Contrato potencialmente afectado:** esquema OpenAPI de `POST /api/v1/records/{source}`.
- **Validación realizada:** inspección del esquema OpenAPI generado confirma que `status` no está en `required`; el endpoint documenta la condición en prosa y el código la valida en ejecución. No se probó un consumidor real generado desde OpenAPI.
- **Decisión humana:** descartado como hallazgo que requiera seguimiento.

### H-04 — La UI puede conservar datos de filtros anteriores

- **Estado:** DESCARTADO
- **Cobertura:** PARCIAL
- **Evidencia:** `frontend/src/App.tsx::refresh` reemplaza `reports` y `daily` después de que ambas solicitudes finalizan correctamente. Si falla, guarda el error pero no limpia esos datos; tampoco se observa protección contra respuestas obsoletas cuando consultas de filtros distintos terminan fuera de orden.
- **Impacto:** podrían mostrarse métricas/reportes anteriores junto a una fecha o canal nuevos, especialmente ante error o concurrencia de consultas.
- **Prioridad propuesta:** Media.
- **Contrato potencialmente afectado:** CA-03 y correspondencia entre filtros activos y reporte presentado.
- **Cómo validarlo:** simular una consulta lenta seguida de otra rápida al cambiar filtros; repetir haciendo fallar la consulta nueva y verificar los datos visibles.
- **Decisión humana:** descartado como hallazgo que requiera seguimiento.

### H-05 — Errores de validación pueden mostrarse sin detalle en la UI

- **Estado:** DESCARTADO
- **Cobertura:** PARCIAL
- **Evidencia:** `frontend/src/api.ts::request` usa `detail` solo cuando es texto. Una reproducción aislada con FastAPI/Pydantic devolvió `422` con `detail` de tipo lista y un error de campo requerido. Según la condición de `request`, ese formato no reemplaza el mensaje genérico por estado HTTP. `frontend/src/App.tsx::uploadRecords` presenta el error resultante como alerta. La reproducción aislada no invocó el endpoint real ni el componente React.
- **Impacto:** al cargar un lote inválido, el operador podría no ver qué campo o registro debe corregir.
- **Prioridad propuesta:** Media.
- **Contrato potencialmente afectado:** errores `422` de `POST /api/v1/records/{source}` y flujo CA-01.
- **Validación realizada:** confirmada la forma de lista en una app FastAPI mínima y el descarte de listas en el parser por inspección estática. Falta reproducirlo a través de la UI y confirmar el mensaje observado.
- **Decisión humana:** descartado como hallazgo que requiera seguimiento.

### H-06 — El resumen no presenta ambos conteos de resolución acordados

- **Estado:** CONFIRMADO
- **Cobertura:** IMPLEMENTADO Y VALIDADO
- **Evidencia inicial:** `backend/app/reconciliation.py::summarize` contaba referencias cuyas incidencias están todas resueltas; `backend/app/schemas.py::ReconciliationSummary` describía `resolved_count` como transacciones. La tarjeta en `frontend/src/App.tsx` podía interpretarse como conteo de incidencias.
- **Resolución:** se conserva `resolved_count` para transacciones resueltas y se añade `resolved_discrepancy_count` para incidencias resueltas. El backend, el contrato API y la UI muestran ambas unidades por separado. Los tests de `backend/tests/test_reconciliation_api.py` verifican el resumen agregado y los conteos; `npm run build` valida el contrato TypeScript/UI.
- **Prioridad propuesta:** Media; la diferencia entre el requisito confirmado y la presentación/contrato actual afecta la interpretación del resumen.
- **Contrato afectado y actualizado:** CA-04 y `GET /api/v1/reconciliations/daily-summary`.
- **Validación:** crear una referencia con varios tipos de descalce, resolverlos y comprobar que el resumen distingue transacciones resueltas e incidencias resueltas, sin mezclar sus unidades; cubierto por tests backend y build frontend.
- **Decisión de Producto/Operaciones:** presentar conteos separados de transacciones e incidencias.

### H-07 — La fecha inicial puede no corresponder al día operativo de Perú

- **Estado:** DESCARTADO
- **Cobertura:** PARCIAL
- **Evidencia:** `frontend/src/App.tsx` inicializa `today` mediante `new Date().toISOString().slice(0, 10)`, que obtiene la fecha UTC. Una reproducción de JavaScript con `TZ=America/Lima` confirmó que `2026-10-16T19:00:00-05:00` produce fecha UTC `2026-10-17`, mientras la fecha local sigue siendo `2026-10-16`. Esa fecha se usa inicialmente para consultar y cargar datos operativos.
- **Impacto:** en `America/Lima` (UTC−5), desde las 19:00 locales la fecha UTC puede ser el día siguiente, lo que podría llevar a consultar o cargar con una fecha distinta a la esperada.
- **Prioridad propuesta:** Baja/media; depende de zona horaria y horario de uso.
- **Contrato potencialmente afectado:** CA-01 y CA-03; interpretación de fecha operativa.
- **Validación realizada:** confirmado el cambio de fecha UTC frente a la fecha local en la reproducción de JavaScript. Falta confirmar con Producto/Operaciones que la fecha operativa esperada de la UI sea `America/Lima`.
- **Decisión humana:** descartado como hallazgo que requiera seguimiento.

## Estado de seguimiento

H-01, H-02, H-03, H-04, H-05 y H-07 se descartaron como hallazgos que requieran
seguimiento. H-06 fue confirmado, implementado y validado en API y UI.
