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

## Phase 8 — GRC controls, evidence, and audit log
- `Control`/`ControlAssessment` model separating **design effectiveness**
  from **operating effectiveness** - a control assessed as well-designed
  but not operating (or vice versa) surfaces as "Partially Effective," not
  silently rounded to either extreme. `overall_status` is the conservative
  combination of both, never a restatement of one.
- `Evidence` model tied to a control assessment, with expiry tracking
  (`refresh_expired_status` flips past-due evidence from Valid to Expired
  automatically).
- `analyze_control_gaps`: flags ineffective/partially-effective/
  not-assessed controls, missing evidence, expired evidence, and overdue
  reviews - deterministic, computed, not stored.
- Append-only-style `AuditLogEntry` (Section 32) with a single `record()`
  entry point, retrofitted into the three most GRC-relevant state changes
  already built: control effectiveness updates, risk treatment updates,
  and incident stage advances - each logs actor, old value, new value, and
  reason only when the status actually changes.
- Northstar seed data plants a realistic spread: one Ineffective control
  (tied narratively to the already-seeded Log4Shell risk-acceptance), one
  Partially Effective, one Not Assessed, one with expired evidence, one
  overdue for review.
- Verified on a **fully fresh Docker volume** (not just an incrementally
  reused one) that the seed process itself populates 5 real audit entries
  out of the box - confirming the audit trail isn't only visible after
  manual interaction.
- Frontend Control Assessment, Evidence Register, and Audit Log pages.
- 23 new backend tests (157 total).

## Phase 9 — Third-party/vendor risk, data security, business continuity
- `Vendor`/`VendorAssessment` with its own deterministic, explainable
  scorer (ADR 0008: NOT a forced reuse of `app/risk_engine/` - vendor
  factors like subprocessors, certifications, and contract terms don't
  map cleanly onto asset-based likelihood/impact, so this follows the same
  design pattern with domain-appropriate inputs instead).
- `DataAsset` catalog (Section 21): where specific sensitive data
  categories (PII, financial, credentials, secrets, business, AI data)
  actually live, independent of an asset's general classification tier -
  one asset can hold several categories with different exposure profiles.
- `ContinuityPlan` (Section 22): RTO/RPO, backup/DR test currency,
  recovery dependencies, with staleness thresholds scaled to asset
  criticality.
- Northstar seed data: 3 vendors (one well-governed, one poorly-governed
  with real incident history, one strong-baseline), 5 data assets, 4
  continuity plans - producing real findings (2 data-security, 6
  continuity) on a fresh clone, not just clean data.
- Frontend Vendors, Data Security, and Business Continuity pages.
- 17 new backend tests (174 total); verified end to end via Docker
  Compose with a full force-recreate.

## Phase 10 — AI inventory + AI security
- `AISystem` model (Section 24): business/technical owner, model provider,
  data processed, integrations, tools available, deployment environment,
  and three governance flags - human oversight, monitoring enabled,
  influences decisions - plus an illustrative (non-binding)
  `RegulatoryRiskTier`.
- `AISecurityFinding` model attributed to one of the 8 `AIRiskLens` values
  from Section 25 (model, application, data, identity, infrastructure,
  tool, third-party, governance) and one of 10 finding types (prompt
  injection, sensitive info disclosure, excessive agency, improper
  authorization, etc.).
- Deterministic governance gap analysis (`analyze_ai_inventory`, same
  computed-not-stored pattern as IAM/controls/data-security/continuity):
  flags tool access without human oversight (excessive agency, critical),
  decisions influenced without review (critical), no monitoring (medium),
  and high regulatory-tier third-party models without oversight (high).
- Northstar seed data: 3 AI systems - the two already referenced in the
  Phase 1 asset inventory (AST-009 Customer Support Assistant, AST-010
  Internal RAG Knowledge Assistant, both reasonably governed) plus a third,
  deliberately under-governed "Experimental AI Trading Signal Assistant"
  (no asset record, no oversight, no monitoring, influences trade
  decisions, high regulatory tier, third-party model) that trips all four
  gap-analysis rules on a fresh clone - plus 3 analyst-identified AI
  security findings across the risk lenses.
- Fixed a Pydantic v2 warning: `model_provider` collides with the
  reserved `model_` namespace prefix - resolved via
  `ConfigDict(protected_namespaces=())` rather than renaming a
  domain-natural field.
- Frontend AI Inventory (governance flags per system) and AI Security
  (analyst findings + live gap analysis) pages, replacing their Phase-0
  placeholders.
- 15 new backend tests (188 total); ruff and Bandit clean; verified end
  to end via Docker Compose with a full force-recreate, including a
  mid-verification Docker Desktop daemon drop and recovery.

## Phase 11 — RAG security + AI-agent security
- `RAGPipeline` model (Section 26) and a deterministic root-cause
  classifier (`analyze_rag_pipeline`): the same visible symptom - a RAG
  assistant surfacing information it shouldn't - is classified as either
  broken authorization (missing per-document access control) or prompt
  injection (unsanitized retrieved content), plus data poisoning
  (untrusted, unvalidated sources) and insecure output handling
  (unvalidated downstream output). Root cause, not just severity, drives
  the fix.
- `AIAgent`/`AgentAssessment` models (Section 27) and a blast-radius
  scorer (`assess_agent`, ADR 0009: its own parallel scorer, following the
  vendor-risk precedent from ADR 0008) - likelihood from autonomy level,
  human-approval requirement, and documented guardrails; impact from
  irreversibility, financial-transaction capability, and breadth of tool
  access.
- Northstar seed data continues the Phase 10 narrative: the "Internal RAG
  Knowledge Assistant" pipeline reproduces the exact access-control gap
  already flagged in Phase 10 (now classified as broken_authorization);
  a new "Public FAQ RAG Assistant" pilot ingesting untrusted public/forum
  content trips all three remaining root causes; a well-governed
  "Customer Support Draft Agent" scores Low, while the "Trading Signal
  Execution Agent" - the execution-layer counterpart of Phase 10's
  deliberately under-governed trading assistant - scores Critical
  (score 20) and is recommended to halt pending governance review.
- Frontend RAG Security (root-cause findings + pipeline catalog) and AI
  Agent Security (expandable cards with contributing factors, matching
  the Vendor Risk page pattern) pages, replacing their Phase-0
  placeholders.
- 23 new backend tests (211 total); ruff and Bandit clean; verified end
  to end via Docker Compose with a full force-recreate against real
  Postgres, through both the backend and frontend proxy.

*(Subsequent phases appended here as completed.)*
