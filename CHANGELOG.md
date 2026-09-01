# Changelog

Phase-by-phase log, per `docs/decisions/0000-project-phasing.md`.

## Phase 0 — Repository + architecture + security baseline
- Repository scaffolding, `.gitignore`, `.env.example`.
- `README.md`, `SECURITY.md`, `CONTRIBUTING.md`.
- Initial Architecture Decision Records (backend, database, frontend,
  modular monolith, synthetic environment).
- Backend skeleton (FastAPI app factory, health endpoint, config, DB
  session wiring).
- Frontend skeleton (Vite + React + TypeScript, routing shell).
- Docker Compose (Postgres + backend + frontend).
- Initial GitHub Actions CI workflow (backend tests + lint).
- Initial pytest health-check test.

## Phase 1 — Enterprise data model + asset inventory
- `Asset` and `AssetDependency` models (11 asset types, environment,
  criticality, data classification, exposure/encryption/logging/backup flags).
- Asset service layer: create/read/update/delete, search + filter, and a
  severity-aware ordering fix (criticality is stored as a string, so a
  naive `ORDER BY` sorted "critical" last - fixed with an explicit CASE
  ranking, with a regression test).
- REST API with role-based authorization (viewer=read, risk_analyst=write,
  admin=delete) and dependency-graph endpoint for later attack-path use.
- Northstar Financial Services synthetic asset inventory (15 assets: web
  portal, API gateway, payment service, customer DB, IdP, cloud storage,
  SaaS CRM, two AI systems, endpoints, core banking server, network device,
  a deliberately low-value legacy test server, and container platform)
  with a realistic dependency chain (Internet → Web Portal → API Gateway →
  Payment Service → Customer Database), matching Section 8's example.
- Frontend Asset Inventory page: search/filter table + detail view, wired
  to the real API.
- 18 new backend tests (31 total); full Docker Compose stack rebuilt and
  re-verified end to end against real Postgres.

*(Subsequent phases appended here as completed.)*
