# Propuesta: conciliacion operativa de transacciones

## Problema

Operaciones necesita identificar cada dia diferencias entre las intenciones de
pago de la wallet, los resultados de los canales de proveedor y los asientos
correspondientes del ledger. Sin una comparacion trazable, un resultado
asincrono, un registro ausente o un importe distinto puede quedar oculto o
interpretarse prematuramente como definitivo.

## Objetivo

Producir una vista diaria verificable que agrupe registros de las tres fuentes,
clasifique su estado de conciliacion, registre descalces investigables y permita
consultar un resumen filtrado por fecha y canal de proveedor.

## Alcance propuesto

### Incluido

- Lectura de intenciones de wallet, resultados de proveedor y asientos de ledger
  mediante las fuentes disponibles en el MVP.
- Normalizacion y correlacion determinista de registros.
- Deteccion de ausencias, duplicados, diferencias de importe o moneda y estados
  asincronos pendientes.
- Persistencia de ejecuciones y de incidencias con evidencia y trazabilidad.
- Consulta de resultados e incidencias por fecha y canal.
- Resumen diario de transacciones conciliadas, no conciliadas y pendientes, y
  recuento separado de incidencias resueltas.
- Reprocesamiento idempotente de los mismos datos.

### No incluido en el primer slice

- Conectividad con proveedores financieros reales.
- Escritura o correccion automatica de transacciones o asientos financieros.
- Decisiones de conciliacion basadas en IA.
- Agentes, MCP o explicaciones generativas como requisito para la salida diaria.
- Reglas contables especificas no provistas por el dominio del MVP.

La arquitectura deja puntos de integracion para futuras consultas asistidas por
IA/MCP. Esas capacidades deberan consumir resultados existentes y no sustituir
las reglas deterministas.

## Usuarios y valor

- **Analista de operaciones:** detecta y prioriza descalces, revisa evidencia y
  actualiza el estado de investigacion.
- **Responsable operativo:** consulta volumen, tendencias y progreso de
  resolucion por dia y canal.
- **Equipo de desarrollo:** puede reproducir una ejecucion y explicar por que
  cada transaccion fue clasificada de una manera determinada.

## Criterios de exito

1. Cada grupo conciliado se puede rastrear hasta sus registros de wallet,
   proveedor y ledger.
2. Cada descalce tiene referencia, tipo, evidencia y estado de investigacion.
3. Una respuesta pendiente del proveedor no se reporta como un descalce
   confirmado antes del umbral operativo acordado.
4. El resumen y el detalle concuerdan para la misma fecha y canal, sin contar
   dos veces una transaccion o incidencia.
5. Repetir una ejecucion sobre los mismos datos no crea incidencias duplicadas.

## Supuestos

- El MVP usa servicios mock; no se presupone una integracion productiva externa.
- Existe o se podra obtener una referencia estable que relacione las fuentes.
- La fecha operativa se interpreta en la zona `America/Lima`, salvo que el
  negocio confirme otra regla.
- El estado de conciliacion y el estado de investigacion son dimensiones
  distintas.
- Los totales de conciliados/no conciliados describen transacciones; el total
  de resueltos describe incidencias. No son categorias mutuamente excluyentes.

## Riesgos y dependencias

- Claves de correlacion incompletas o no unicas pueden producir falsos
  emparejamientos.
- Los formatos, estados terminales y semantica de importes dependen de los
  contratos reales de los mocks.
- Sin un SLA para resultados asincronos, no se puede clasificar de forma
  consistente una respuesta ausente como pendiente o descalce.
- Persistencia y volumen esperado no estan especificados; esto afecta consultas,
  retencion e idempotencia.

## Preguntas para cerrar antes de implementar

1. Cual es la referencia canonica que comparten wallet, proveedor y ledger? Hay
   casos en los que la correlacion requiere mas de una clave?
2. Que estados del proveedor son terminales y cual es el SLA para marcar como
   ausente una respuesta que sigue pendiente?
3. La investigacion puede marcar una incidencia como resuelta solo un operador
   autorizado, o tambien se permite una resolucion automatica al reconciliarse
   los datos?
4. Cuales son los canales MVP y como se representan registros sin canal?
5. Que moneda(s), precision y politica de redondeo aplican?
6. Que tecnologias, contratos y limites de paginacion tienen los servicios mock
   actuales?
7. Que roles pueden ejecutar conciliaciones y cambiar estados de investigacion,
   y por cuanto tiempo se conserva la evidencia?

## Decision solicitada

Revisar y aprobar el alcance, los supuestos y las preguntas abiertas. La
implementacion debe comenzar solo despues de inspeccionar las fuentes y acordar
las reglas operativas que cambian la clasificacion de una transaccion.
