# AEGIS — Enterprise Cyber Resilience & AI Security Risk Platform

A portfolio-grade cybersecurity platform simulating the security and AI-risk
program of a fictional financial services company, **Northstar Financial
Services** (~500 employees). AEGIS connects technical security findings to
business risk end to end:

```
Technical Security → Threats → Vulnerabilities → Business Impact →
Controls → Risk → Remediation → Governance → AI Security
```

## Why this project exists

Built while developing toward **Cyber GRC → Technology Risk → AI Risk →
AI Governance / AI Assurance**. AEGIS is deliberately *not* a pentesting or
exploit-development project — it demonstrates enough technical depth
(identity, network, cloud, application, and AI security concepts) to
understand and challenge engineering explanations, while the core skill
being demonstrated is **connecting technical findings to explainable,
business-relevant risk**.

## Important disclaimer

Northstar Financial Services is entirely fictional; every dataset in this
repository is synthetic. AEGIS is not a production security product, not a
compliance certification, not a penetration test, and does not claim
endorsement by NIST, OWASP, CIS, MITRE, or any other named framework body.
Framework references are described as "mapped to" / "aligned with" an
assessment reference — never as proof of legal or regulatory compliance.
See `docs/decisions/` for the reasoning behind every major scope decision
and `docs/architecture/limitations.md` for an explicit list of what this
project does not do.

## What's inside

| Module | What it does |
|---|---|
| Asset Inventory | Enterprise asset register with criticality, exposure, and data classification |
| Threat Modeling & Attack Paths | Asset/trust-boundary/data-flow modeling with MITRE ATT&CK-referenced attack paths |
| Risk Engine | Centralized, explainable inherent/residual risk scoring - not scattered across the app |
| Vulnerability Management | CVE/CVSS tracking with technical severity vs. business risk explicitly separated |
| IAM Risk | Privileged/orphan/inactive account and access-risk detection |
| Cloud Security Posture | Modeled cloud configuration findings (IAM, storage, network, secrets) |
| Application/API Security | OWASP-referenced findings against local synthetic test scenarios |
| Security Monitoring & Incident Simulation | Correlated synthetic security events, not a real SIEM |
| Incident Response | Full lifecycle (Detection → Lessons Learned) for simulated incidents |
| GRC / Control Assessment | Risk → Control → Evidence → Test → Finding → Remediation, with design vs. operating effectiveness |
| Evidence Management | Evidence records with owner, validity date, and status |
| Third-Party / Vendor Risk | Vendor risk scoring and findings |
| Data Security | Classification (Public → Highly Restricted) and category-based exposure assessment |
| Business Continuity & DR | RTO/RPO and recovery-dependency scenarios |
| AI Inventory & AI Security | AI system register plus Model/Application/Data/Identity/Infrastructure/Tool/Third-Party/Governance risk lenses |
| RAG Security | Simulated RAG pipeline with authorization-failure vs. prompt-injection root-cause classification |
| AI Agent Security | Agent identity/permissions/tools/blast-radius assessment |
| AI Governance | Inventory → Classification → Risk → Control → Evidence → Approval → Monitoring lifecycle |
| Executive Dashboard & Reports | Drill-down from executive risk to technical finding to evidence |
| Audit Log | Append-only record of every governance-relevant state change |

## Architecture at a glance

- **Frontend**: React (Vite) SPA — see `docs/decisions/` for why.
- **Backend**: Python, FastAPI, modular routers/services (no single giant file).
- **Database**: PostgreSQL via SQLAlchemy + Alembic migrations.
- **Risk engine**: isolated, dependency-free Python module — pure functions,
  no DB or network calls, fully unit-testable (`backend/app/risk_engine/`).
- **Containerization**: Docker + Docker Compose for local `db` + `backend`
  + `frontend`.
- **CI/CD**: GitHub Actions — tests, lint, dependency/secret/SAST scanning
  on every push and PR (see `.github/workflows/`).

Full diagrams and data flow in `docs/architecture/`.

## Quick start

```bash
cp .env.example .env          # edit JWT_SECRET_KEY / DB password for local use
docker compose -f infra/docker/docker-compose.yml up --build
```

- Backend API: http://localhost:8000/docs (OpenAPI/Swagger)
- Frontend: http://localhost:5173
- Seeded demo login and Northstar Financial Services sample data load
  automatically on first backend startup — see `docs/deployment/`.

Run backend tests:

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Documentation index

| Document | Covers |
|---|---|
| `docs/architecture/` | System design, data flow, security boundaries, ADR index |
| `docs/decisions/` | Architecture Decision Records for every major choice |
| `docs/threat-models/` | Asset → threat → attack-path → impact → control models |
| `docs/risk-methodology/` | Risk engine methodology, likelihood/impact/control-effectiveness |
| `docs/control-assessment/` | Control assessment workflow and design vs. operating effectiveness |
| `docs/ai-security/` | AI/RAG/agent security model and AI governance workflow |
| `docs/testing/` | Test strategy and how to run the suite |
| `docs/deployment/` | Docker Compose usage, environment variables, seeding |
| `SECURITY.md` | Security posture of the app itself, safety boundary, reporting |
| `CONTRIBUTING.md` | How the codebase is organized and how to extend it |
| `CHANGELOG.md` | Notable changes by phase |

## Status

This repository is under active, phased build (see `docs/decisions/0000-project-phasing.md`).
Each phase is tested, documented, and pushed before the next begins — see
the commit history for progress, and `CHANGELOG.md` for a phase-by-phase
summary.

## License

MIT — see `LICENSE`. Framework references (NIST, OWASP, MITRE, CIS, ISO)
remain the property of their respective publishers; see
`docs/architecture/references.md`.
