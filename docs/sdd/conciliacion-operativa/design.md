# Diseno tecnico propuesto: conciliacion operativa

## Estado del diseno

Propuesta logica, pendiente de contrastar con el codigo, las tecnologias y los
contratos de los servicios mock. Los nombres de componentes y operaciones que
siguen no son contratos existentes.

## Principios

1. El motor de conciliacion es determinista; IA no clasifica resultados
   financieros.
2. Las fuentes Wallet, Proveedor y Ledger se consultan sin mutarlas.
3. Se preserva la evidencia de origen junto con cada regla aplicada.
4. Los pendientes asincronos se distinguen de los descalces confirmados.
5. Repetir una ejecucion no duplica incidencias ni pierde su estado operativo.
6. Resumen y detalle derivan del mismo resultado de ejecucion.

## Componentes logicos

1. **Adaptadores de fuente:** consultan wallet, proveedor y ledger, validan
   respuestas y traducen campos al modelo canonico. No se definira un adaptador
   concreto hasta inspeccionar las interfaces actuales.
2. **Normalizador:** valida referencias, importes, moneda, canal, estado y
   timestamps; conserva el valor original y el normalizado.
3. **Correlacionador:** agrupa registros con la clave canonica aprobada. Las
   colisiones y claves ambiguas se derivan a incidencias, no se resuelven por
   orden de llegada.
4. **Motor de reglas:** calcula estado de conciliacion, diferencias y evidencia
   de forma determinista.
5. **Persistencia de conciliacion:** guarda ejecuciones, resultados, incidencias
   e historial de investigacion sin escribir en las fuentes financieras.
6. **API de reportes:** sirve resumen, detalle y filtros; autoriza cambios de
   investigacion por separado de las consultas.
7. **Dashboard:** presenta resumen diario, filtros e incidencias. No contiene
   reglas financieras.
8. **Extension futura IA/MCP:** solo consulta resultados/evidencia y explica
   hechos frente a hipotesis. No inicia escrituras financieras ni cambia
   estados de investigacion sin una operacion explicita y autorizada.

## Flujo de datos

1. Un operador o proceso solicita ejecutar la conciliacion para una fecha y,
   opcionalmente, un canal.
2. La API valida fecha y canal, registra una ejecucion y consulta las fuentes.
3. Los adaptadores informan exitos y errores individualmente. Un fallo en una
   fuente requerida produce una ejecucion parcial/fallida, nunca una salida
   completa con exito aparente.
4. El normalizador conserva referencias a los datos originales y calcula la
   fecha operativa en `America/Lima` como supuesto inicial.
5. El correlacionador crea grupos por clave aprobada y marca duplicados o
   ambiguedades.
6. El motor aplica reglas y produce estado, tipos de diferencia y evidencia.
7. La capa de persistencia registra resultado e incidencias de forma idempotente
   respecto de la ejecucion y la clave de incidencia.
8. API y dashboard leen ese resultado persistido para que totales y detalle
   correspondan al mismo corte.

## Modelo de dominio candidato

| Entidad | Campos principales | Proposito |
| --- | --- | --- |
| `ReconciliationRun` | `id`, `businessDate`, `channel?`, `status`, `ruleVersion`, `startedAt`, `completedAt`, `sourceStatus`, `errorSummary` | Identifica filtro y resultado de una ejecucion. |
| `SourceRecord` | `source`, `sourceRecordId`, `transactionRef?`, `channel?`, `amount?`, `currency?`, `sourceStatus?`, `eventAt?`, `rawReference` | Representa evidencia normalizada con referencia al original. |
| `ReconciliationResult` | `runId`, `transactionRef`, `channel?`, `reconciliationStatus`, `sourceRecordIds`, `differences`, `ruleIds` | Resultado calculado para un grupo canonico. |
| `ReconciliationIssue` | `id`, `issueKey`, `transactionRef?`, `channel?`, `type`, `sources`, `investigationStatus`, `firstDetectedAt`, `lastDetectedAt`, `evidence`, `resolution?` | Descalce y su gestion persistente. |
| `InvestigationEvent` | `issueId`, `previousStatus`, `newStatus`, `actorId`, `occurredAt`, `note?` | Historial auditable de cambios de investigacion. |

Los tipos/formatos de importes, moneda, identificadores y timestamps se deben
definir usando contratos reales. Nunca se deben usar numeros de punto flotante
para decidir igualdad monetaria; se requiere aritmetica decimal o unidades
menores enteras segun la fuente.

## Clasificacion propuesta

- `RECONCILED`: existe un conjunto no ambiguo de registros requeridos, sus
  estados terminales son compatibles y los importes/monedas coinciden segun la
  politica aprobada.
- `PENDING`: hay una respuesta no terminal o falta una fuente cuya ventana de
  espera no ha vencido. No crea un descalce confirmado por esa ausencia.
- `UNRECONCILED`: hay evidencia suficiente de inconsistencia, por ejemplo
  importe/moneda incompatible, duplicado, emparejamiento ambiguo o fuente ausente
  despues de la condicion de cierre acordada.

La categoria por transaccion debe derivarse de una sola regla de precedencia
versionada. Propuesta: inconsistencia confirmada prevalece sobre pendiente;
pendiente prevalece sobre conciliado; conciliado solo cuando no hay diferencias
y se cumplen todos los requisitos. Las reglas exactas para estados de pago
fallidos, reversiones y multiples asientos quedan abiertas hasta inspeccionar
los servicios.

## Incidencias e idempotencia

- Propuesta de clave natural: referencia canonica + canal (si aplica) + tipo de
  descalce + fuente(s) involucradas. Se debe incorporar un identificador estable
  de origen cuando la referencia transaccional no sea suficiente.
- La persistencia debe aplicar una restriccion unica o mecanismo equivalente
  para evitar crear la misma incidencia en ejecuciones repetidas.
- Al volver a detectar una incidencia existente, actualizar `lastDetectedAt` y
  la evidencia/version de ejecucion, preservando su estado de investigacion y
  su historial.
- Si los datos posteriores dejan de mostrar el descalce, no se debe resolver
  automaticamente hasta que Operaciones apruebe la politica. Se puede marcar
  como ya no detectado en la ejecucion reciente sin borrar ni reescribir la
  incidencia.

## Conteos y consultas

- Los conteos de conciliadas, no conciliadas y pendientes se calculan sobre
  grupos de transaccion distintos, no sobre numero bruto de registros.
- Las incidencias abiertas/en investigacion/resueltas se cuentan por incidencia
  distinta en el filtro de fecha/canal, independientemente de su estado de
  conciliacion actual.
- Un resumen debe declarar `runId`, fecha operativa, canal aplicado, zona
  horaria y momento de calculo.
- Si el mismo registro aparece en multiples ejecuciones, no se suma mas de una
  vez dentro del resumen de una ejecucion.

## Contratos HTTP candidatos

Los siguientes son ejemplos de recursos logicos, no rutas aprobadas:

| Operacion | Proposito |
| --- | --- |
| `POST /reconciliation-runs` | Solicitar una ejecucion para `businessDate` y canal opcional; devuelve `runId` y estado de ejecucion. |
| `GET /reconciliation-runs/{runId}` | Consultar estado, filtros y errores de fuentes. |
| `GET /reconciliation-runs/{runId}/summary` | Obtener los totales del mismo corte. |
| `GET /reconciliation-runs/{runId}/transactions` | Listar resultados con paginacion y filtros. |
| `GET /reconciliation-issues` | Buscar incidencias por fecha, canal y estado. |
| `GET /reconciliation-issues/{issueId}` | Ver detalle, evidencia e historial. |
| `PATCH /reconciliation-issues/{issueId}/investigation-status` | Solicitar un cambio autorizado de estado, con actor y nota opcional. |

Las respuestas de ejecucion deberan distinguir `SUCCEEDED`, `PARTIAL` y
`FAILED`; una ejecucion larga puede necesitar respuesta asincrona con `runId`
consultable. Autenticacion, codigos de error, paginacion e idempotency key del
POST se deben ajustar a convenciones existentes.

## Estados de investigacion propuestos

`OPEN -> INVESTIGATING -> RESOLVED`. Se recomienda permitir transiciones
explicitas y auditadas; la reapertura (`RESOLVED -> OPEN`) requiere politica y
autorizacion acordadas. El API debe rechazar transiciones no permitidas con un
error legible, no aceptarlas silenciosamente. Estos estados son una propuesta,
no una regla ya aprobada.

## Seguridad, auditoria y manejo de fallos

- Separar permisos de lectura de reportes, ejecucion y cambio de investigacion.
- Validar fecha, canal, identificadores y paginacion en el limite de API.
- No exponer datos sensibles de origen que no sean necesarios para investigar.
- Registrar actor, accion, resultado y `runId`; evitar incluir credenciales o
  datos sensibles completos en logs.
- Identificar fuente fallida y error correlacionable; no ocultar fallos con
  arrays vacios ni resultados de exito predeterminados.
- Proteger cambios de estado contra concurrencia mediante versionado o
  actualizacion condicional.
- Acordar retencion, acceso a evidencia y politica de eliminacion antes de
  produccion.

## Observabilidad

Metricas minimas propuestas: ejecuciones por estado, duracion, errores por
fuente, grupos conciliados/no conciliados/pendientes, incidencias por tipo y
antiguedad, y tiempo hasta resolucion. Incluir `runId` en logs y respuestas para
permitir rastreo. Los umbrales de alerta se acordaran con el objetivo operativo
del MVP.
