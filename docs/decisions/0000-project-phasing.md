# ADR 0000: Phased Build Order

## Status
Accepted

## Context
AEGIS covers an unusually wide surface (asset management through AI agent
security) for a single portfolio project. Building every module to full
depth simultaneously risks a shallow, untested, unexplainable result across
the board.

## Decision
Build in the phase order below. Each phase must have working code, passing
tests, and updated documentation before the next phase starts, and is
committed/pushed independently (see `CHANGELOG.md` for the running log):

0. Repository + architecture + security baseline
1. Enterprise data model + asset inventory
2. Threat modeling + attack paths
3. Risk engine
4. Vulnerability management
5. IAM + cloud security
6. Application/API security + secrets detection
7. Security monitoring + incident response
8. GRC + controls + evidence
9. Third-party risk + data security + resilience
10. AI inventory + AI security
11. RAG security + AI-agent security
12. DevSecOps (CI security gates)
13. Executive dashboard + reports
14. Final security review + portfolio hardening

## Consequences
- Early phases (data model, risk engine) are foundational and other
  modules depend on them — regressions there block everything downstream,
  so they carry the most test coverage.
- Later modules (AI security, RAG security, agent security) can reuse the
  same risk engine and control-assessment machinery built in phases 3 and
  8, rather than each inventing its own scoring logic — this is why the
  risk engine is built once, early, and imported everywhere else.
