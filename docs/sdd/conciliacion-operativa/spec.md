# Especificación funcional actual (alineada a implementación)

## 1) Glosario operativo

- **Corrida**: ejecución de conciliación para una `reconciliation_date` y un `channel`.
- **Referencia transaccional**: clave usada para agrupar registros entre fuentes.
- **Descalce**: hallazgo de inconsistencia o ausencia detectada por reglas.
- **Estado de investigación**: ciclo operativo de un descalce (`OPEN`, `IN_PROGRESS`, `RESOLVED`).

## 2) Requisitos funcionales implementados

### RF-01 Carga de registros fuente

El sistema permite cargar registros normalizados por fuente (`wallet`, `provider`, `ledger`)
mediante `POST /api/v1/records/{source}`.

### RF-02 Reglas de validación de carga

- El lote debe tener entre 1 y 1000 registros.
- `provider` requiere `status`.
- `wallet` y `ledger` no admiten `status`.
- `amount_minor` debe ser entero positivo.
- `currency` debe tener 3 letras mayúsculas.

### RF-03 Ejecución de conciliación

El sistema ejecuta una corrida con `POST /api/v1/reconciliations` para una fecha y canal.
No se permite crear más de una corrida para la misma combinación `fecha + canal`.

### RF-04 Detección de tipos de descalce

La corrida detecta:

- faltantes por fuente;
- duplicados por fuente;
- diferencia de canal;
- diferencia de monto;
- diferencia de moneda;
- resultado de proveedor no exitoso (`FAILED` o `PENDING`).

### RF-05 Resumen por corrida

Cada corrida devuelve:

- `transaction_count`
- `reconciled_count`
- `unreconciled_count`
- `resolved_count`

### RF-06 Consulta de reportes

`GET /api/v1/reconciliations` devuelve corridas de una fecha, opcionalmente filtradas por canal,
incluyendo descalces y resumen de cada corrida.

### RF-07 Resumen diario agregado

`GET /api/v1/reconciliations/daily-summary` agrega resultados de todas las corridas del día e
incluye la lista de canales procesados.

### RF-08 Consulta de corrida individual

`GET /api/v1/reconciliations/{run_id}` devuelve una corrida específica o `404` si no existe.

### RF-09 Gestión de investigación de descalces

`PATCH /api/v1/discrepancies/{discrepancy_id}` permite:

- pasar a `IN_PROGRESS`;
- resolver (`RESOLVED`) con nota obligatoria;
- actualizar nota cuando corresponda.

### RF-10 Restricción de reapertura

Si un descalce ya está en `RESOLVED`, no puede volver a `OPEN`/`IN_PROGRESS` (`409`).

## 3) Requisitos no funcionales implementados

- **NFR-01 Trazabilidad mínima**: cada descalce conserva referencia, tipo, detalle, timestamps y nota.
- **NFR-02 Documentación API**: OpenAPI disponible en `/openapi.json` y UI en `/docs` y `/redoc`.
- **NFR-03 Determinismo básico**: reglas de conciliación codificadas y reproducibles sobre los mismos datos.
- **NFR-04 Persistencia local**: SQLite con creación automática de tablas.

## 4) Comportamientos validados por pruebas

Los tests en [backend/tests/test_reconciliation_api.py](../../../backend/tests/test_reconciliation_api.py)
y [backend/tests/test_demo_data.py](../../../backend/tests/test_demo_data.py) cubren:

1. conciliación correcta cuando las tres fuentes coinciden;
2. detección de faltantes y resolución de descalces;
3. detección de duplicados y diferencias de monto;
4. cobertura del catálogo de tipos de descalce;
5. filtros por fecha/canal y resumen diario agregado;
6. errores esperados (`422`, `404`, `409`);
7. exposición del contrato OpenAPI.

## 5) Diferencias entre diseño ideal y estado actual

- No existe aún un estado de conciliación “pendiente por SLA temporal”.
- `provider=PENDING` se considera descalce inmediato (`PROVIDER_NOT_SUCCESSFUL`).
- No hay auditoría de actor por cambio de estado.
- No hay control de acceso en endpoints.
