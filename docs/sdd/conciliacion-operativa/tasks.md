# Plan de trabajo: conciliacion operativa

Las tareas estan ordenadas por dependencias. No representan trabajo ya
implementado. El orden debe revisarse despues de validar los contratos y
resolver las preguntas abiertas de la propuesta.

## Slice 0 — Descubrimiento y decisiones

- [ ] Inspeccionar los servicios mock de wallet, proveedor y ledger, sus datos,
  contratos, estados y errores.
- [ ] Documentar claves de correlacion, campos obligatorios, zona horaria,
  monedas y politica de importes.
- [ ] Acordar estados terminales, SLA/ventana asincrona y reglas para reversiones
  y pagos fallidos.
- [ ] Aprobar tipos de incidencia, transiciones, permisos y politica de
  resolucion/reapertura.
- [ ] Acordar volumen, paginacion, retencion, tecnologia de persistencia y
  contratos API/UI conforme a patrones existentes.

## Slice 1 — Dominio y motor determinista

- [ ] Definir modelos canonicos tipados y validacion de registros de origen.
- [ ] Implementar adaptadores de lectura de las tres fuentes y manejo explicito
  de fallos parciales.
- [ ] Implementar correlacion determinista, duplicados y deteccion de
  ambiguedades.
- [ ] Implementar clasificacion de conciliado, no conciliado y pendiente con
  reglas versionadas.
- [ ] Producir evidencia explicable por cada resultado e incidencia.
- [ ] Agregar pruebas unitarias para cada regla monetaria, estado asincrono,
  registro ausente, duplicado y correlacion.

## Slice 2 — Persistencia y ejecuciones

- [ ] Persistir ejecuciones, filtros, estado de fuentes, version de reglas y
  resultados.
- [ ] Implementar claves de idempotencia/unicidad para evitar incidencias
  duplicadas en reejecuciones.
- [ ] Persistir estados de investigacion e historial de cambios con control de
  concurrencia.
- [ ] Probar reejecucion, fallo durante lectura y recuperacion/reintento.

## Slice 3 — API y resumen

- [ ] Ajustar rutas, DTOs, autenticacion, errores y paginacion a la arquitectura
  real del repositorio.
- [ ] Exponer ejecucion, estado de ejecucion, resultados, detalle de incidencia
  y cambios autorizados de investigacion.
- [ ] Calcular resumen diario desde el mismo conjunto de resultados que usa el
  detalle.
- [ ] Implementar filtros por fecha operativa y canal, incluyendo semantica
  acordada para canal ausente.
- [ ] Agregar pruebas de contrato e integracion para filtros, permisos, errores
  y consistencia de conteos.

## Slice 4 — Dashboard y validacion end-to-end

- [ ] Mostrar resumen, filtros, estados y lista/detalle de incidencias.
- [ ] Mostrar estado parcial/fallido de ejecuciones sin presentarlo como
  conciliacion completa.
- [ ] Validar con datos de ejemplo los escenarios EA-01 a EA-10 de
  [spec.md](./spec.md).
- [ ] Ejecutar regresion y revisar accesibilidad/usabilidad con Operaciones.
- [ ] Preparar demo reproducible con datos coincidentes, descalces, pendientes,
  duplicados y reejecucion.

## Extension posterior: IA y MCP

- [ ] Definir herramientas MCP de consulta de resultados y resumen con
  permisos minimos.
- [ ] Separar hechos observados de hipotesis en explicaciones generadas.
- [ ] Mantener las herramientas MCP sin permisos para modificar fuentes
  financieras; cambios de investigacion pasan por API autorizada y auditada.
- [ ] Probar entradas invalidas, limites de datos, autorizacion y trazabilidad
  antes de habilitar agentes.

## Definition of Done

- Todos los criterios de aceptacion aprobados tienen pruebas automatizadas o
  evidencia de validacion manual reproducible.
- Resultados, resumen e incidencias son consistentes para los mismos filtros y
  ejecucion.
- Se demuestra que una reejecucion no duplica incidencias y conserva su
  historial.
- Errores de fuente se muestran explicitamente y nunca como resultado exitoso.
- No se modifican registros financieros de origen.
- Contratos, decisiones operativas y preguntas resueltas quedan documentados.
