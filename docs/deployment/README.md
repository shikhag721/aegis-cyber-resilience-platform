# Deployment (local / demo)

AEGIS is designed to run locally via Docker Compose - see
`docs/decisions/0005-synthetic-environment.md` for why there is no cloud
deployment target.

## Run

```bash
cp .env.example .env
# Edit .env: set a real JWT_SECRET_KEY and a Postgres password for your machine.
docker compose -f infra/docker/docker-compose.yml up --build
```

This starts three containers:

- `db` — PostgreSQL 16, with a named volume for persistence.
- `backend` — FastAPI on port 8000; seeds a demo admin user
  (`admin` / see `DEMO_ADMIN_PASSWORD` in `.env.example`) on startup, then
  runs with `--reload` for local iteration.
- `frontend` — Vite dev server on port 5173, proxying `/api` to `backend`.

## Environment variables

See `.env.example` for the full list with inline explanations. Never
commit a real `.env` file — see `SECURITY.md`.

## Stopping / resetting

```bash
docker compose -f infra/docker/docker-compose.yml down        # stop
docker compose -f infra/docker/docker-compose.yml down -v     # stop + wipe DB volume
```

## Running the backend without Docker (fast local iteration)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt
python scripts/seed_demo_data.py    # uses the default SQLite DB from app/core/config.py
uvicorn app.main:app --reload
```

This uses the SQLite fallback from `app/core/config.py` rather than
Postgres - fine for UI/API development, but run the Postgres path (via
Docker Compose, or by setting `DATABASE_URL` yourself) before considering
a change to database-specific behaviour complete.
