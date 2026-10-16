# Proposal

## Why

Se necesita un servicio que permita comparar movimientos de wallet, proveedor y ledger de forma repetible y detectar diferencias que requieran investigación. Definir primero sus contratos y límites permitirá construir la API y su operación asistida sin mezclar decisiones automáticas con confirmaciones del analista.

## What Changes

- Crear una API para cargar registros normalizados de wallet, provider y ledger y validar sus campos antes de persistirlos.
- Implementar conciliación determinista por fecha y canal, con protección contra corridas duplicadas y clasificación de registros faltantes, duplicados y diferencias.
- Proveer reportes por corrida, disponibilidad por fecha/canal, resumen diario e historial paginado, con métricas de transacciones e incidencias claramente separadas.
- Permitir el seguimiento manual de incidencias y exigir una nota para resolverlas manualmente.
- En las corridas de demostración, cerrar automáticamente solo los escenarios sintéticos funcionales conocidos (diferencia de monto, falta de respuesta de proveedor y resultado `PENDING`), agregando la nota `Se cierra automáticamente por error funcional`. Mantener abierto el escenario sintético `TIMEOUT` para que Operaciones registre su investigación manualmente en la web. No aplicar esta regla a referencias que no pertenezcan al seed de demostración.
- Añadir una explicación determinista basada en evidencia fuente acotada, diferenciando hechos, hipótesis y recomendaciones sin modificar estados. Si evidencia actual contradice una incidencia `RESOLVED`, señalarlo como excepción para revisión humana sin reabrirla.
- Facilitar un entorno local reproducible con SQLite y datos sintéticos de demostración idempotentes para los 14 días calendario completos anteriores en `America/Lima`, incluyendo escenarios de timeout en algunas fechas.
- Exponer herramientas MCP para consulta y ejecución explícita de conciliaciones; no incluir scheduler ni carga de registros o cambios de incidencias desde MCP. El auto-cierre demo ocurre únicamente dentro de la corrida solicitada.

## Capabilities

### New Capabilities

- `backend/wallet-reconciliation-api`: contrato funcional del servicio de conciliación, investigación, reporting y operación manual mediante API y MCP.

### Modified Capabilities

Ninguna. No hay especificaciones OpenSpec principales existentes que modificar.

## Impact

- Área de servicio prevista: `backend/app/` y `backend/tests/`.
- Contratos HTTP previstos: carga de registros, conciliación, reportes, resumen diario, disponibilidad, historial, actualización y explicación de incidencias.
- Integraciones previstas: persistencia local SQLite y servidor MCP que consume la API.
- Documentación de implementación prevista: guía local del backend y documentación funcional del servicio.
- Fuera de alcance: conexión real con proveedores, autenticación/autorización, aplicar auto-cierre a datos operativos, reapertura de incidencias resueltas y scheduler.
