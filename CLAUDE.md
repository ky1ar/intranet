# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Intranet for Krear 3D — a logistics/operations platform. Two frontends (intranet SPA + registro SPA) backed by a single Flask API, all containerized with Docker.

## Common Commands

All commands run from `/var/www/intranet`.

```bash
# Dev environment
make dev-up        # Build and start all dev containers (api_dev, redis_dev, intranet_dev, registro_dev)
make dev-down      # Stop dev containers
make dev-logs      # Tail api_dev logs (last 1000 lines)
make dev-restart   # Restart only api_dev container

# Prod environment
make prod-up       # Build and start prod containers
make prod-down     # Stop prod containers
make prod-logs     # Tail api container
make prod-restart  # Restart api container

# Log archiving
make dev-save      # Save new api_dev logs since last snapshot to logs_dev/
make prod-save     # Save new api logs since last snapshot to logs/
```

The backend volume-mounts `./backend:/application`, so code changes take effect immediately without rebuilding the container.

### Switching frontend to local API

By default frontends point to `https://devapi.krear3d.com`. To target the local API, edit `api:` in `Alpine.store('cache')` inside:
- `intranet/static/js/main.js`
- `registro/static/js/main.js`

Then restart: `docker compose -f docker-compose.dev.yml restart intranet-dev registro-dev`

### Health check

```bash
curl http://localhost:5010/dev/
# {"status":"ok","env":"dev"}
```

## Architecture

### Backend (`backend/`)

Flask API using a **4-layer architecture**: `routes → controllers → services → repositories`

```
routes/       Flask Blueprints — only route definitions + auth decorators
controllers/  Request parsing, validation, delegates to services
services/     Business logic
repository/   DB queries via SQLAlchemy (uses g.db_session per request)
```

Supporting modules:
- `models.py` — legacy/shared SQLAlchemy models (Users, etc.)
- `db_models/` — feature-specific models (attendance, complaint, safebuy, etc.)
- `integrations/` — third-party API clients (Odoo, WhatsApp, couriers)
- `proxy/` — external courier proxies (Shalom, Olva, Marvisur, ApiPeru)
- `handlers.py` — decorator utilities (see below)
- `response.py` — standard `Response` class returning `{"data": ..., "success": bool}`
- `utils.py` — date/time helpers (always Peru time = UTC−5), file utilities, name formatting

**Key patterns:**

Every controller method is wrapped with `@handle_logs_and_exceptions` from `handlers.py`. This decorator logs the request/response and converts the service's `(data, status_code)` tuple into a formatted JSON response.

```python
# Controller pattern
@handle_logs_and_exceptions
def my_action(self, data):
    if validation := validate_request(data, {"required_key"}):
        return validation, 400
    return self.service.do_something(data.get("required_key"))
```

DB sessions are scoped per request via `g.db_session` (set up in `before_request`, torn down in `teardown_request`). Use `g.db_session` in repositories, never `db.session` directly. Use `@handle_db_exceptions` in repositories to auto-rollback on `SQLAlchemyError`.

Config classes in `config.py`: `Config` (main), `Redis`, `WABA`, `Odoo`, `ApisNet`, `ApiPeru`, `Shalom`, `Olva`, `Marvisur`, `Paths`. Env loaded from `backend/.env.dev` or `backend/.env.prod`.

Firebase (push notifications) initialized at startup via `serviceAccountKey.json`. Redis client available as `redis_client` imported from `application`.

### Frontends

**`intranet/`** — internal staff SPA (Alpine.js + Pinecone Router + socket.io + chart.js + zxing-browser)
**`registro/`** — external customer-facing SPA (Alpine.js + Pinecone Router + signature_pad + html2canvas + jspdf)

Both are static sites served by `nginx:alpine`. The Alpine `store('cache')` in `static/js/main.js` is the global state hub:
- `api` — base API URL
- `user` — authenticated user object (modules, level, department)
- Modal system: `showModal(key)` / `hideModal(key)` / `isVisibleModal(key)` using a `Set`
- Data cache: `fetchData(endpoints)` / `getData(key)` / `refresh(key)` — keyed endpoint cache
- Auth: `verify()` hits `/user/verify`, `logout()` clears cache

Views in `views/` are loaded by Pinecone Router; each view declares an Alpine component (e.g. `x-data="support_data"`). The JS for each view component lives alongside the view or is defined in `main.js`.

`PineToast` (defined at top of `main.js`) is a global loading indicator that auto-shows/hides on every `fetch()` call (monkey-patched). Suppress it with header `X-No-Toast: 1`.

### Docker services (dev)

| Container     | Port         | Description              |
|---------------|--------------|--------------------------|
| `api_dev`     | 5010→5010    | Flask API                |
| `redis_dev`   | 6379→6379    | Redis cache              |
| `intranet_dev`| 7010→80      | Intranet frontend        |
| `registro_dev`| 7011→80      | Registro frontend        |

Network `backend` must exist externally: `docker network create backend`

### Shared uploads

`/shared_uploads/` is mounted into both the API container and the Nginx containers (as `static/images/uploads`). File uploads go here; subfolders: `pdf/`, `picking/`, `complaint_proof/`, `qr/`, `imports/`, `safebuy/`, `leaves/`.
