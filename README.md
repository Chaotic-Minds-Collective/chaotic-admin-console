# Chaotic Unified Admin Console

React dashboard and Flask services for the ATLAS control center.

## Features

- Mobile dashboard with grid health and restart countdown
- Admin panel for authenticated start, stop, and broadcast requests
- Grid visualizer
- Browser-local, rule-based log analyzer (log text is not uploaded)

## Prerequisites

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:5343b04ed580d74b263c4928f8f3be6c401a3542e35f1b2cd09070ee41f0bed3 -->

- Python 3.10 or later
- Node.js 20 or later and npm
- The game server/RCON configuration required by your deployment
- `mcrcon`, available on the admin API process's `PATH` and executable by that process, is required for broadcasts.

<!-- /coderabbit-ai-generated:v1 -->

## Configure the backend

Set these environment variables in the backend process environment or your deployment's secret manager. Do not commit credentials or put them in the React client.

- `ADMIN_API_TOKEN`: a long, random token required for state-changing admin API calls.
- `RCON_PASSWORD`: the RCON password for the server.
- `ADMIN_UI_ORIGIN`: exact browser origin of the admin UI, for example `http://localhost:3000` during local development.
- `DASHBOARD_ORIGIN`: exact browser origin of the dashboard, typically `http://localhost:3000` during local development.

On Windows PowerShell, generate a token for the current shell with:

```powershell
$env:ADMIN_API_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set `RCON_PASSWORD` securely for the same shell or deployment; do not paste it into source files or commit it. The tracked `data/config.json` no longer contains the RCON password. Since a previous value was committed, rotate that credential before deploying this branch.

## Configure the frontend

The React build only needs the public API URLs; these are not secrets:

- `REACT_APP_API_BASE_URL`: Flask admin API URL, default `http://localhost:5000`.
- `REACT_APP_STATUS_API_URL`: grid/restart status API URL, default `http://localhost:5050`.

For production, serve the UI and both APIs over HTTPS and configure the backend origins to exactly match the UI origin. Enter the `ADMIN_API_TOKEN` in the Admin Panel; it is held in page memory and sent only with admin requests.

## Run locally

Start the admin API:

```powershell
cd server
python -m pip install flask
python app.py
```

In another terminal, start the grid-status API:

```powershell
cd server
python grid_status_api.py
```

In a third terminal, start the React client:

```powershell
cd client
npm install
npm start
```

To run the optional log monitor, configure its required log paths for your server and run `python log_monitor.py` from `server/`.

The restart countdown remains "Not scheduled" until `data/restart-time.json` contains a valid ISO 8601 UTC timestamp, for example `{"restart_time_utc":"2030-01-01T00:00:00Z"}`.
