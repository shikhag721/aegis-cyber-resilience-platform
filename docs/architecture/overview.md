# Architecture Overview

## Component diagram

```text
                     ┌─────────────────────────┐
                     │   React (Vite) SPA       │
                     │   frontend/src/pages/*    │
                     └────────────┬─────────────┘
                                  │  REST + JWT bearer token
                                  ▼
                     ┌─────────────────────────┐
                     │   FastAPI backend        │
                     │   app/api/v1/*.py routers│
                     │   app/services/*.py       │
                     └────────────┬─────────────┘
                                  │  SQLAlchemy ORM
                                  ▼
                     ┌─────────────────────────┐
                     │   PostgreSQL             │
                     │   (Docker Compose: db)   │
                     └─────────────────────────┘

              ┌───────────────────────────────────┐
              │   app/risk_engine/ (pure Python)   │
              │   No FastAPI or SQLAlchemy imports  │
              │   Imported BY services, not the      │
              │   other way around - see ADR 0004   │
              └───────────────────────────────────┘
```

## Request flow (example: viewing the risk register)

1. Browser sends `GET /api/v1/risks` with `Authorization: Bearer <jwt>`.
2. `app/core/deps.py::get_current_user` decodes and validates the JWT,
   loads the `User` row, and rejects the request (401) if invalid/expired.
3. The router's `require_role(...)` dependency checks the user's role is
   authorized for this endpoint (403 if not).
4. The router calls `app/services/risk.py`, which queries SQLAlchemy models
   and, where a risk needs (re)scoring, calls into `app/risk_engine/` with
   plain Python inputs (never an ORM object directly) and gets back a
   plain, explainable result object.
5. The service maps ORM rows + risk engine results to a Pydantic response
   schema; FastAPI serializes it to JSON.

## Security boundaries

- The frontend never talks to PostgreSQL directly - only via the backend's
  authenticated REST API.
- The risk engine never makes a network or database call - it is a pure
  function boundary, which is also why it can be unit tested without any
  infrastructure running at all.
- The only process with a database credential is the backend container
  (via `DATABASE_URL`); the frontend container has no database credential
  and no direct network path to `db` in `docker-compose.yml` beyond what
  Docker's default bridge network allows (documented as a hardening item
  for network segmentation in `docs/architecture/limitations.md`).

## Data flow: audit-relevant state changes

```text
User action (e.g. change risk status)
  → API request, authorization-checked
  → Service layer applies the change
  → Audit log entry written in the SAME transaction (actor, action,
    object, old value, new value, timestamp)
  → Commit
```

Writing the audit entry in the same transaction as the change it describes
is deliberate: it prevents a state change from ever being persisted
without a corresponding audit record (see `docs/architecture/audit-log.md`,
added in Phase 8 alongside the control-assessment module).

## See also

- `docs/decisions/` — why each major technology/pattern was chosen.
- `docs/architecture/limitations.md` — what is intentionally simplified.
- `docs/architecture/references.md` — external frameworks referenced and how.
