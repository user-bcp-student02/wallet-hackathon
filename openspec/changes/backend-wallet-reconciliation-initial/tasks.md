# Tasks

## 1. Base del servicio y persistencia

- [ ] 1.1 Crear o ajustar la configuración y modelos persistentes necesarios; verificar la inicialización en una base temporal y en una base con datos previos sin borrar registros.
- [x] 1.2 Definir schemas de entrada y salida para fuentes, corridas, incidencias y resúmenes, incluyendo el estado de proveedor `TIMEOUT`; verificar validación y errores por fuente.

## 2. Ingesta y motor de conciliación

- [ ] 2.1 Implementar la carga validada de wallet, provider y ledger; verificar campos por fuente, límite de 1,000 registros y persistencia con pruebas de API.
- [ ] 2.2 Implementar la comparación determinista por referencia, clasificación de faltantes/duplicados/diferencias y unicidad fecha-canal; verificar tipos detectados, referencias conciliadas y conflicto de corrida duplicada.
- [x] 2.3 Aplicar la política de auto-resolución solo a los casos sintéticos conocidos al crear la corrida; verificar que ningún registro no demo del mismo tipo se auto-resuelve.
- [x] 2.4 Documentar el formato de registros, regla de cierre para escenarios demo y ejecución de conciliaciones; verificar los ejemplos contra las validaciones de API.

## 3. Investigación y auto-resolución de demo

- [ ] 3.1 Implementar transiciones manuales, nota humana obligatoria al resolver y rechazo de reapertura; verificar que las notas humanas se conservan y `RESOLVED` no vuelve a otro estado.
- [x] 3.2 Auto-resolver solo los casos sintéticos demo `AMOUNT_MISMATCH`, `MISSING_PROVIDER_RESULT` y `PENDING`, con la nota aprobada exacta; verificar estados y motivos.
- [x] 3.3 Crear escenarios sintéticos `TIMEOUT` en fechas seleccionadas y mantenerlos `OPEN`, disponibles para investigación manual desde la web.
- [x] 3.4 Verificar que incidencias no demo de los mismos tipos permanecen `OPEN` y que el flujo manual existente acepta nota y no reabre `RESOLVED`.
- [x] 3.5 Implementar y probar que los reportes y resúmenes reflejen estados automáticos, manteniendo separados los conteos de transacciones resueltas e incidencias resueltas.
- [x] 3.6 Documentar alcance demo-only del auto-cierre, estado `TIMEOUT` y conteos de transacciones/incidencias; verificar consistencia con contrato y pruebas.

## 4. Reportes, evidencia y explicación

- [ ] 4.1 Implementar disponibilidad, historial filtrado y paginado; verificar conteos, orden, límites y filtros con pruebas de API.
- [ ] 4.2 Implementar explicación determinista de los tipos de incidencia con hechos, hipótesis no verificadas y recomendación manual; verificar los tipos soportados.
- [x] 4.3 Verificar que la explicación de incidencias demo continúa siendo de solo lectura, incluida la explicación de escenarios `TIMEOUT`, sin cambiar estado ni nota.
- [ ] 4.4 Limitar evidencia explicativa a 20 filas por fuente y devolver inconcluso ante falta o truncamiento; verificar límites, temporalidad actual y ausencia de modificaciones en fuentes, estados y métricas.
- [ ] 4.5 Documentar contratos de disponibilidad, historial y explicación; verificar los ejemplos contra los schemas de respuesta.

## 5. Entorno local y herramientas MCP

- [x] 5.1 Implementar seed sintético idempotente para los 14 días calendario completos anteriores en `America/Lima`, con escenarios `TIMEOUT` en algunas fechas; verificar conservación de registros, ausencia de duplicados y de corridas.
- [ ] 5.2 Implementar tools MCP para disponibilidad, reportes, resumen, historial, explicación y ejecución manual explícita; verificar delegación a la API y que MCP no carga registros ni cambia estados/notas.
- [ ] 5.3 Documentar instalación local, configuración MCP y límites operativos; verificar los comandos en una instalación limpia.

## 6. Verificación integrada

- [x] 6.1 Ejecutar la suite backend completa y verificar cobertura de API, auto-resolución demo, persistencia, explicación, seed y MCP.
