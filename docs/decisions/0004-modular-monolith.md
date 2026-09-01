# ADR 0004: Modular monolith, not microservices

## Status
Accepted

## Context
The brief covers ~20 domains. It would be possible to split each into a
separate service, but that adds real operational complexity (service
discovery, inter-service auth, distributed tracing) with no corresponding
benefit for a single-operator portfolio project and no real production
load to justify independent scaling.

## Decision
Build a single FastAPI backend, organized as a **modular monolith**: one
process, but strict internal module boundaries — one router + one service
module + one set of SQLAlchemy models per domain
(`backend/app/api/v1/<domain>.py`, `backend/app/services/<domain>.py`,
`backend/app/models/<domain>.py`), all composed in `backend/app/main.py`.
The risk engine (`backend/app/risk_engine/`) is kept fully decoupled from
the web layer — it takes plain data in, returns plain data out, with no
FastAPI or SQLAlchemy imports.

## Why
This directly answers the brief's Section 50 ("No Fake Complexity"):
Kubernetes/microservices here would be "complex → impressive-looking →
poorly understood," not "simple → correct → explainable → tested →
secure." A modular monolith gives real separation of concerns (each domain
is independently testable and reviewable) without the operational
overhead a real microservices deployment would require to run and explain
correctly in an interview.

## Consequences
- One Docker image for the backend, one for the frontend, one Postgres
  container — three services in `infra/docker/docker-compose.yml`, not
  twenty.
- If a specific module (e.g. the RAG security simulator) later needed
  independent scaling in a hypothetical production version, the module
  boundary already exists to extract it — documented as a "what I'd
  change for production" item, not built now.
