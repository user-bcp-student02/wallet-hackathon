# Plan de trabajo actualizado: conciliación operativa

Este plan refleja el estado real del MVP ya implementado y el backlog sugerido.

## 1) Entregables completados (estado actual)

### Dominio y persistencia

- [x] **DOM-01** Modelado de registros fuente, corridas y descalces en SQLite.
- [x] **DOM-02** Catálogo de tipos de descalce e investigación (`OPEN`, `IN_PROGRESS`, `RESOLVED`).
- [x] **DOM-03** Restricción de unicidad por corrida (`fecha + canal`).
- [x] **DOM-04** Restricción de unicidad de descalce por corrida/referencia/tipo.

### Reglas de conciliación

- [x] **RULE-01** Detección de faltantes por fuente.
- [x] **RULE-02** Detección de duplicados por fuente.
- [x] **RULE-03** Detección de mismatch de canal, monto y moneda.
- [x] **RULE-04** Detección de estado de proveedor no exitoso.
- [x] **RULE-05** Cálculo de resumen (`transaction_count`, `reconciled_count`, `unreconciled_count`, `resolved_count`).

### API

- [x] **API-01** Endpoint de salud (`GET /health`).
- [x] **API-02** Endpoints de carga por fuente (`POST /api/v1/records/{source}`).
- [x] **API-03** Endpoint para ejecutar corridas (`POST /api/v1/reconciliations`).
- [x] **API-04** Endpoint para listar corridas por fecha/canal (`GET /api/v1/reconciliations`).
- [x] **API-05** Endpoint de resumen diario agregado (`GET /api/v1/reconciliations/daily-summary`).
- [x] **API-06** Endpoint de detalle por corrida (`GET /api/v1/reconciliations/{run_id}`).
- [x] **API-07** Endpoint de actualización de descalce (`PATCH /api/v1/discrepancies/{discrepancy_id}`).
- [x] **API-08** OpenAPI documentado y UI de docs (`/openapi.json`, `/docs`, `/redoc`).

### Frontend

- [x] **UI-01** Dashboard con métricas operativas.
- [x] **UI-02** Filtros por fecha y canal.
- [x] **UI-03** Ejecución de corrida desde UI.
- [x] **UI-04** Visualización de descalces por corrida.
- [x] **UI-05** Flujo de investigación y resolución con nota.
- [x] **UI-06** Carga de lotes JSON por fuente.

### Calidad

- [x] **QA-01** Tests de API para conciliación, filtros, errores y OpenAPI.
- [x] **QA-02** Tests de seed demo e idempotencia de carga inicial.

## 2) Backlog recomendado (siguiente iteración)

### Reglas de negocio

- [ ] **NEXT-RULE-01** Incorporar SLA temporal para distinguir pendiente vs ausencia definitiva.
- [ ] **NEXT-RULE-02** Definir explícitamente semántica final para `provider=PENDING`.
- [ ] **NEXT-RULE-03** Versionar reglas de conciliación para trazabilidad de cambios.

### Investigación y auditoría

- [ ] **NEXT-OPS-01** Registrar historial de cambios de estado con actor y timestamp.
- [ ] **NEXT-OPS-02** Evaluar habilitar reapertura controlada de descalces resueltos.

### Seguridad y acceso

- [ ] **NEXT-SEC-01** Agregar autenticación.
- [ ] **NEXT-SEC-02** Agregar autorización por roles (consulta vs gestión).

### Integración y escalabilidad

- [ ] **NEXT-INT-01** Implementar adaptadores de ingesta desde fuentes reales.
- [ ] **NEXT-INT-02** Soportar paginación y filtros adicionales para alto volumen.
- [ ] **NEXT-INT-03** Definir estrategia de reejecución idempotente más flexible que “una corrida por fecha/canal”.

### Observabilidad

- [ ] **NEXT-OBS-01** Métricas técnicas (latencia por endpoint, errores por tipo).
- [ ] **NEXT-OBS-02** Logging estructurado con correlación por corrida.

## 3) Criterio de “listo para producción”

Se considera listo para producción cuando, como mínimo:

1. exista seguridad de acceso;
2. reglas de SLA estén formalizadas;
3. exista auditoría de investigación con actor;
4. se valide desempeño con volumen esperado real;
5. se complete integración con fuentes no mock.
