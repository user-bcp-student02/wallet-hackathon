# Diseño técnico implementado: conciliación operativa

## 1) Arquitectura actual

La solución está implementada en dos capas:

- **Backend API** en [backend/app/main.py](../../../backend/app/main.py)
  con FastAPI, SQLAlchemy y SQLite.
- **Frontend web** en [frontend/src/App.tsx](../../../frontend/src/App.tsx)
  con React + TypeScript.

La UI consume directamente los endpoints REST del backend (vía proxy de Vite en desarrollo).

## 2) Componentes backend

### 2.1 API HTTP

Definida en [backend/app/main.py](../../../backend/app/main.py):

- `GET /health`
- `POST /api/v1/records/{source}`
- `POST /api/v1/reconciliations`
- `GET /api/v1/reconciliations`
- `GET /api/v1/reconciliations/daily-summary`
- `GET /api/v1/reconciliations/{run_id}`
- `PATCH /api/v1/discrepancies/{discrepancy_id}`

### 2.2 Contratos y validación

Definidos en [backend/app/schemas.py](../../../backend/app/schemas.py) con Pydantic:

- Lotes de 1 a 1000 registros.
- `amount_minor > 0`.
- `currency` en formato `^[A-Z]{3}$`.
- `status` obligatorio para `provider`, prohibido para `wallet`/`ledger`.
- Para `RESOLVED`, `investigation_note` es obligatoria.

### 2.3 Modelo de persistencia

Definido en [backend/app/models.py](../../../backend/app/models.py):

- `source_records`
- `reconciliation_runs`
- `discrepancies`

Restricciones relevantes:

- unicidad de corrida por `reconciliation_date + channel`;
- unicidad de descalce por `run_id + transaction_reference + discrepancy_type`.

### 2.4 Motor de conciliación

Implementado en [backend/app/reconciliation.py](../../../backend/app/reconciliation.py):

1. filtra registros por fecha;
2. agrupa por `transaction_reference`;
3. selecciona solo referencias vinculadas al `channel` de la corrida;
4. evalúa reglas de faltantes/duplicados/mismatch y estado del proveedor;
5. incrementa `reconciled_count` cuando no hay hallazgos;
6. persiste descalces con estado inicial `OPEN`.

## 3) Reglas implementadas actualmente

Tipos de descalce:

- `MISSING_WALLET_RECORD`
- `MISSING_PROVIDER_RESULT`
- `MISSING_LEDGER_ENTRY`
- `DUPLICATE_WALLET_RECORD`
- `DUPLICATE_PROVIDER_RESULT`
- `DUPLICATE_LEDGER_ENTRY`
- `CHANNEL_MISMATCH`
- `AMOUNT_MISMATCH`
- `CURRENCY_MISMATCH`
- `PROVIDER_NOT_SUCCESSFUL`

Notas de comportamiento:

- Si el proveedor viene con `FAILED` o `PENDING`, se marca `PROVIDER_NOT_SUCCESSFUL`.
- No existe estado transaccional `PENDING` en resumen; se usa:
  - `reconciled_count`
  - `unreconciled_count`
  - `resolved_count`
- `resolved_count` cuenta referencias cuyos descalces están todos en `RESOLVED`.

## 4) Flujo funcional actual

1. Operaciones carga lotes por fuente.
2. Operaciones ejecuta corrida para fecha/canal.
3. Backend crea corrida y descalces detectados.
4. UI consulta reportes y resumen diario.
5. Operaciones actualiza descalces (`IN_PROGRESS` o `RESOLVED` con nota).

## 5) Estados de investigación

Estados soportados:

- `OPEN`
- `IN_PROGRESS`
- `RESOLVED`

Reglas:

- se puede pasar de `OPEN` a `IN_PROGRESS` o `RESOLVED`;
- se puede actualizar nota en transiciones válidas;
- no se puede reabrir un descalce ya `RESOLVED` (retorna `409`).

## 6) Diseño frontend

La pantalla principal en [frontend/src/App.tsx](../../../frontend/src/App.tsx):

- carga reportes y resumen diario en paralelo;
- muestra salud de API;
- ejecuta corrida con formulario de canal;
- permite carga JSON por fuente;
- renderiza descalces por corrida con acciones de investigación.

Cliente HTTP en [frontend/src/api.ts](../../../frontend/src/api.ts):

- tipado de respuestas;
- manejo de errores con `ApiError`;
- operaciones CRUD del flujo operativo.

## 7) Datos demo y entorno

El seed está en [backend/app/demo_data.py](../../../backend/app/demo_data.py):

- carga dataset demo sólo si BD está vacía;
- crea corridas demo para `qr` y `p2p`;
- se desactiva en producción o con `SEED_DEMO_DATA=false`.

## 8) Cobertura de pruebas

Pruebas en:

- [backend/tests/test_reconciliation_api.py](../../../backend/tests/test_reconciliation_api.py)
- [backend/tests/test_demo_data.py](../../../backend/tests/test_demo_data.py)

Validan:

- conciliación exitosa;
- descalces por tipo;
- resolución de descalces y efecto en resumen;
- filtros por fecha/canal y resumen diario;
- validaciones de API y unicidad de corrida;
- disponibilidad de OpenAPI/docs.

## 9) Limitaciones técnicas vigentes

- Sin autenticación/autorización.
- Sin historial de eventos de investigación por actor (solo estado actual y nota).
- Sin SLA temporal para diferenciar pendiente vs ausente definitivo.
- Sin integración nativa con sistemas externos reales.
