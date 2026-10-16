# Spec Delta

## Purpose

Define el comportamiento funcional del servicio backend que recibirá registros de wallet, proveedor y ledger, generará conciliaciones investigables y expondrá consultas operativas mediante API y MCP.

## ADDED Requirements

### Requirement: Ingesta validada de registros normalizados

El sistema SHALL aceptar lotes de 1 a 1000 registros normalizados para wallet, provider o ledger, validando las referencias, fecha, canal, importe, moneda y campos requeridos por fuente.

#### Scenario: Carga válida
- **WHEN** se envía un lote no vacío que cumple el formato de la fuente
- **THEN** el sistema persiste los registros y devuelve la fuente y el total cargado

#### Scenario: Lote fuera de límites o con datos inválidos
- **WHEN** el lote está vacío, excede 1000 filas, el importe no es positivo, la moneda no tiene tres letras mayúsculas o faltan campos requeridos
- **THEN** el sistema rechaza la solicitud con un error de validación y no informa una carga exitosa

#### Scenario: Estado de proveedor obligatorio
- **WHEN** se cargan registros de provider sin estado o se incluye estado en registros wallet o ledger
- **THEN** el sistema rechaza el lote conforme a las reglas de validación de cada fuente

### Requirement: Conciliación única por fecha y canal

El sistema SHALL crear como máximo una corrida para cada combinación de fecha operativa y canal y SHALL comparar los registros disponibles usando reglas deterministas.

#### Scenario: Crear corrida con datos disponibles
- **WHEN** se solicita una fecha y canal con datos fuente y no existe una corrida previa para esa combinación
- **THEN** el sistema persiste la corrida y sus resultados y devuelve un identificador y un resumen

#### Scenario: Rechazar corrida duplicada
- **WHEN** se solicita una corrida para una combinación fecha y canal ya procesada
- **THEN** el sistema responde con conflicto y conserva los resultados existentes

#### Scenario: Rechazar corrida sin datos
- **WHEN** se solicita una corrida para una combinación fecha y canal sin registros fuente
- **THEN** el sistema informa que no hay datos y no crea una corrida

### Requirement: Clasificación de diferencias por referencia

El sistema SHALL identificar faltantes, duplicados, diferencias de canal, importe o moneda y estados de proveedor distintos de `SUCCESS`.

#### Scenario: Clasificar datos inconsistentes
- **WHEN** los registros agrupados por referencia presentan una condición soportada
- **THEN** el sistema crea una incidencia con referencia, tipo, detalle y estado inicial `OPEN`

#### Scenario: Clasificar proveedor no exitoso
- **WHEN** un registro de provider tiene estado `FAILED`, `PENDING` o `TIMEOUT`
- **THEN** el sistema crea una incidencia `PROVIDER_NOT_SUCCESSFUL`

#### Scenario: Contar una referencia conciliada
- **WHEN** las fuentes comparables coinciden y el provider reporta `SUCCESS`
- **THEN** el sistema cuenta la referencia como conciliada y no crea incidencia para ella

### Requirement: Gestión manual del estado de incidencias

El sistema SHALL permitir la gestión manual de incidencias mediante los estados `OPEN`, `IN_PROGRESS` y `RESOLVED`, exigiendo una nota no vacía para una resolución manual y prohibiendo la reapertura de una incidencia resuelta.

#### Scenario: Iniciar investigación
- **WHEN** se actualiza una incidencia `OPEN` a `IN_PROGRESS`
- **THEN** el sistema persiste y devuelve el nuevo estado

#### Scenario: Resolver manualmente con nota
- **WHEN** se actualiza una incidencia no resuelta a `RESOLVED` con nota de investigación
- **THEN** el sistema persiste el estado y la nota y devuelve la incidencia actualizada

#### Scenario: Rechazar resolución manual sin nota
- **WHEN** una persona intenta resolver manualmente una incidencia sin nota no vacía
- **THEN** el sistema rechaza la operación con un error de validación

#### Scenario: Rechazar reapertura
- **WHEN** se intenta cambiar una incidencia `RESOLVED` a `OPEN` o `IN_PROGRESS`
- **THEN** el sistema rechaza la operación con un conflicto y conserva `RESOLVED`

### Requirement: Auto-resolución limitada a escenarios sintéticos conocidos

Al crear una corrida, el sistema SHALL auto-resolver solo los registros sembrados conocidos para `AMOUNT_MISMATCH`, `MISSING_PROVIDER_RESULT` y `PROVIDER_NOT_SUCCESSFUL` con `PENDING`, usando la nota exacta `Se cierra automáticamente por error funcional`. No SHALL auto-resolver registros que no sean de esos escenarios demo.

#### Scenario: Cerrar escenarios funcionales conocidos de la demo
- **WHEN** una corrida detecta en datos sintéticos sembrados una diferencia de monto, un resultado de proveedor faltante o un estado de proveedor `PENDING`
- **THEN** la incidencia se crea en `RESOLVED` con la nota exacta `Se cierra automáticamente por error funcional`, pero la transacción no incrementa `reconciled_count`

#### Scenario: Mantener timeout abierto para investigación web
- **WHEN** la corrida detecta un resultado de proveedor `TIMEOUT` en la data sintética
- **THEN** crea una incidencia `PROVIDER_NOT_SUCCESSFUL` en estado `OPEN` con detalle `Tiempo de espera superado`, disponible para ingresar una nota y gestionar desde la web

#### Scenario: No auto-resolver datos que no son de demostración
- **WHEN** una corrida detecta un tipo de incidencia funcional en registros que no pertenecen al seed sintético
- **THEN** la incidencia permanece `OPEN` para investigación manual

#### Scenario: No contar una resolución automática como conciliación correcta
- **WHEN** una transacción contiene una discrepancia que se auto-resuelve durante la corrida
- **THEN** se incluye en `transaction_count` y los contadores de resueltas, pero no en `reconciled_count`

### Requirement: Métricas de transacciones e incidencias

El sistema SHALL exponer métricas de transacciones separadas de métricas de incidencias, sin mezclar sus unidades de conteo.

#### Scenario: Calcular métricas de corrida
- **WHEN** se consulta el resumen de una corrida
- **THEN** informa transacciones totales, conciliadas, no conciliadas, transacciones resueltas e incidencias resueltas en campos distintos

#### Scenario: Contar transacción resuelta
- **WHEN** una transacción tiene una o más incidencias y todas están en `RESOLVED`
- **THEN** cuenta como transacción resuelta y cada incidencia resuelta incrementa por separado el conteo de incidencias resueltas

#### Scenario: Resumen diario sin corridas
- **WHEN** se consulta una fecha sin corridas
- **THEN** el sistema devuelve conteos en cero y una lista de canales vacía

### Requirement: Disponibilidad por fecha y canal

El sistema SHALL informar conteos de registros por fuente para cada canal de una fecha y si ya existe una corrida, sin exponer referencias transaccionales en esa consulta.

#### Scenario: Consultar disponibilidad
- **WHEN** se consulta una fecha con registros de origen
- **THEN** el sistema devuelve canales, conteos por fuente y la existencia de una corrida para cada canal

#### Scenario: Fecha sin registros
- **WHEN** se consulta una fecha sin registros fuente
- **THEN** el sistema devuelve una lista de canales vacía

### Requirement: Historial filtrable y paginado de corridas

El sistema SHALL ofrecer un historial de corridas en orden cronológico inverso con filtros inclusivos de fecha, filtro exacto de canal y paginación acotada.

#### Scenario: Consultar historial con filtros válidos
- **WHEN** se consulta el historial con fechas y canal válidos
- **THEN** el sistema devuelve total filtrado, límite, desplazamiento y corridas con ID, fecha, canal, creación y resumen, sin detalle de incidencias

#### Scenario: Consultar historial sin filtros
- **WHEN** se consulta el historial sin parámetros de filtro
- **THEN** el sistema devuelve las corridas más recientes primero y aplica el límite de página predeterminado

#### Scenario: Rechazar rango o límite inválido
- **WHEN** la fecha inicial es posterior a la fecha final o el límite supera 100
- **THEN** el sistema responde con error de validación

### Requirement: Explicación determinista con evidencia limitada

El sistema SHALL explicar los tipos de incidencia soportados usando evidencia fuente actual, separando hechos, hipótesis no verificadas, evaluación y recomendación manual, sin cambiar datos ni estados.

#### Scenario: Evidencia suficiente para observar una condición
- **WHEN** la evidencia consultada permite observar la condición asociada a la incidencia
- **THEN** el sistema devuelve evaluación `OBSERVED`, hechos, evidencia por fuente, hipótesis no verificadas y recomendación manual

#### Scenario: Evidencia insuficiente o truncada
- **WHEN** falta evidencia suficiente o alguna fuente excede el límite de 20 filas
- **THEN** el sistema devuelve `INCONCLUSIVE`, informa la insuficiencia o truncamiento y no afirma una causa raíz

#### Scenario: Evidencia consultada después de una corrida
- **WHEN** se obtiene la explicación luego de cambios en los registros fuente
- **THEN** el sistema identifica la evidencia como actual al momento de la consulta y no como snapshot de la corrida

#### Scenario: Incidencia inexistente
- **WHEN** se solicita explicar un identificador de incidencia inexistente
- **THEN** el sistema responde `404`

#### Scenario: Evidencia contradictoria para incidencia resuelta
- **WHEN** la explicación de una incidencia `RESOLVED` detecta que la evidencia actual contradice la condición documentada al resolverla
- **THEN** el sistema señala una excepción que requiere revisión humana y mantiene el estado `RESOLVED` sin modificar la nota

### Requirement: Datos sintéticos locales seguros e idempotentes

El sistema SHALL poder poblar un entorno de desarrollo con datos sintéticos de los 14 días calendario completos anteriores en `America/Lima`, sin borrar datos ni crear corridas, e incluir escenarios `TIMEOUT` en algunas fechas para su investigación manual.

#### Scenario: Inicializar datos de demostración
- **WHEN** el servicio se inicia en desarrollo con el seed habilitado
- **THEN** asegura datos para los 14 días anteriores sin duplicar datos ya sembrados y sin crear corridas, con escenarios `TIMEOUT` en algunas fechas

#### Scenario: Deshabilitar seed
- **WHEN** el servicio se inicia en producción o el seed se deshabilita explícitamente
- **THEN** no se generan registros sintéticos

#### Scenario: Investigar manualmente un timeout desde la web
- **WHEN** Operaciones abre una incidencia sintética `TIMEOUT` en la web
- **THEN** puede ingresar una nota de investigación y actualizar el estado conforme al flujo manual existente

### Requirement: Operación MCP explícita y limitada

El servidor MCP SHALL permitir consultar disponibilidad, reportes, resumen diario, historial y explicaciones, y solicitar corridas manualmente; no SHALL cargar registros fuente ni actualizar estados o notas de incidencias.

#### Scenario: Consultar mediante MCP
- **WHEN** se solicita disponibilidad, reporte, resumen, historial o explicación
- **THEN** MCP devuelve el resultado del servicio backend sin ejecutar una operación de escritura

#### Scenario: Ejecutar una conciliación solicitada
- **WHEN** una persona solicita explícitamente una corrida para fecha y canal con datos disponibles
- **THEN** MCP solicita la corrida al backend y devuelve el reporte resultante sin omitir la protección contra duplicados

#### Scenario: Solicitud sin datos o corrida automática
- **WHEN** no existen datos para la fecha y canal solicitados o el servicio inicia
- **THEN** MCP informa la falta de datos o permanece inactivo y no crea corridas

#### Scenario: Auto-resolución de demo no se expone como escritura MCP
- **WHEN** el backend auto-resuelve un caso sintético al crear una corrida
- **THEN** MCP no ofrece herramientas para cargar registros ni para cambiar estados o notas de incidencias
