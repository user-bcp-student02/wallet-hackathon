# Propuesta aterrizada: conciliación operativa de transacciones

## Problema de negocio

Operaciones necesita detectar diariamente diferencias entre:

1. intenciones registradas por wallet;
2. resultados reportados por proveedor;
3. asientos del ledger.

Sin una vista unificada por referencia transaccional, es difícil priorizar
descalces y cerrar investigación con trazabilidad.

## Objetivo del MVP entregado

Entregar una solución operativa mínima que permita:

- cargar registros normalizados por fuente;
- ejecutar conciliación por fecha y canal;
- visualizar descalces con detalle;
- gestionar su estado de investigación;
- consultar resumen diario agregado.

## Alcance implementado

### Backend (FastAPI + SQLite)

- API para cargar lotes JSON en:
  - `POST /api/v1/records/wallet`
  - `POST /api/v1/records/provider`
  - `POST /api/v1/records/ledger`
- API para ejecutar corrida:
  - `POST /api/v1/reconciliations`
- API para consulta:
  - `GET /api/v1/reconciliations`
  - `GET /api/v1/reconciliations/{run_id}`
  - `GET /api/v1/reconciliations/daily-summary`
- API para investigación:
  - `PATCH /api/v1/discrepancies/{id}`
- Persistencia de:
  - registros fuente (`source_records`);
  - corridas (`reconciliation_runs`);
  - descalces (`discrepancies`).

### Frontend (React + TypeScript)

- Filtro por fecha y canal.
- Ejecución de corridas.
- Visualización de métricas:
  - transacciones revisadas;
  - conciliadas;
  - por investigar;
  - resueltas.
- Tabla de descalces con acciones:
  - pasar a `IN_PROGRESS`;
  - resolver con nota (`RESOLVED`).
- Panel para cargar lotes JSON por fuente.

## Valor entregado

- Permite operación end-to-end local sin dependencias externas.
- Reduce trabajo manual de cruce entre fuentes.
- Da trazabilidad por referencia transaccional y tipo de descalce.
- Habilita seguimiento de investigación y cierre operativo.

## Limitaciones conocidas del MVP

- No existe SLA temporal para clasificar “pendiente” por ventana de espera.
- `PENDING` del proveedor hoy se modela como descalce (`PROVIDER_NOT_SUCCESSFUL`).
- No se permite reabrir descalces ya resueltos.
- No hay autenticación/autorización por perfiles.
- Solo una corrida por combinación `fecha + canal`.
- No integra orígenes reales; recibe datos ya normalizados.

## Criterios de éxito verificados en esta versión

1. Se puede ejecutar conciliación y obtener resumen por corrida.
2. Se detectan descalces por faltantes, duplicados y diferencias de datos.
3. El resumen diario agrega múltiples corridas de la misma fecha.
4. Se puede resolver un descalce con nota y ver impacto en métricas.
5. OpenAPI y documentación interactiva están disponibles (`/openapi.json`, `/docs`, `/redoc`).

## Siguiente alcance recomendado (post-MVP)

1. Definir SLA y estado “pendiente” temporal explícito.
2. Incorporar control de acceso y auditoría de actor.
3. Permitir reejecución idempotente versionada (más allá de bloqueo por unicidad).
4. Integrar adaptadores desde fuentes reales (wallet/provider/ledger).
5. Añadir paginación y filtros avanzados para volumen alto.
