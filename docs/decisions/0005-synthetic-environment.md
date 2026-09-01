# ADR 0005: Fully synthetic environment, no live integrations

## Status
Accepted

## Context
A realistic enterprise security platform would integrate with real cloud
provider APIs, a real IdP, a real SIEM, and real vulnerability scanners.
Doing so here would mean either (a) requiring the reviewer to have cloud
accounts and credentials just to run the demo, or (b) actually scanning
real infrastructure, which is out of scope and against this project's
explicit defensive/educational safety boundary (`SECURITY.md`).

## Decision
Every data source in AEGIS — assets, vulnerabilities, IAM findings, cloud
posture findings, security events, incidents, AI systems — is structured,
synthetic, seeded data for the fictional Northstar Financial Services,
not a live integration. Modules are explicitly named to reflect this,
e.g. "Security Monitoring & Incident **Simulation**," not "SIEM."

## Why
- Runnable by anyone with Docker and no external accounts.
- No risk of accidentally scanning or targeting a real system.
- Forces the risk/control logic itself to be the thing under test, not
  the reliability of a third-party integration.

## Consequences
- Documented explicitly, module by module, as a limitation — see
  `docs/architecture/limitations.md` — so this is never presented as more
  capable than it is.
- The architecture still models what a *real* integration would look like
  (e.g. `backend/app/models/cloud_finding.py` has the fields a real AWS
  Config/Security Hub export would produce) so extending to a live
  integration later is a data-source change, not a schema redesign.
