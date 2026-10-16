# Wallet reconciliation API

FastAPI + SQLite implementation of the MVP's daily operational reconciliation story.
SQLite stores normalized wallet transactions, provider results, ledger records, runs,
and discrepancy investigation status. The initial input contract is a JSON batch API;
provider and ledger integrations can map their source formats to this canonical shape.

## Levantar el backend en local

Desde la raíz del repositorio, abre una terminal para el backend:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Uvicorn queda escuchando por defecto en `http://127.0.0.1:8000`. La base SQLite se
crea en `backend/wallet.db` si no existe; se puede cambiar mediante `DATABASE_URL`.
En desarrollo, una base vacía recibe automáticamente registros de ejemplo para la
fecha actual, con corridas QR y P2P y varios tipos de descalce. Si la base ya contiene
registros o corridas, no se agregan datos de demostración.
La documentación interactiva está en [Swagger UI](http://127.0.0.1:8000/docs) y
[ReDoc](http://127.0.0.1:8000/redoc); el contrato OpenAPI JSON está en
`http://127.0.0.1:8000/openapi.json`.

Para desactivar los datos de ejemplo durante el desarrollo, antes de iniciar Uvicorn:

```powershell
$env:SEED_DEMO_DATA = "false"
uvicorn app.main:app --reload
```

El seed queda desactivado automáticamente con `APP_ENV=production`; los datos de
demostración no se deben utilizar como registros financieros reales.

Para los siguientes inicios, con el entorno virtual activo, basta con:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Funcionalidad de la API

- `POST /api/v1/records/wallet`, `/provider`, `/ledger`: guarda lotes de hasta 1,000
  registros normalizados. Los montos son enteros en unidades menores; para PEN, céntimos.
- `POST /api/v1/reconciliations`: crea una corrida diaria para una fecha y un canal.
- `GET /api/v1/reconciliations?reconciliation_date=AAAA-MM-DD&channel=qr`: consulta
  reportes filtrados por fecha y, opcionalmente, canal.
- `GET /api/v1/reconciliations/daily-summary?reconciliation_date=AAAA-MM-DD`: agrega
  los totales y canales de todas las corridas del día.
- `GET /api/v1/reconciliations/{run_id}`: consulta el resumen y detalle de descalces.
- `PATCH /api/v1/discrepancies/{id}`: actualiza el estado de investigación y su nota.

The reconciliation compares records by transaction reference and expects at most one
normalized record per source/reference/date. Duplicate source rows, missing records,
channel/amount/currency mismatches, and non-successful provider outcomes are reported.
Esta versión crea una sola corrida por fecha y canal; los flujos de repetición y
corrección, límites específicos de proveedores, autenticación y reglas de normalización
del ledger deben definirse antes del uso en producción.

Los resúmenes cuentan referencias de transacción distintas: conciliadas (sin descalces),
pendientes (con al menos un descalce no resuelto) y resueltas (con descalces y todos
resueltos). Estas categorías son mutuamente excluyentes.

## Tests

```powershell
python -m pytest
```
