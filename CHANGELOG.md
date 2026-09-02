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

## Phase 6 — Application/API security + secrets detection
- Added `/app-security` route (ADR 0007) - not in the original nav list,
  since neither Vulnerability Management (CVE-based) nor Cloud Security
  (cloud config) was the right home for OWASP-style app findings or
  leaked-credential findings.
- `AppSecFinding` model: broken auth/authz, injection, insecure config,
  sensitive data exposure, missing rate limiting, session security - each
  with an OWASP reference.
- A genuine, working regex-based secret scanner
  (`app/services/secrets_scanner.py`, gitleaks/TruffleHog-style patterns:
  AWS keys, Slack tokens, PEM private key headers, generic API
  key/password assignments) - detection only, redacts every match in its
  output, never stores or reproduces a real credential.
- Seed data plants 5 OWASP-referenced app findings plus a synthetic
  "leaked config" text that is run through the real scanner at seed time
  (not hand-written records) - 3 of 4 planted fake secrets correctly
  detected and persisted with redacted snippets.
- Frontend page lets a user paste text and scan it live via the API.
- 19 new backend tests (115 total). Caught and documented a real gotcha
  during Docker verification: a Docker Desktop restart mid-build left
  stale containers serving the previous phase's image despite `--build` -
  fixed with `--no-cache` + `--force-recreate`, now documented in
  `docs/testing/README.md` as a checked step.
- A genuine DevSecOps moment: GitHub's own push protection blocked the
  first push of this phase, having detected that two of *this project's
  own* synthetic test fixtures were shaped closely enough like real Slack/
  Stripe token formats to match its live secret-scanning rules. Fixed by
  reshaping the fake values to be unambiguously non-real while still
  exercising the same detection code paths - a real external confirmation
  that credential-format detection (the same category of thing this
  phase's own scanner does) works as intended, caught before merge, not
  after.

## Phase 7 — Security monitoring + incident response
- `SecurityEvent` model and a correlation engine
  (`app/services/monitoring.py::correlate`) that flags a *sequence* of
  events per account (failed login(s) → successful login → unusual
  location/privilege escalation → database access/unusual data transfer)
  within a 24-hour window as a single, explainable finding - a single
  isolated event never triggers a finding on its own, matching how real
  detection-engineering correlation rules work.
- `Incident` model with an enforced, forward-only lifecycle (Detection →
  Triage → Investigation → Containment → Eradication → Recovery → Lessons
  Learned) - stages cannot be skipped, and every transition requires a
  substantive timeline note (validator-enforced).
- Seed data plants the exact compromise chain for `a.singh` (the same
  account already flagged in Phase 5 for missing MFA on a privileged
  account), correctly detected as a Critical correlation finding, and a
  linked incident progressed through 4 lifecycle stages with a full
  timeline.
- Frontend page shows correlated findings and incidents with an
  "Advance Stage" workflow.
- 19 new backend tests (134 total); verified end to end via Docker
  Compose with a full `--force-recreate` across all three services this
  time, confirming the stale-image lesson from Phase 6 stuck.

*(Subsequent phases appended here as completed.)*
