# SDD: Conciliación operativa de transacciones

Este paquete documenta la **implementación actual** del MVP de conciliación
operativa desarrollada en:

- [backend/](../../../backend/)
- [frontend/](../../../frontend/)

## Artefactos

- [Propuesta](./proposal.md): objetivo de negocio y alcance realmente entregado.
- [Especificación](./spec.md): comportamiento funcional observado en API y UI.
- [Diseño técnico](./design.md): arquitectura, modelo de datos y reglas implementadas.
- [Plan de trabajo](./tasks.md): trazabilidad de lo completado y backlog siguiente.

## Estado actual del SDD

El SDD ya no describe solo una propuesta: refleja el estado del código vigente
en [backend/app/](../../../backend/app/) y [frontend/src/](../../../frontend/src/).

### Implementado en el MVP

- Carga de lotes normalizados para wallet, provider y ledger.
- Corridas de conciliación por `fecha + canal` con restricción de unicidad.
- Detección de descalces por faltantes, duplicados, diferencias de canal/monto/moneda
  y estado de proveedor no exitoso.
- Consulta de reportes por fecha/canal y resumen diario agregado.
- Gestión de investigación de descalces (`OPEN`, `IN_PROGRESS`, `RESOLVED`) con nota.
- Dashboard React para ejecutar corridas, revisar métricas y resolver descalces.

### Fuera de alcance actual

- Integración directa con proveedores externos reales.
- SLA temporal para diferenciar pendientes vs ausencias definitivas.
- Reapertura de descalces resueltos.
- Autenticación/autorización por roles y auditoría avanzada.
