# Reporte de pruebas de Wallet

- Fecha y hora local: 2026-10-16 14:15:53 -05:00
- URL principal: `http://127.0.0.1:5174/`
- Base para API y proxy: `http://127.0.0.1:5174`
- Alcance: seis comprobaciones HTTP de lectura y validación; no se enviaron datos válidos ni se solicitaron operaciones que modifiquen datos.

## Resultados

| ID | Expectativa | Resultado observado | Código HTTP | Estado |
|---|---|---|---:|---|
| WALLET-UI-01 | `GET /` devuelve `200` y HTML con el elemento raíz de la aplicación. | Respondió con HTML de la aplicación y se encontró `id="root"`. | 200 | PASS |
| WALLET-API-01 | `GET /health` devuelve `200` y `{"status":"ok"}`. | El proxy respondió `{"status":"ok"}`. | 200 | PASS |
| WALLET-API-02 | La consulta de conciliaciones para hoy (`2026-10-16`) devuelve `200`. | Respondió con una lista JSON de conciliaciones para la fecha consultada. | 200 | PASS |
| WALLET-API-03 | La consulta con fecha inválida devuelve `422`. | Respondió con error de validación de fecha. | 422 | PASS |
| WALLET-API-04 | Una ruta API inexistente devuelve `404`. | Respondió `{"detail":"Not Found"}`. | 404 | PASS |
| WALLET-API-05 | `POST /api/v1/reconciliations` con cuerpo `{}` devuelve `422` por campos requeridos ausentes. | Respondió con errores de validación por falta de `reconciliation_date` y `channel`; no se creó una conciliación. | 422 | PASS |
| WALLET-UI-01-VISUAL | Abrir la página en un navegador y comprobar que la interfaz sea visible y utilizable. | No ejecutado: no hay una herramienta de navegador disponible en esta sesión. | — | BLOQUEADO |

## Totales

- PASS: 6
- FAIL: 0
- ERROR: 0
- BLOQUEADO: 1 comprobación visual no ejecutada
- Respuestas de error esperadas aprobadas: 3 (`422` por fecha inválida, `404` por ruta inexistente y `422` por `POST` inválido).
