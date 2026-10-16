# Especificacion: conciliacion operativa de transacciones

## Lenguaje del dominio

- **Ejecucion:** procesamiento de un conjunto de registros de origen para una
  fecha operativa y filtros determinados.
- **Grupo de transaccion:** registros de wallet, proveedor y ledger que se
  relacionan con una misma referencia canonica.
- **Estado de conciliacion:** resultado determinista de comparar el grupo.
- **Incidencia:** descalce que requiere seguimiento operativo.
- **Estado de investigacion:** progreso de la gestion de una incidencia.
- **Canal:** canal de proveedor asociado al resultado de pago.

El estado de conciliacion no sustituye el estado de investigacion. Resolver una
incidencia no cambia la evidencia financiera ni reescribe el resultado original.

## Requisitos funcionales

### RF-01 — Comparacion de fuentes

El sistema MUST comparar para una fecha operativa los registros de intencion de
wallet, los resultados de proveedor y los asientos de ledger disponibles.
Cada resultado MUST conservar las referencias a los registros de origen que
participaron en la comparacion.

### RF-02 — Correlacion y normalizacion

El sistema MUST normalizar los campos necesarios para comparar las fuentes y
correlacionarlas mediante las claves aprobadas para el MVP. MUST NOT emparejar
registros con claves ambiguas como si la coincidencia fuera cierta; debe
registrar el caso para investigacion.

### RF-03 — Clasificacion determinista

El sistema MUST clasificar cada grupo como conciliado, no conciliado o
pendiente, usando reglas versionadas y reproducibles. La clasificacion MUST
indicar los valores comparados y la regla que produjo el resultado.

Una respuesta asincrona no terminal MUST permanecer pendiente. La ausencia de
resultado o asiento solo se clasifica como descalce confirmado cuando se cumpla
la condicion de cierre/SLA acordada para esa fuente.

### RF-04 — Incidencias

Cada descalce confirmado MUST crear o actualizar una incidencia con:

- identificador estable;
- referencia de transaccion y canal, cuando esten disponibles;
- tipo de descalce y fuentes involucradas;
- estado actual de investigacion;
- fecha de deteccion;
- valores comparados y referencias de evidencia;
- ejecucion que lo detecto y marcas de tiempo relevantes.

### RF-05 — Tipos minimos de descalce

El sistema MUST poder representar, cuando la evidencia lo permita:

- resultado del proveedor ausente tras el SLA;
- asiento del ledger ausente tras el SLA;
- registro sin pareja en una fuente;
- diferencia de importe;
- diferencia de moneda;
- duplicado en una fuente;
- estado terminal incompatible entre fuentes;
- correlacion ambigua.

El catalogo definitivo y las condiciones de emision deben validarse contra los
contratos reales y las reglas del negocio.

### RF-06 — Estado de investigacion

El sistema MUST exponer el estado actual de investigacion de cada incidencia y
preservar el historial de cambios, actor y fecha. El conjunto inicial propuesto
es `OPEN`, `INVESTIGATING` y `RESOLVED`; la transicion permitida, autorizacion y
posibilidad de reapertura quedan sujetas a aprobacion operativa.

### RF-07 — Reporte filtrable

El reporte MUST poder filtrarse por fecha operativa y canal de proveedor. La
respuesta MUST indicar los filtros aplicados y la zona horaria usada para
determinar la fecha. El canal debe proceder del registro del proveedor; los
registros sin canal no se deben asignar a un canal ficticio.

### RF-08 — Resumen diario

Para los filtros aplicados, el resumen MUST incluir como minimo:

- transacciones analizadas;
- transacciones conciliadas;
- transacciones no conciliadas;
- transacciones pendientes;
- incidencias abiertas/en investigacion;
- incidencias resueltas.

Cada transaccion se cuenta una sola vez por ejecucion y agrupacion canonica.
Las incidencias resueltas se cuentan aparte y no como una tercera categoria
mutuamente excluyente de transacciones.

### RF-09 — Reejecucion idempotente

Volver a procesar los mismos registros y reglas MUST NOT crear incidencias
duplicadas ni borrar actualizaciones de investigacion. El resultado debe
permitir distinguir una nueva ejecucion de una nueva incidencia.

### RF-10 — Trazabilidad y errores

Cada ejecucion MUST registrar fecha, filtros, version de reglas, fuentes leidas,
resultado y errores por fuente. Si una fuente falla, el sistema MUST informar
que la ejecucion es parcial o fallida y MUST NOT presentar el resultado parcial
como conciliacion completa.

## Requisitos no funcionales

- **NFR-01 Verificabilidad:** cada clasificacion se explica con evidencia y
  reglas deterministas; no depende de texto generativo.
- **NFR-02 Integridad:** el proceso de conciliacion es de solo lectura respecto
  de las fuentes financieras.
- **NFR-03 Consistencia:** resumen, listado y detalle usan la misma ejecucion,
  filtros, zona horaria y reglas de conteo.
- **NFR-04 Seguridad:** solo usuarios autorizados pueden ejecutar procesos o
  cambiar estados de investigacion; consultas devuelven el minimo dato necesario.
- **NFR-05 Auditabilidad:** ejecuciones y cambios de investigacion tienen
  historial suficiente para reconstruir quien hizo que y cuando.
- **NFR-06 Resiliencia:** fallo o retraso de un proveedor no se presenta como
  conciliacion exitosa ni transforma automaticamente un pendiente en incidencia.
- **NFR-07 Rendimiento y retencion:** umbrales, paginacion y politica de
  retencion se fijan luego de conocer volumen, infraestructura y obligaciones.

## Escenarios de aceptacion

### EA-01 — Transaccion coincidente en las tres fuentes

**Dado** un grupo con una intencion, un resultado terminal exitoso y un asiento
del ledger correlacionados, con importes y moneda iguales.

**Cuando** se ejecuta la conciliacion para su fecha y canal.

**Entonces** el grupo se clasifica como conciliado, no crea incidencia y aporta
una unidad al total de conciliados.

### EA-02 — Intencion sin resultado del proveedor

**Dado** una intencion sin resultado de proveedor.

**Cuando** aun no se cumple el SLA acordado.

**Entonces** el grupo queda pendiente y no se cuenta como descalce confirmado.

**Y cuando** vence el SLA sin resultado.

**Entonces** se crea una incidencia de resultado ausente con evidencia y estado
de investigacion inicial.

### EA-03 — Resultado exitoso sin asiento

**Dado** un resultado terminal exitoso sin asiento correlacionado.

**Cuando** se cumple la condicion de cierre acordada para el ledger.

**Entonces** se crea una incidencia de asiento ausente con la referencia del
proveedor y de la intencion disponible.

### EA-04 — Importe o moneda diferente

**Dado** registros correlacionados con distinto importe o moneda.

**Cuando** se ejecuta la comparacion.

**Entonces** el grupo se clasifica como no conciliado y la incidencia conserva
ambos valores, sus monedas y las fuentes correspondientes.

### EA-05 — Respuesta asincrona pendiente

**Dado** un proveedor que informa un estado no terminal.

**Cuando** se ejecuta la conciliacion antes del SLA.

**Entonces** la transaccion se cuenta como pendiente, no como conciliada ni como
descalce confirmado, y no se crea una incidencia de ausencia prematura.

### EA-06 — Duplicado en una fuente

**Dado** dos registros de la misma fuente que compiten por una referencia.

**Cuando** se ejecuta la conciliacion.

**Entonces** el sistema no escoge uno silenciosamente y crea/actualiza una
incidencia de duplicado o correlacion ambigua con ambas evidencias.

### EA-07 — Reejecucion sobre los mismos datos

**Dado** un descalce ya registrado.

**Cuando** se vuelve a ejecutar la misma fecha con datos y reglas sin cambios.

**Entonces** se registra una nueva ejecucion si corresponde, se conserva la
incidencia existente y no se duplica su contador.

### EA-08 — Filtro por fecha y canal

**Dado** resultados para varias fechas y canales.

**Cuando** se consulta una fecha y un canal especificos.

**Entonces** resumen, transacciones e incidencias corresponden al mismo
subconjunto y la respuesta declara los filtros aplicados.

### EA-09 — Fuente no disponible

**Dado** que falla la lectura de una de las tres fuentes requeridas.

**Cuando** se intenta ejecutar la conciliacion.

**Entonces** la ejecucion se marca parcial o fallida, el error identifica la
fuente y no se presenta como reporte completo ni exitoso.

### EA-10 — Cambio de investigacion

**Dado** una incidencia abierta.

**Cuando** un usuario autorizado cambia su estado.

**Entonces** se valida la transicion, el actor y la fecha quedan auditados y el
estado anterior permanece consultable.

## Trazabilidad de criterios

| Criterio de aceptacion original | Requisitos / escenarios |
| --- | --- |
| CA-01 Comparacion wallet, proveedor y ledger | RF-01 a RF-03; EA-01 a EA-06 |
| CA-02 Referencia, tipo y estado de investigacion | RF-04 a RF-06; EA-02 a EA-06, EA-10 |
| CA-03 Filtros por fecha y canal | RF-07; EA-08 |
| CA-04 Resumen diario | RF-08 y RF-09; EA-01, EA-07 y EA-08 |
