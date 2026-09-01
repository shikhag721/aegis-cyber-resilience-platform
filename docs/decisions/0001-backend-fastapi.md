# ADR 0001: Backend framework — FastAPI

## Status
Accepted

## Context
The backend needs to serve a documented REST API for ~20 domain areas
(assets, risk, controls, IAM, AI security, etc.) with strong input
validation, auth, and automatic API documentation for reviewers.

## Decision
Use Python + FastAPI.

## Why
- Pydantic-based request/response validation gives free, strict input
  validation at every API boundary — directly supports the "no unvalidated
  input" application-security requirement (see `SECURITY.md`).
- Automatic OpenAPI/Swagger docs (`/docs`) let a reviewer explore every
  endpoint without reading source first.
- Async-capable, but the project does not need to over-engineer around
  async — most endpoints are simple CRUD/query operations over Postgres.
- Same language (Python) as the risk engine and any future AI/RAG
  components, avoiding a second runtime for the API layer.

## Alternatives considered
- **Django REST Framework**: heavier, more opinionated ORM/admin tooling
  not needed here; FastAPI's explicit dependency-injection style makes
  authorization checks easier to test in isolation.
- **Node/Express**: would split the stack across two languages (JS for
  API, Python for risk engine/AI) for no clear benefit.

## Consequences
Modular router-per-domain structure required to avoid a monolithic
`main.py` — enforced via `backend/app/api/v1/<domain>.py` files, each
mounted in `backend/app/main.py`.
