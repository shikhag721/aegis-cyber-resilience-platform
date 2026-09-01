# Security

## What AEGIS is

AEGIS is a **defensive, educational portfolio project**: a simulated enterprise
cyber-resilience and AI-security risk platform built around a fictional
organization (Northstar Financial Services) with entirely synthetic data.
It is not a production security product and holds no real customer,
employee, or infrastructure data.

## Safety boundary

This project does not and will not contain:

- malware, exploit code, or credential-theft tooling
- persistence mechanisms
- phishing infrastructure usable against real targets
- automation that attacks or scans real external systems
- real secrets, credentials, or personal data of any kind

All "attack path," "vulnerability," and "incident" content is either
descriptive/simulated data or runs against intentionally local, isolated
test fixtures. See `docs/threat-models/` for how offensive concepts are
represented defensively (root-cause classification, detection, and
remediation - not exploitation).

## Secret handling

- Real secrets are never committed. `.env` is gitignored; only
  `.env.example` (placeholder values) is tracked.
- CI includes a secret-scanning step (see `.github/workflows/`) intended to
  catch accidental commits before merge.
- Passwords are hashed (bcrypt via passlib/argon2, see
  `backend/app/core/security.py`); JWT signing keys are read from
  environment variables only.
- If you fork this repo, generate your own `JWT_SECRET_KEY` and database
  credentials - never reuse the example values beyond local development.

## Application security controls (this codebase)

Documented in detail in `docs/architecture/` and enforced by
`backend/app/tests/`:

- Authentication via hashed passwords + JWT, no plaintext credential storage.
- Role-based authorization checked at the API layer, tested for both
  expected-success and expected-failure (403/401) cases.
- SQLAlchemy ORM with parameterized queries only - no raw string-interpolated SQL.
- Input validation via Pydantic schemas on every API boundary.
- CORS restricted to configured origins; security headers set on all responses.
- An append-only audit log for state-changing governance actions (risk
  status changes, control status changes, evidence changes) - see
  `docs/architecture/audit-log.md`.
- Dependency and static-analysis scanning in CI (Bandit, pip-audit/Trivy,
  and a secret scan) - see `.github/workflows/`.

## Reporting a concern

This is a personal portfolio project without a formal security response
SLA. If you find a real vulnerability in this code (not a documented,
intentional simulation), please open a GitHub issue describing it.

## Known, accepted limitations

See `docs/architecture/` and each module's own documentation for a full
list, but in short: this is a local/demo-oriented system (SQLite-compatible
test mode, Docker Compose for local Postgres), not hardened for
multi-tenant production deployment, and does not integrate with real
cloud provider APIs, a real SIEM, or real EDR/identity systems - those are
modeled as structured, explainable data rather than live integrations.
