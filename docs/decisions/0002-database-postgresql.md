# ADR 0002: Database — PostgreSQL

## Status
Accepted

## Context
The data model is genuinely relational (assets ↔ vulnerabilities ↔ risks
↔ controls ↔ evidence, vendors ↔ assessments, AI systems ↔ AI risks, etc.)
with real referential-integrity requirements, and the platform is framed
as an "enterprise" system rather than a single-user local demo.

## Decision
Use PostgreSQL as the primary database, run via Docker Compose for local
development, accessed through SQLAlchemy ORM models with Alembic for
schema migrations.

## Why
- Proper foreign-key constraints and transactions matter here — an
  inconsistent risk register or a control pointing at a deleted asset
  would undermine the entire premise of an evidence-based GRC tool.
- JSONB support is useful for semi-structured fields (e.g. contributing
  risk factors, threat model data-flow diagrams) without needing a
  separate document store.
- Widely used in real enterprise environments, unlike SQLite, which better
  fits the "does this look like an enterprise platform" bar this project
  is held to (see `README.md` "Final Portfolio Standard").

## Consequences / trade-off
- Requires Docker (or a local Postgres install) to run the full stack —
  documented in `docs/deployment/`.
- Test strategy (see `docs/testing/`): the risk engine itself has zero
  database dependency and is unit-tested with plain Python objects. API/
  integration tests run against a real Postgres instance (via
  docker-compose test profile / CI service container) rather than SQLite,
  specifically so JSONB and constraint behaviour are tested faithfully —
  the earlier AI Governance portfolio project used a SQLite+brute-force
  approach for a smaller local tool; AEGIS intentionally does not repeat
  that simplification given its stated enterprise-platform positioning.
