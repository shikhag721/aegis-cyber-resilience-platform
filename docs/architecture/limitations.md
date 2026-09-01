# Limitations

Updated as each phase lands. Being explicit here is itself part of the
GRC/AI-assurance skill this project demonstrates — see the equivalent
document in the companion AI Governance project for the same principle
applied there.

## Organizational / data
- Northstar Financial Services is entirely fictional; every asset,
  vulnerability, incident, vendor, and AI system record is synthetic.

## Integrations
- No live cloud provider API integration (AWS/Azure/GCP) — cloud security
  findings are modeled, structured data, not a live Config/Security Hub
  export. See ADR 0005.
- No live SIEM/EDR/IdP integration — security events and IAM findings are
  synthetic and seeded, not collected from a real environment.
- No live vulnerability scanner integration — CVE/CVSS records are
  synthetic/curated, not pulled from a real scanner feed.

## Security engineering
- Local/demo deployment only (Docker Compose); not hardened for
  multi-tenant production use (no WAF, no network segmentation beyond
  Docker's default bridge network, no secrets manager — `.env` only).
- The frontend Docker image runs Vite's dev server, not a production
  Nginx-served static build — documented in `infra/docker/frontend.Dockerfile`.
- Rate limiting is not yet implemented (planned for Phase 6 alongside
  application/API security hardening).

## Risk & GRC methodology
- The risk-scoring methodology (see `docs/risk-methodology/` once Phase 3
  lands) is an illustrative, documented model — not an industry-certified
  standard, and not a substitute for a real risk appetite exercise.
- Framework mappings (NIST CSF 2.0, CIS Controls, MITRE ATT&CK, OWASP,
  NIST AI RMF) are this project's own interpretation for illustrative
  purposes — "mapped to" / "aligned with," never "certified compliant with."

## AI security
- AI/RAG/agent security scenarios are simulated against local test
  fixtures, not a production LLM deployment with real user traffic.

*(This list grows as each phase is built — see CHANGELOG.md for what has
landed so far.)*
