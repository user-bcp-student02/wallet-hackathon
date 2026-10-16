# SDD: Conciliacion operativa de transacciones

Paquete de especificacion para la conciliacion diaria de transacciones de wallet,
resultados de proveedores de pago y asientos del ledger.

## Artefactos

- [Propuesta](./proposal.md): problema, objetivo, alcance, riesgos y supuestos.
- [Especificacion](./spec.md): requisitos funcionales y escenarios verificables.
- [Diseno tecnico](./design.md): arquitectura logica, modelo, reglas y contratos candidatos.
- [Plan de trabajo](./tasks.md): slices de implementacion y estrategia de pruebas.

## Estado y limites

Este paquete es una propuesta para revision; no representa una implementacion ni
confirma contratos tecnicos existentes. El repositorio disponible contiene
documentacion de producto, pero no el codigo de los servicios mock ni sus
contratos. Antes de cerrar el diseno tecnico, deben inspeccionarse esos servicios
y resolverse las preguntas abiertas registradas en los artefactos.

El diseno mantiene la conciliacion financiera determinista. Agentes de IA y MCP
se consideran una extension posterior y no pueden decidir resultados
financieros ni modificar datos de origen.
