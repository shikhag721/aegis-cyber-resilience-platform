# Northstar Financial Services — Threat Model

Live data: `GET /api/v1/threat-actors`, `/api/v1/threats`, `/api/v1/attack-paths`
(seeded by `backend/app/seed_data/northstar_threats.py`). This document is
the narrative companion, not a duplicate of the data.

## Trust boundaries and data flow (simplified)

```text
                    ┌─────────── Internet (untrusted) ───────────┐
                    │                                              │
                    ▼                                              ▼
          Customer Web Portal (AST-001)                Salesforce CRM (AST-008)
                    │                                   [third-party trust boundary]
                    ▼
          Edge Load Balancer (AST-013)
                    │
                    ▼
     ═══════ trust boundary: perimeter ═══════
                    │
                    ▼
          Public API Gateway (AST-002)
                    │
                    ▼
     ═══════ trust boundary: internal services ═══════
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
Payment Processing (AST-003)   AI Customer Support (AST-009)
          │                   │
          ▼                   ▼
     Customer Database (AST-004) ◄── restricted: customer PII, payment data
```

Employees (via AST-005 Identity Provider) and the Core Banking Server
(AST-012) sit inside the internal-services boundary and are not directly
reachable from the internet — any path that reaches them from outside
must cross at least the perimeter and internal-services boundaries above.

## Threat actors modeled

See `GET /api/v1/threat-actors` for the live records. Three actor types
are modeled: an externally motivated organized cybercrime group (the
primary actor for customer-facing paths), a malicious insider (relevant
because of standing internal database access), and a compromised
third-party vendor (relevant because of the Salesforce integration).

## Why each threat is relevant here (not just a MITRE ID)

Every entry in the threat catalog includes a `why_relevant` field tying
the technique to a specific Northstar asset or a specific, named control
gap — see the "Threat Catalog" section of the Threat Modeling page in the
running app, or query `/api/v1/threats` directly. This was a deliberate,
enforced design choice: `ThreatCreate.why_relevant` has a validator
(`backend/app/schemas/threat.py`) rejecting anything under 20 characters,
specifically to prevent the anti-pattern the project brief calls out —
listing a MITRE technique ID with no scenario-specific justification.

## Attack paths

Three attack paths are modeled, each scored by likelihood × impact
(1-25, same scale the risk engine will use in Phase 3):

1. **Compromised customer credential → payment data exfiltration**
   (score 15) — the Section 8 worked example, applied to real assets:
   credential stuffing against the Web Portal → authenticated API Gateway
   access → privilege abuse in the Payment Processing Service → Customer
   Database access.
2. **Malicious insider bulk export of customer records** (score 10) —
   lower likelihood than the external path, but comparable impact;
   included specifically so insider risk isn't deprioritized purely on
   likelihood, a common (and dangerous) shortcut in less rigorous risk
   registers.
3. **Compromised vendor session reaches commercial client data** (score
   8) — models third-party/supply-chain risk via the Salesforce
   integration, foreshadowing the dedicated Vendor Risk module (Phase 9).

## What this threat model does not cover

- It does not model every asset's every threat — it is illustrative,
  covering the highest-value paths given Northstar's stated architecture
  (Section 4), not an exhaustive enumeration.
- MITRE ATT&CK technique IDs are asserted based on the scenario described,
  not derived from an actual detection/telemetry pipeline (there isn't
  one — see `docs/architecture/limitations.md`).
- Likelihood/impact scores here are illustrative, calibrated the same way
  the Phase 3 risk engine will be — not a validated actuarial estimate.
