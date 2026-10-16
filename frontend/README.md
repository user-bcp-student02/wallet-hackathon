# Wallet reconciliation frontend

React + TypeScript + Vite UI for the FastAPI reconciliation backend.

## Levantar el frontend en local

Desde la raíz del repositorio, abre una terminal para el frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abre la URL que muestra Vite, normalmente `http://127.0.0.1:5173`. Para que los datos
se carguen, el backend debe estar disponible en `http://127.0.0.1:8000`. El proxy de
Vite reenvía `/api` y `/health` al backend; no necesitas configurar CORS para el
desarrollo local.

Después de instalar las dependencias una vez, para los siguientes inicios basta con
ejecutar `npm run dev` desde `frontend/`. Detén el frontend con `Ctrl+C` en su
terminal.

## Features

- Daily summary and reconciliation reports, filterable by date and channel.
- Start a reconciliation run for a selected date and channel.
- Review discrepancy references, types, details, and status; mark findings in
  progress or resolve them with an investigation note.
- Load normalized JSON batches for wallet, provider, and ledger sources.
- API connectivity indicator and visible backend errors.

The API base and proxy target are set in `vite.config.ts` for local development.
