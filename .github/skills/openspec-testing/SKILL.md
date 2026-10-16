---
name: openspec-testing
description: "Prueba la interfaz Wallet en http://127.0.0.1:5174/ y verifica sus respuestas HTTP, carga en navegador cuando esté disponible y API de conciliación mediante el proxy."
---

# Pruebas de Wallet y API de conciliación

## Objetivo

Probar como objetivo principal la aplicación Wallet en
`http://127.0.0.1:5174/`. Verificar que la página responde y, cuando haya un
navegador disponible, que la interfaz se carga. Complementar la prueba con
comprobaciones de salud y de la API de conciliación a través del proxy del
frontend.

## Reglas de seguridad

- Usa exactamente `http://127.0.0.1:5174/` como página objetivo y
  `http://127.0.0.1:5174` como base para las rutas de API.
- Ejecuta las peticiones HTTP `GET` de lectura y `POST` de validación indicadas
  en los casos básicos. Para `POST`, usa únicamente el cuerpo inválido definido
  abajo y confirma que la respuesta sea `422`; no crees conciliaciones, cargues
  registros ni cambies estados durante estas pruebas básicas.
- No envíes cuerpos válidos a rutas `POST` ni repitas solicitudes que puedan
  escribir datos. Si una petición `POST` devuelve una respuesta de éxito,
  regístrala como `FAIL` e indica el código observado; no la repitas.
- No inventes resultados: cada caso pasa solo si el código HTTP y las
  comprobaciones de respuesta coinciden con lo esperado.
- Distingue un error esperado (por ejemplo, `404` o `422` esperado) de un fallo
  de prueba. Un error de conexión no cuenta como error funcional esperado: es
  un fallo o bloqueo del entorno.
- No incluyas tokens, credenciales ni datos sensibles en el reporte.

## Casos básicos por defecto

1. **WALLET-UI-01 — Página principal disponible:** `GET /` devuelve `200` y
   contiene el documento HTML de la aplicación. Si hay un navegador disponible,
   abre `http://127.0.0.1:5174/` y comprueba que la interfaz se muestra sin un
   error visible que impida su uso. Registra por separado si no fue posible
   hacer la comprobación en navegador.
2. **WALLET-API-01 — Salud del backend vía proxy:** `GET /health` devuelve
   `200` con `{"status":"ok"}`.
3. **WALLET-API-02 — Consulta válida:** consultar
   `/api/v1/reconciliations` con la fecha de hoy devuelve `200`.
4. **WALLET-API-03 — Fecha inválida:** la misma consulta con una fecha inválida
   devuelve `422`.
5. **WALLET-API-04 — Ruta inexistente:** una ruta API inexistente devuelve
   `404`.
6. **WALLET-API-05 — POST sin datos válidos:** enviar
   `POST /api/v1/reconciliations` con `Content-Type: application/json` y cuerpo
   `{}` devuelve `422` por campos requeridos ausentes. Este caso comprueba el
   método `POST` sin crear una conciliación ni modificar datos.

Los casos de error son exitosos cuando la API devuelve el error esperado. Por
ejemplo, recibir `422` para la fecha inválida o para el `POST` inválido es
`PASS`; recibir un código de éxito en cualquiera de esos casos es `FAIL`.

## Procedimiento

1. Prueba primero `GET http://127.0.0.1:5174/`. Si no responde, registra el
   fallo o bloqueo de conexión; no lo presentes como un fallo funcional del
   backend.
2. Cuando haya navegador disponible, abre la página y comprueba que la interfaz
   sea visible y utilizable. No marques esta verificación como aprobada si no
   pudiste observarla.
3. Ejecuta los casos de API mediante el frontend como base para comprobar el
   proxy: usa `GET` para las consultas de lectura y el `POST` inválido indicado
   para comprobar validación sin persistir datos.
4. En el caso `POST`, envía exactamente `{}` como cuerpo JSON; no lo sustituyas
   por un cuerpo válido ni uses otra ruta de escritura.
5. Comprueba el código HTTP esperado y, cuando el caso lo defina, el cuerpo
   JSON o contenido de texto esperado.
6. Clasifica cada caso como `PASS`, `FAIL`, `ERROR` o `BLOQUEADO`.
7. Reporta solo los resultados observados. No afirmes que se ejecutaron casos
   que no se pudieron enviar.

## Informe

Para cada caso incluye ID, expectativa, resultado observado, código HTTP y
estado. Cierra con totales de casos aprobados, fallidos, errores esperados
aprobados y bloqueados. Si hay fallo de conexión, indica qué URL y servicio no
respondió sin confundirlo con un error funcional de la API.
