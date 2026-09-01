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

## Issues found and fixed during integration testing

Kept here deliberately rather than deleted, as a record that the stack was
actually run end-to-end, not just unit tested in isolation:

- **Phase 0**: the frontend's Vite dev-server proxy defaulted to
  `http://localhost:8000` for the backend target. That works when running
  the frontend directly on the host, but inside Docker Compose
  "localhost" from the frontend container resolves to itself, not the
  `backend` service — every proxied `/api/*` request returned `502 Bad
  Gateway`. Fixed by setting `VITE_API_PROXY_TARGET=http://backend:8000`
  as an environment variable on the `frontend` service in
  `infra/docker/docker-compose.yml`, read by `frontend/vite.config.ts`.
  Caught by actually curling `http://localhost:5173/api/v1/health`
  through the browser-facing port after bringing up the full stack, not
  by testing each container in isolation — see `docs/testing/README.md`.
- **Phase 0**: `passlib[bcrypt]` failed its own internal self-test against
  modern `bcrypt` releases (`ValueError: password cannot be longer than 72
  bytes`) — an unrelated, unmaintained-library incompatibility, not a bug
  in this code. Replaced with Argon2id via `argon2-cffi`; see ADR 0006.
- **Phase 0**: `npm audit` flagged moderate/high vulnerabilities in the
  pinned `vite`/`esbuild` and `react-router-dom` versions (dev-server CORS
  exposure and an open-redirect/deserialization issue respectively).
  Upgraded to `vite@8` + `@vitejs/plugin-react@6` and
  `react-router-dom@7`; `npm audit` reports zero vulnerabilities after the
  upgrade and the build/tests still pass.

*(This list grows as each phase is built — see CHANGELOG.md for what has
landed so far.)*
