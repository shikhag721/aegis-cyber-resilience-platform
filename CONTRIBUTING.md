# Contributing / Codebase Guide

This is a personal portfolio project, but organized as if a small team
would work on it — mainly so it's easy to navigate and extend.

## Layout

```
backend/
  app/
    main.py           FastAPI app factory, router mounting, middleware
    core/              config, security (JWT/hashing), logging
    db/                SQLAlchemy session/engine, Alembic env
    models/            SQLAlchemy ORM models, one file per domain
    schemas/           Pydantic request/response schemas, one file per domain
    api/v1/            FastAPI routers, one file per domain
    services/          Business logic per domain (routers stay thin)
    risk_engine/        Pure-Python risk scoring - no DB/HTTP imports
  alembic/             Migration scripts
  tests/               pytest suite, mirrors app/ structure
frontend/
  src/
    pages/             One folder per route/module
    components/        Shared UI (tables, risk badges, cards)
    api/               Typed API client
docs/                  Architecture, ADRs, methodology, per-module docs
infra/docker/          Dockerfiles + docker-compose.yml
.github/workflows/     CI (tests, lint, SAST, dependency/secret scan)
```

## Adding a new domain module (example: "widgets")

1. `backend/app/models/widgets.py` — SQLAlchemy model(s).
2. `backend/app/schemas/widgets.py` — Pydantic create/read/update schemas.
3. `backend/app/services/widgets.py` — business logic (calls risk_engine if relevant).
4. `backend/app/api/v1/widgets.py` — FastAPI router; mount in `main.py`.
5. `backend/tests/test_widgets_api.py` + a service/unit test.
6. `frontend/src/pages/Widgets/` — list + detail views, added to the nav.
7. Document it: what problem it solves, what risk/control concept it
   demonstrates, and its limitations — see any existing `docs/` module doc
   as a template.

## Commit conventions

Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`,
`security:`, `ci:`, `chore:`. One logical change per commit; no
"final"/"done"/"all code" commits.

## Before pushing

- `pytest` (backend) passes.
- No new files matching `.env`, `*.pem`, `*.key` are staged.
- `git status` reviewed — no unexpected generated files.
