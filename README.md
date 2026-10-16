# wallet-hackathon
W6 — Conciliación Operativa de Transacciones
1. Descripción del proyecto

Sistema de conciliación operativa para un MVP de wallet en Perú, diseñado para comparar las intenciones de pago, los resultados reportados por los proveedores y los asientos registrados en el ledger de la wallet.

El sistema permite detectar descalces financieros, identificar operaciones pendientes de investigación y generar resúmenes diarios para facilitar el seguimiento operativo y mantener la integridad financiera.

La solución utiliza servicios mock existentes para simular las fuentes de información y contempla el uso de agentes de IA y herramientas MCP (Model Context Protocol) para apoyar la consulta, el análisis y la explicación de las incidencias detectadas.

2. Historia de usuario

Como analista de operaciones,

quiero una conciliación diaria entre intenciones de pago, resultados del proveedor y asientos del ledger de wallet,

para detectar descalces tempranamente y mantener la integridad financiera del MVP.

3. Objetivos
Comparar transacciones de wallet con resultados de proveedores y registros del ledger.
Identificar diferencias de importe, registros faltantes, duplicados y operaciones pendientes.
Registrar cada descalce con una referencia, tipo y estado de investigación.
Permitir consultas por fecha y canal de proveedor.
Generar un resumen diario de operaciones conciliadas, no conciliadas y resueltas.
Incorporar agentes de IA que ayuden a investigar incidencias y explicar resultados a partir de datos verificables.
Mantener trazabilidad de las operaciones y de las acciones realizadas sobre las incidencias.
4. Alcance funcional
4.1. Fuentes de información

La solución considera tres fuentes principales:

Wallet: intenciones y registros de transacciones de la wallet.
Proveedor de pagos: resultados de procesamiento por canal, incluidos estados asíncronos.
Ledger: asientos contables o movimientos financieros registrados por la wallet.

Las fuentes se consumirán mediante los servicios mock existentes. No se presupone una conexión directa con proveedores financieros reales.

4.2. Motor de conciliación

El motor debe:

Obtener los registros de las tres fuentes.
Normalizar campos y formatos.
Relacionar registros utilizando referencias e identificadores disponibles.
Comparar importes, monedas y estados cuando corresponda.
Detectar registros ausentes o duplicados.
Diferenciar operaciones pendientes de descalces confirmados.
Registrar los resultados de cada ejecución.
Evitar duplicar incidencias al volver a procesar los mismos registros.

La lógica que determina si una operación está conciliada debe ser determinista y verificable. La IA no sustituye las reglas de conciliación.

4.3. Gestión de incidencias

Cada incidencia debe incluir, como mínimo:

Identificador de incidencia.
Referencia de transacción.
Tipo de descalce.
Fuente o fuentes involucradas.
Estado actual de investigación.
Fecha de detección.
Detalle de los valores comparados.
Evidencia que justifica la clasificación.

Los estados y las transiciones permitidas deben definirse durante la implementación.

4.4. Dashboard y reportes

El sistema debe ofrecer:

Resumen diario de conciliación.
Total de registros analizados.
Total de operaciones conciliadas.
Total de operaciones no conciliadas.
Total de incidencias resueltas.
Filtros por fecha y canal de proveedor.
Listado de incidencias y vista de detalle.
Consulta del estado actual de investigación.

Los estados deben definirse de manera que una operación pendiente no se clasifique automáticamente como un descalce confirmado. Asimismo, el reporte debe evitar contabilizar una misma operación o incidencia más de una vez.

5. Criterios de aceptación
ID	Criterio	Resultado esperado
CA-01	Comparación de fuentes	La salida diaria compara registros de wallet contra resultados de proveedor y asientos del ledger.
CA-02	Identificación de descalces	Cada descalce tiene referencia de transacción, tipo y estado actual de investigación.
CA-03	Filtros	Los reportes pueden filtrarse por fecha y canal de proveedor.
CA-04	Resumen diario	El reporte muestra totales de conciliados, no conciliados y resueltos.
Escenarios mínimos de validación
Una transacción coincide en las tres fuentes.
Existe una intención de pago sin resultado del proveedor.
El proveedor confirma un pago sin asiento correspondiente en el ledger.
El importe registrado difiere entre fuentes.
Una fuente contiene registros duplicados.
El proveedor informa una operación pendiente.
Se vuelve a ejecutar la conciliación sobre los mismos datos.
Se consulta el resumen por fecha y canal.
6. Arquitectura propuesta

La arquitectura lógica contempla los siguientes componentes:

┌───────────────────────────────┐
│       Frontend / Dashboard    │
│ Resumen · Filtros · Incidencias│
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│        API / Backend          │
│ Ejecución · Consultas · Estados│
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│    Motor de Conciliación      │
│ Reglas · Comparación · Descalces│
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│       Servicios Mock          │
│ Wallet · Proveedor · Ledger   │
└───────────────────────────────┘

        Capa de IA y herramientas

┌───────────────────────────────┐
│       Agentes de IA           │
│ Coordinación · Investigación  │
│ Resumen operativo             │
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│         Servidor MCP          │
│ Herramientas de consulta      │
│ y conciliación                │
└───────────────────────────────┘


Este diagrama representa la arquitectura propuesta; debe ajustarse a los servicios, tecnologías y contratos existentes en el repositorio.

Principios de diseño
Reutilizar los servicios mock existentes.
Mantener separadas las reglas financieras y las capacidades generativas de IA.
Definir contratos claros entre frontend, backend, agentes y herramientas.
Garantizar trazabilidad de las ejecuciones y las incidencias.
Aplicar permisos mínimos a las herramientas MCP.
Evitar que los agentes modifiquen directamente los registros financieros.
7. Agentes y herramientas MCP

La implementación de agentes se realizará de forma incremental.

Agente coordinador

Orquesta las consultas y organiza el flujo de conciliación y generación de reportes.

Agente de conciliación

Solicita los datos necesarios y utiliza el motor determinista para obtener resultados verificables.

Agente de investigación

Consulta la evidencia disponible y explica las causas posibles de una incidencia. Las conclusiones deben distinguir los hechos comprobados de las hipótesis.

Agente de reporte

Genera resúmenes diarios y responde preguntas operativas utilizando resultados de conciliación existentes.

Herramientas MCP propuestas

Los nombres son ilustrativos y deben adaptarse a los contratos reales de los servicios:

get_wallet_transactions
get_provider_results
get_ledger_entries
run_reconciliation
get_reconciliation_exceptions
get_daily_summary

Las herramientas deben validar entradas, limitar los datos accesibles y registrar las operaciones relevantes. Las herramientas de consulta deben permanecer separadas de cualquier acción que modifique estados de investigación.

8. Plan de implementación
Sprint 1 — Construcción end-to-end por slices

Objetivo: disponer de una primera conciliación funcional de extremo a extremo.

Actividades:

Configurar el entorno de desarrollo y el repositorio.
Revisar los servicios mock existentes y sus contratos.
Definir la especificación funcional y técnica mediante SDD (Spec-Driven Development).
Definir modelo de datos, arquitectura y tareas de implementación.
Diseñar las skills y los prompts iniciales.
Integrar las fuentes de wallet, proveedor y ledger.
Implementar el motor de conciliación básico.
Exponer resultados mediante la API.
Mostrar el resumen y las incidencias en el dashboard.
Preparar pruebas funcionales y una demo inicial.

Criterio de salida: una ejecución de conciliación puede completarse de principio a fin y los resultados se pueden verificar.

Sprint 2 — Funcionalidades, agentes e integraciones

Objetivo: completar el MVP y validar su comportamiento operativo.

Actividades:

Implementar los agentes especializados por función.
Levantar y configurar el servidor MCP.
Integrar los agentes con las herramientas MCP.
Completar reglas para duplicados, diferencias de importe, registros ausentes y estados asíncronos.
Implementar filtros y resumen diario.
Completar el seguimiento de incidencias.
Incorporar explicaciones y resúmenes generados por IA.
Validar permisos, manejo de errores y trazabilidad.
Ejecutar pruebas de integración y regresión.
Preparar y ensayar la demo final.

Criterio de salida: el flujo de conciliación está integrado, los casos prioritarios están cubiertos y la IA explica