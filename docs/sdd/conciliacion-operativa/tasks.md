# Plan de trabajo: conciliacion operativa

Este plan convierte los requisitos de [spec.md](./spec.md) y el diseno de
[design.md](./design.md) en entregables verificables. Las tareas son trabajo
pendiente; marcar una casilla solo cuando se cumpla su salida y verificacion.

## Como usar este plan

- Los identificadores estables (`D-`, `DOM-`, `RUN-`, `API-`, `UI-`, `QA-`)
  permiten referenciar tareas en issues o revisiones.
- `Depende de` enumera prerequisitos reales; tareas sin prerequisitos dentro de
  su fase pueden avanzar en paralelo.
- No fijar framework, persistencia, rutas definitivas ni formatos de datos
  hasta revisar los patrones y contratos que ya existen en el repositorio de
  implementacion.
- El Slice 0 es un gate: no comenzar cambios funcionales que dependan de una
  decision abierta hasta que esta quede aprobada y documentada.
- Mantener la traza de ejecucion, grupos e incidencias. La ejecucion es de solo
  lectura sobre las fuentes financieras.

## Slice 0 — Descubrimiento y decisiones operativas

### D-01 — Inventariar las tres fuentes

- [ ] Localizar los servicios mock de wallet, proveedor y ledger, y registrar
  sus operaciones, modelos, ejemplos, paginacion, errores y datos disponibles.
- **Salida:** matriz de fuentes con campos de identificacion, estado, fecha,
  importe, moneda, canal y referencia de origen.
- **Verificacion:** cada campo de la matriz apunta a su contrato, codigo o
  fixture; los campos inexistentes quedan identificados como brechas.
- **Depende de:** ninguna.

### D-02 — Aprobar correlacion y semantica financiera

- [ ] Acordar la referencia canonica y las claves secundarias permitidas;
  definir que se hace con referencias ausentes, repetidas o contradictorias.
- [ ] Acordar moneda, precision, redondeo, zona horaria y regla para asignar la
  fecha operativa a registros con timestamps distintos.
- **Salida:** decision de dominio con ejemplos positivos, colisiones y casos
  que deben quedar ambiguos.
- **Verificacion:** es posible asignar todos los casos de ejemplo a una unica
  regla sin usar el orden de llegada ni comparar importes con punto flotante.
- **Depende de:** D-01.

### D-03 — Aprobar estados de proveedor y ventana asincrona

- [ ] Mapear los estados de cada canal a no terminal, exito terminal, fallo
  terminal o estado desconocido.
- [ ] Acordar SLA/ventana de espera y el instante desde el que se mide para
  declarar ausente un resultado o asiento.
- [ ] Acordar el tratamiento de reversiones, multiples intentos y eventos fuera
  de orden.
- **Salida:** tabla de estados y reglas de cierre por fuente/canal.
- **Verificacion:** cada estado observado tiene una accion definida y los
  ejemplos dentro/fuera de SLA producen clasificaciones distintas y esperadas.
- **Depende de:** D-01.

### D-04 — Aprobar incidencias e investigacion

- [ ] Aprobar catalogo de tipos de descalce, informacion de evidencia y clave
  estable para deduplicar incidencias.
- [ ] Aprobar estados, transiciones, reapertura, roles autorizados y politica
  sobre incidencias que dejan de detectarse en una nueva ejecucion.
- **Salida:** tabla de transiciones y permisos, y catalogo de incidencias con
  ejemplos.
- **Verificacion:** cada transicion valida e invalida tiene un resultado
  esperado y un evento de auditoria definido.
- **Depende de:** D-02 y D-03.

### D-05 — Acordar arquitectura de entrega

- [ ] Identificar patrones existentes para API, persistencia, autenticacion,
  tareas largas, errores, paginacion y UI en el repositorio que implementara el
  producto.
- [ ] Acordar volumen esperado, retencion, permisos, disponibilidad y umbrales
  de rendimiento del MVP.
- [ ] Elegir las rutas y contratos definitivos respetando las convenciones
  existentes; tratar los del diseno como candidatos.
- **Salida:** decisiones tecnicas registradas y contratos revisados por los
  responsables correspondientes.
- **Verificacion:** no quedan decisiones abiertas que cambien la clasificacion,
  la integridad financiera o el contrato externo del primer slice.
- **Depende de:** D-01 a D-04.

### Gate G0 — Aprobacion antes de implementar

- [ ] Revisar y aprobar las salidas D-01 a D-05 con Operaciones y responsables
  tecnicos.
- **Salida:** decisiones aprobadas, preguntas sin resolver con responsable y
  fecha, y alcance del primer release confirmado.
- **Verificacion:** RF-01 a RF-10 siguen siendo verificables con los contratos y
  reglas acordados.
- **Depende de:** D-01 a D-05.

## Slice 1 — Dominio y motor determinista

### DOM-01 — Definir modelos canonicos

- [ ] Modelar los registros de origen normalizados sin perder el identificador
  original ni la referencia a la evidencia recibida.
- [ ] Modelar grupo de transaccion, estado de conciliacion, diferencia,
  ejecucion e incidencia usando tipos restringidos y validaciones explicitas.
- [ ] Representar dinero con decimal exacto o unidades menores enteras segun la
  decision D-02; no usar punto flotante para igualdad monetaria.
- **Salida:** modelos y validadores que expresan las decisiones D-01 y D-02.
- **Verificacion:** entradas invalidas y valores fuera del dominio se rechazan
  con errores identificables; los modelos conservan la referencia de origen.
- **Depende de:** G0.

### DOM-02 — Implementar adaptadores de lectura

- [ ] Implementar un adaptador por fuente usando sus contratos reales.
- [ ] Traducir errores de transporte, respuestas invalidas y fallos parciales a
  errores tipados que indiquen la fuente.
- [ ] Mantener estas operaciones de solo lectura y propagar los filtros y
  limites admitidos por la fuente.
- **Salida:** tres adaptadores sustituibles por fixtures y con errores
  observables.
- **Verificacion:** pruebas de adaptador cubren respuesta valida, vacia,
  malformada, paginada y fallida para cada fuente.
- **Depende de:** DOM-01 y D-01.

### DOM-03 — Normalizar y correlacionar

- [ ] Normalizar estados, referencias, timestamps, importes, monedas y canales
  segun las decisiones aprobadas.
- [ ] Correlacionar registros con la clave canonica y conservar todos los
  candidatos y referencias de origen.
- [ ] Detectar duplicados y colisiones sin elegir una pareja silenciosamente.
- **Salida:** grupos de transaccion deterministas y casos ambiguos representados
  como tales.
- **Verificacion:** los mismos registros en distinto orden producen los mismos
  grupos; una colision no genera un emparejamiento arbitrario.
- **Depende de:** DOM-01 y DOM-02.

### DOM-04 — Implementar reglas de conciliacion

- [ ] Definir reglas puras y versionadas para coincidencia de wallet, proveedor
  y ledger, diferencias de importe/moneda y estados incompatibles.
- [ ] Aplicar la regla de precedencia aprobada entre `RECONCILED`, `PENDING` y
  `UNRECONCILED`.
- [ ] Aplicar SLA y estados terminales por fuente; no convertir una espera aun
  vigente en descalce confirmado.
- **Salida:** motor que devuelve clasificacion, regla aplicada y diferencias
  comparadas sin efectos secundarios.
- **Verificacion:** repetir la misma entrada con la misma version de reglas
  produce exactamente la misma salida.
- **Depende de:** DOM-03 y D-03.

### DOM-05 — Construir evidencia e incidencias candidatas

- [ ] Emitir evidencia auditable para cada clasificacion e incidencia:
  referencias de origen, valores comparados, regla y marcas de tiempo.
- [ ] Generar una clave estable para la incidencia usando el catalogo y las
  decisiones D-04.
- [ ] Distinguir los hechos recibidos de las conclusiones calculadas.
- **Salida:** resultado explicable y candidato de incidencia serializable.
- **Verificacion:** para cada tipo minimo de RF-05 se puede rastrear la
  clasificacion hasta registros y regla concretos.
- **Depende de:** DOM-04 y D-04.

### QA-01 — Probar dominio y reglas

- [ ] Crear pruebas de tabla para EA-01 a EA-06, incluidas fronteras del SLA,
  diferencias monetarias, ausencia de canal, duplicados y correlacion ambigua.
- [ ] Probar monedas distintas, precision maxima y valores no representables
  segun la politica aprobada.
- [ ] Probar que el orden de los registros no altera el resultado.
- **Salida:** suite automatizada de reglas y correlacion, alineada con el
  framework existente.
- **Verificacion:** cada regla aprobada tiene al menos un caso positivo, uno
  negativo y una frontera relevante; sin cambios al origen financiero.
- **Depende de:** DOM-01 a DOM-05.

## Slice 2 — Persistencia y ciclo de ejecucion

### RUN-01 — Persistir ejecuciones y resultados

- [ ] Crear el esquema/migracion para ejecuciones, resultados y referencias de
  evidencia, con indices para fecha, canal y referencia de transaccion.
- [ ] Guardar filtros, zona horaria, version de reglas, tiempos, estado de cada
  fuente y estado global de la ejecucion.
- **Salida:** resultados consultables por `runId` sin recalcular silenciosamente
  ni perder la procedencia.
- **Verificacion:** leer una ejecucion persistida devuelve los mismos grupos y
  filtros que produjo el motor; migraciones siguen el flujo del proyecto.
- **Depende de:** DOM-01 a DOM-05 y D-05.

### RUN-02 — Orquestar ejecucion completa y parcial

- [ ] Implementar ciclo de vida `SUCCEEDED`, `PARTIAL` y `FAILED` conforme a
  D-05.
- [ ] No publicar una ejecucion completa si una fuente requerida no pudo leerse;
  exponer fuente, error y etapa de fallo.
- [ ] Manejar reintentos de lectura de forma acotada e idempotente; no ocultar
  errores ni convertirlos en listas vacias.
- **Salida:** ejecucion trazable desde solicitud hasta resultado, con fallo
  explicito por fuente.
- **Verificacion:** EA-09 demuestra que un fallo no se presenta como exito ni
  como ausencia de registros.
- **Depende de:** DOM-02 y RUN-01.

### RUN-03 — Persistir incidencias idempotentemente

- [ ] Aplicar unicidad/actualizacion atomica sobre la clave estable de
  incidencia aprobada.
- [ ] En una reejecucion, actualizar ultima deteccion/evidencia y preservar el
  estado de investigacion y su historial.
- [ ] Registrar si la incidencia fue detectada en la ejecucion actual sin
  borrar ni resolver automaticamente incidencias anteriores.
- **Salida:** incidencias consistentes entre ejecuciones repetidas.
- **Verificacion:** EA-07 no incrementa el total de incidencias distintas ni
  revierte una investigacion existente.
- **Depende de:** DOM-05 y RUN-01.

### RUN-04 — Auditar cambios de investigacion

- [ ] Persistir actor, estado anterior/nuevo, hora y nota opcional en cada
  cambio permitido.
- [ ] Rechazar transiciones invalidas y proteger actualizaciones concurrentes.
- **Salida:** historial inmutable de cambios y estado actual recuperable.
- **Verificacion:** la carrera entre dos cambios no pierde eventos y una
  transicion no permitida deja intacto el estado.
- **Depende de:** D-04 y RUN-01.

### QA-02 — Probar persistencia y resiliencia

- [ ] Probar creacion, lectura, actualizacion idempotente, duplicado concurrente
  y conservacion de historial.
- [ ] Probar fallos antes, durante y despues de persistir una ejecucion y
  documentar el comportamiento de recuperacion.
- **Salida:** pruebas de integracion para el almacenamiento y ciclo de
  ejecucion.
- **Verificacion:** no quedan ejecuciones en estado de exito sin resultados
  persistidos completos ni incidencias duplicadas.
- **Depende de:** RUN-01 a RUN-04.

## Slice 3 — API de conciliacion y reportes

### API-01 — Definir contratos y controles de acceso

- [ ] Publicar esquemas de solicitud/respuesta, filtros, paginacion y errores
  de acuerdo con D-05 y convenciones existentes.
- [ ] Separar permisos de consulta, ejecucion y cambio de investigacion.
- [ ] Validar fecha, canal, ids, limites de pagina y transiciones en el borde de
  la API.
- **Salida:** contratos versionados y matriz de permisos.
- **Verificacion:** casos de entrada invalida producen errores explicitos y
  consultas no autorizadas no revelan evidencia.
- **Depende de:** G0 y RUN-01.

### API-02 — Exponer solicitud y estado de ejecucion

- [ ] Implementar solicitud de ejecucion; definir respuesta sincrona/asincrona
  segun el comportamiento acordado.
- [ ] Exponer `runId`, filtros normalizados, estado, fuentes, errores y marcas
  de tiempo.
- **Salida:** cliente puede iniciar una ejecucion y conocer su resultado real.
- **Verificacion:** una ejecucion parcial o fallida se distingue de una
  completada y es consultable por su id.
- **Depende de:** RUN-02 y API-01.

### API-03 — Exponer resultados e incidencias

- [ ] Implementar consultas paginadas de transacciones e incidencias con
  filtros de fecha operativa, canal y estado de investigacion aprobados.
- [ ] Exponer detalle de evidencia e historial respetando permisos y minimizacion
  de datos.
- [ ] Asegurar que el detalle pertenece a la ejecucion consultada cuando el
  recurso depende de `runId`.
- **Salida:** operaciones de consulta para resumen, listado y detalle.
- **Verificacion:** EA-08 devuelve exactamente el subconjunto de fecha/canal y
  mantiene paginacion estable.
- **Depende de:** API-01 y RUN-01.

### API-04 — Exponer resumen consistente

- [ ] Calcular transacciones analizadas, conciliadas, no conciliadas y
  pendientes sobre grupos canonicos distintos.
- [ ] Contar incidencias abiertas/en investigacion/resueltas por separado y sin
  duplicados.
- [ ] Incluir `runId`, fecha, canal, zona horaria y momento de calculo.
- **Salida:** resumen y detalle basados en el mismo corte de datos.
- **Verificacion:** las sumas concuerdan con el detalle y EA-08 produce iguales
  filtros en resumen e incidencias.
- **Depende de:** API-03 y DOM-04.

### API-05 — Exponer cambios de investigacion

- [ ] Implementar el cambio de estado autorizado con control de concurrencia y
  registro de actor.
- [ ] Responder de forma explicita a transicion invalida, version conflictiva o
  incidencia inexistente.
- **Salida:** operacion de investigacion auditada, separada de operaciones de
  conciliacion financiera.
- **Verificacion:** EA-10 pasa y la API no altera los registros de wallet,
  proveedor o ledger.
- **Depende de:** RUN-04 y API-01.

### QA-03 — Probar contratos y API

- [ ] Agregar pruebas de contrato para validacion, autorizacion, errores,
  paginacion, ejecucion, filtros, resumen y cambios de estado.
- [ ] Probar respuesta vacia legitima separada de fallo de fuente.
- **Salida:** suite API automatizada con fixtures reproducibles.
- **Verificacion:** se cubren RF-01, RF-04, RF-06 a RF-10 y las respuestas de
  error asociadas.
- **Depende de:** API-02 a API-05.

## Slice 4 — Dashboard y validacion end-to-end

### UI-01 — Mostrar ejecuciones y resumen

- [ ] Presentar fecha/canal aplicados, identificador y estado de ejecucion,
  totales de transacciones e incidencias y errores parciales.
- [ ] Distinguir visualmente conciliadas, no conciliadas y pendientes; no
  representar una ejecucion parcial/fallida como conciliacion completa.
- **Salida:** vista diaria consistente con API-04.
- **Verificacion:** totales visibles coinciden con la respuesta del backend para
  los mismos filtros.
- **Depende de:** API-02 y API-04.

### UI-02 — Filtrar y revisar incidencias

- [ ] Implementar filtros de fecha y canal, listado paginado y detalle de
  incidencia con evidencia.
- [ ] Mostrar estado de investigacion e historial; ofrecer transiciones solo a
  usuarios autorizados y solo las permitidas.
- [ ] Mostrar claramente canal desconocido/ausente sin asignarle uno ficticio.
- **Salida:** flujo operativo de consulta y seguimiento.
- **Verificacion:** filtros no mezclan fechas/canales y las acciones reflejan
  el estado persistido o el error devuelto por API.
- **Depende de:** API-03 y API-05.

### QA-04 — Validar experiencia y extremo a extremo

- [ ] Ejecutar EA-01 a EA-10 con fixtures/datos demostrativos, desde la
  obtencion de fuentes hasta el resumen y el detalle de investigacion.
- [ ] Revisar accesibilidad, estados de carga/vacio/error y usabilidad con
  Operaciones.
- [ ] Ensayar una demostracion reproducible con coincidencia, ausencias,
  diferencia de importe, duplicado, pendiente y reejecucion.
- **Salida:** evidencia de ejecucion y lista de defectos bloqueantes resueltos.
- **Verificacion:** no existen discrepancias entre clasificacion, incidencia,
  resumen y UI para el mismo `runId`.
- **Depende de:** UI-01, UI-02 y QA-03.

## Slice 5 — Preparacion operativa y entrega

### OPS-01 — Incorporar trazabilidad y metricas

- [ ] Registrar `runId`, etapa y fuente en logs sin incluir credenciales ni
  datos sensibles innecesarios.
- [ ] Medir ejecuciones por estado, duracion, errores por fuente, volumen por
  clasificacion e incidencias por tipo/antiguedad.
- [ ] Acordar umbrales y alertas con Operaciones.
- **Salida:** guia para diagnosticar ejecuciones y detectar degradacion.
- **Verificacion:** una ejecucion de prueba puede seguirse desde solicitud a
  resultados usando su `runId`.
- **Depende de:** RUN-02 y D-05.

### OPS-02 — Documentar operacion y soporte

- [ ] Documentar como lanzar, consultar y reintentar una ejecucion, interpretar
  resultados parciales, investigar un descalce y escalar errores de fuente.
- [ ] Documentar retencion, permisos, limitaciones conocidas y procedimiento de
  recuperacion.
- **Salida:** runbook y contratos finales actualizados junto con la entrega.
- **Verificacion:** un operador puede seguir el flujo usando el runbook sin
  depender de una explicacion oral del equipo de desarrollo.
- **Depende de:** OPS-01 y QA-04.

## Extension posterior — IA y MCP

Estas tareas no bloquean la conciliacion diaria determinista ni el primer
release, salvo que se apruebe expresamente su inclusion en alcance.

### AI-01 — Definir herramientas MCP de solo consulta

- [ ] Especificar entradas, salidas, autorizacion, limites de datos y
  trazabilidad para consultar ejecuciones, incidencias y resumen.
- **Salida:** contratos de herramientas alineados con API-01 y sin escritura en
  las fuentes financieras.
- **Verificacion:** entradas fuera de contrato se rechazan y cada consulta se
  puede rastrear.
- **Depende de:** API-01 a API-04 y aprobacion explicita de alcance.

### AI-02 — Habilitar explicaciones asistidas

- [ ] Separar evidencia confirmada de hipotesis; incluir referencias a
  resultados existentes y no permitir que el agente cambie una clasificacion.
- [ ] Mantener cualquier cambio de investigacion en el flujo API autorizado y
  auditado.
- **Salida:** explicacion no autoritativa que no altera registros ni resultados.
- **Verificacion:** pruebas confirman que el agente no puede ejecutar escrituras
  financieras ni resolver incidencias por su cuenta.
- **Depende de:** AI-01 y autorizacion de seguridad/Operaciones.

## Matriz de trazabilidad minima

| Criterio / requisito | Tareas principales | Prueba o evidencia |
| --- | --- | --- |
| CA-01 / RF-01 a RF-03: comparar las tres fuentes | D-01, DOM-01 a DOM-04, RUN-02 | QA-01, EA-01 a EA-06 |
| CA-02 / RF-04 a RF-06: registrar y seguir descalces | D-04, DOM-05, RUN-03, RUN-04, API-05, UI-02 | QA-02, QA-03, EA-02 a EA-07, EA-10 |
| CA-03 / RF-07: filtrar por fecha y canal | D-02, API-01, API-03, UI-02 | QA-03, EA-08 |
| CA-04 / RF-08 y RF-09: resumen e idempotencia | RUN-03, API-04 | QA-02, QA-03, EA-07, EA-08 |
| RF-10: trazabilidad y fallos explicitos | RUN-01, RUN-02, OPS-01, OPS-02 | QA-02, QA-03, QA-04, EA-09 |

## Definition of Done del MVP

- [ ] G0 esta aprobado y las decisiones relevantes estan documentadas.
- [ ] Criterios CA-01 a CA-04 y escenarios EA-01 a EA-10 tienen prueba
  automatizada o evidencia manual reproducible.
- [ ] Cada resultado muestra referencia de origen, regla y evidencia; resumen,
  lista y detalle coinciden para el mismo `runId` y filtros.
- [ ] Reejecutar no duplica incidencias ni borra su estado/historial.
- [ ] Fallos de fuente se notifican como parciales/fallidos, nunca como listas
  vacias presentadas como exito.
- [ ] La conciliacion no modifica transacciones ni asientos financieros.
- [ ] Permisos, auditoria, paginacion, zona horaria y retencion siguen las
  decisiones aprobadas.
- [ ] Dashboard, runbook y contratos estan revisados por Operaciones y por los
  responsables tecnicos.
- [ ] Las extensiones de IA/MCP permanecen fuera del release si no fueron
  aprobadas y validadas de forma independiente.
