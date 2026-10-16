# wallet-hackathon
W6 — Conciliación Operativa de Transacciones
1. Descripción del proyecto

Sistema de conciliación operativa para un MVP de wallet en Perú, diseñado para comparar las intenciones de pago, los resultados reportados por los proveedores y los asientos registrados en el ledger de la wallet.

El sistema permite detectar descalces financieros, identificar operaciones pendientes de investigación y generar resúmenes diarios para facilitar el seguimiento operativo y mantener la integridad financiera.

La solución utiliza servicios mock existentes para simular las fuentes de información y contempla el uso de agentes de IA y herramientas MCP (Model Context Protocol) para apoyar la consulta, el análisis y la explicación de las incidencias detectadas.

## Preparar el backend local en Windows

Desde la raíz del repositorio, crea y activa el entorno virtual e instala las
dependencias del backend:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

La instalación incluye `tzdata` en Windows, necesaria para que Python encuentre
la zona `America/Lima` usada al inicializar los datos sintéticos. Si el entorno
virtual ya existía, vuelve a ejecutar `python -m pip install -e ".[dev]"` con
el entorno activado para instalar la dependencia. Consulta el
[README del backend](./backend/README.md) para más opciones de configuración.

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

El backend actual recibe lotes de registros ya normalizados mediante su API. Para
desarrollo, genera datos sintéticos locales de wallet, proveedor y ledger para los
cinco días anteriores; no consulta automáticamente servicios mock externos ni
proveedores financieros reales.

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
Total de transacciones resueltas y, por separado, incidencias resueltas.
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
7. Agente y herramientas MCP locales

El agente **Wallet Reconciliation Operator** se invoca manualmente en VS Code.
Recibe fechas explícitas (puede resolver “ayer” usando `America/Lima`), consulta
los datos disponibles y solicita al backend determinista las corridas pedidas.
No hay scheduler ni ejecución automática al iniciar la API.

El servidor MCP local `wallet-reconciliation` se comunica con la API local y
expone herramientas acotadas:

- `list_available_reconciliation_data`: consulta conteos por fecha/canal/fuente
  y si ya existe una corrida.
- `run_reconciliation`: ejecuta solo si hay datos; ante una corrida existente
  devuelve el reporte existente, sin intentar duplicarla.
- `get_reconciliation_report`: consulta una corrida sin crearla.
- `get_daily_reconciliation_summary`: consulta el resumen diario, con conteos
  de transacciones e incidencias resueltas separados.

El MCP no carga datos fuente ni cambia estados de investigación y no tiene
acceso de escritura a wallet, proveedor o ledger. Los datos sembrados son
sintéticos. Las instrucciones operativas reutilizables están en
`.github/skills/wallet-reconciliation-operations/SKILL.md`.

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

[x] Configurar un agente operativo manual y su skill de ejecución.
[x] Levantar el servidor MCP local e integrar las herramientas acotadas de conciliación.
[x] Completar reglas para duplicados, diferencias de importe, registros ausentes y estados de proveedor.
[x] Implementar filtros, resumen diario y seguimiento de incidencias.
[x] Validar límites de operación, errores explícitos y no duplicación de corridas.
[x] Ejecutar pruebas backend y build/type-check del frontend.
[ ] Incorporar explicaciones generadas por IA y ensayar la demo final.

Criterio de salida alcanzado para esta iteración: una persona puede consultar
disponibilidad y solicitar manualmente una conciliación de punta a punta usando
el agente MCP; la API conserva la autoridad sobre resultados y validaciones.
Las explicaciones generadas por IA y cualquier scheduler siguen fuera de alcance.
