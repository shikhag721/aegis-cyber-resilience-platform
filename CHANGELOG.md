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

## Phase 2 — Threat modeling + attack paths
- `ThreatActor`, `Threat` (with MITRE ATT&CK mapping + an enforced
  `why_relevant` field - a validator rejects vague/generic justifications),
  `AttackPath`/`AttackPathStep` models.
- Attack paths scored by likelihood × impact (same 1-25 scale the Phase 3
  risk engine will use), sorted highest-first.
- Northstar threat model: 3 threat actors, 6 threats with specific
  asset-tied justifications, 3 attack paths - including the Section 8
  worked example (credential compromise → API → payment service →
  customer database) plus an insider path and a third-party/vendor path.
- `docs/threat-models/northstar-threat-model.md` narrative + trust-boundary
  diagram.
- Frontend Threat Modeling and Attack Paths pages (expandable step detail,
  score badges) wired to the real API.
- 10 new backend tests (41 total); re-verified end to end via Docker
  Compose against real Postgres, including idempotent re-seeding.

## Phase 3 — Risk engine
- `app/risk_engine/`: pure, dependency-free (no FastAPI/SQLAlchemy imports)
  likelihood × impact scoring, capped-and-summed explainable factors,
  inherent vs. residual risk (control-effectiveness reduction), risk
  appetite, and a treatment suggestion (Accept/Mitigate/Transfer/Avoid) -
  always decision support, never auto-applied.
- Verified the Section 9 CVSS-vs-business-risk principle as an executable
  test AND live in seeded data: a Critical-severity, known-exploited
  finding on the isolated legacy test server (AST-014) scores lower
  (residual: Low) than a Medium-severity finding on customer-facing
  infrastructure (residual: High).
- `RiskRecord` model/service/API: persists engine assessments against an
  asset (snapshotting asset criticality/classification/exposure so
  history stays meaningful), plus a human-entered treatment decision
  requiring a substantive reason (validator enforced).
- 5 Northstar risk register entries seeded, two with recorded treatment
  decisions (one Mitigate in progress, one Accept/closed).
- `docs/risk-methodology/README.md` full write-up.
- Frontend Risk Register page: list with contributing-factor drill-down,
  plus a working "New Risk Assessment" intake form.
- 24 new backend tests (65 total); re-verified end to end via Docker
  Compose against real Postgres.

## Phase 4 — Vulnerability management
- `Vulnerability` model (CVE, CVSS, known-exploited flag, compensating
  controls, remediation status/owner/due date) with a single, explicit
  `cvss_to_severity_band()` translation point - the risk engine never sees
  a raw CVSS number, only the resulting band, keeping technical severity
  and business risk visibly distinct.
- `assess_vulnerability` bridges to the Phase 3 risk engine using the
  affected asset's real context, linking the resulting `RiskRecord` back
  onto the vulnerability.
- Seeded with real, publicly known CVE numbers (Log4Shell-class, xz
  backdoor-class, libwebp-class) applied to fictional Northstar assets:
  Log4Shell (CVSS 10.0, known-exploited) on the isolated legacy test
  server assesses to **residual risk 4 (Low)**, while a CVSS 8.8 finding
  on the internet-facing Customer Web Portal assesses to **residual risk
  18 (Critical)** - the Section 9 principle, live in real seeded data,
  not just a unit test.
- Frontend Vulnerability Management page: CVSS vs. business-risk shown
  side by side, with a one-click "Assess Business Risk" action.
- 11 new backend tests (76 total); re-verified end to end via Docker
  Compose against real Postgres.

## Phase 5 — IAM risk + cloud security posture
- `IdentityAccount` model + deterministic IAM finding engine detecting:
  orphan accounts (terminated but still enabled), missing MFA on
  privileged access, inactive accounts (90+ day threshold), inappropriate
  production access by department, segregation-of-duties conflicts (toxic
  permission pairs), and privilege-escalation paths (privileged service
  account + production access + no MFA). Fixed a real SQLite/Postgres
  cross-database datetime bug caught by the test suite (naive vs.
  timezone-aware comparison).
- `CloudFinding` model (structured findings, not a live cloud API
  integration - see ADR 0005): public exposure, overly permissive IAM,
  unencrypted data, missing logging, open security groups, config drift,
  exposed secrets.
- Northstar seed data plants one example of every IAM finding type plus 5
  cloud findings across 5 finding types - all correctly detected by the
  engine.
- Frontend IAM Risk and Cloud Security pages wired to the real API.
- 20 new backend tests (96 total); re-verified end to end via Docker
  Compose against real Postgres.

*(Subsequent phases appended here as completed.)*
