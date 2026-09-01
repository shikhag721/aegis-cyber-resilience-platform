# Risk Methodology

## Principle: deterministic, explainable, never LLM-decided

Every score in `backend/app/risk_engine/` is a pure function of structured
input - no network call, no database call, no LLM. Given the same input,
it always returns the same output (`test_no_llm_or_randomness_same_input_same_output`).
This is a deliberate AI-assurance / risk-assurance principle (Section 50):
a risk platform that lets a generative model quietly influence a score
cannot be trusted or audited.

> **This is a portfolio demonstration methodology, calibrated for
> illustration.** It is not a certified industry standard (Section 10)
> and must be recalibrated against a real organization's own loss data
> and risk appetite before being used for an actual decision.

## Inputs

| Input | Source |
|---|---|
| `asset_criticality` | Read directly from the linked Asset (Phase 1) - a risk record can never disagree with its own asset's inventory record |
| `data_classification` | Read directly from the linked Asset |
| `internet_exposed` | Read directly from the linked Asset |
| `logging_enabled` | Read directly from the linked Asset |
| `threat_severity` | Supplied at assessment time - e.g. derived from a CVE's CVSS band (Phase 4), or a Threat's assessed severity (Phase 2) |
| `known_exploited` | Supplied at assessment time - e.g. a CISA KEV-style flag (Phase 4) |
| `control_effectiveness` | 0.0-1.0, from Phase 8's control assessment (design AND operating effectiveness, evidenced) |

## Scoring

```
Impact    = criticality_base(asset_criticality) + classification_bonus(data_classification), capped at 5
Likelihood = severity_base(threat_severity) + exposure/exploitation/detection factors, capped at 5
Inherent Score = Likelihood x Impact          (1-25)
Residual Score = Inherent Score x (1 - control_effectiveness x 0.6), minimum 1
```

| Score | Rating |
|---|---|
| 1-4 | Low |
| 5-9 | Moderate |
| 10-16 | High |
| 17-25 | Critical |

## Why this correctly separates technical severity from business risk (Section 9)

`threat_severity` (e.g. a CVSS band) is only ONE likelihood factor among
several, and impact is driven entirely by the *asset*, not the
vulnerability. This means:

- A **Critical**-severity finding on an isolated, low-criticality,
  internal-only asset (like Northstar's `AST-014` legacy test server)
  scores **low overall** - impact caps it.
- A **Medium**-severity finding on a **Critical**, internet-facing,
  restricted-data asset (like `AST-002`/`AST-003`) scores **higher
  overall** than the example above, correctly reflecting business risk
  over raw technical severity.

This is asserted directly as a test:
`tests/test_risk_engine.py::test_cvss_vs_business_risk_worked_example`.

## Inherent vs. residual risk

**Inherent risk** assumes zero effective controls. **Residual risk**
applies `control_effectiveness` - a number that should come from Phase
8's control assessment, which itself only counts a control as effective
when it is both *design-effective* (properly designed) and
*operating-effective* (evidenced as actually functioning), never from a
control simply being "documented." Controls can reduce inherent risk by
at most 60% in this model - a simple, transparent reduction, not a
probabilistic risk model.

## Risk appetite and treatment (Section 20)

`RiskAppetite` (Low/Moderate/High) sets the residual-rating ceiling the
organization tolerates without further action. `suggest_treatment()`
compares the residual rating against that ceiling and returns a
**suggestion** - Accept, or Mitigate (with Avoid/Transfer noted as
alternatives for Critical/High residual risk). This is explicitly
decision support: the actual `treatment_decision` on a `RiskRecord` is a
human-entered field (`PATCH /risk-register/{id}/treatment`), requiring a
`treatment_reason` of at least 10 characters - the engine never
auto-applies its own suggestion.

## Explainability (Section 48)

Every assessment returns `contributing_factors`: a list of exactly which
inputs pushed the score up, and why, e.g.:

```text
HIGH RISK (score 12 = likelihood 4 x impact 3)

Contributing factors:
+ Threat/vulnerability severity: high (weight 3)
+ Internet exposed (weight 1)
+ Asset criticality: high (weight 3)

Primary concern:
The affected asset is classified as high criticality.

Recommended treatment:
Mitigate (or Transfer, e.g. via insurance/contractual risk-shifting, if
mitigation is not cost-effective)
```

This is shown directly in the Risk Register UI rather than a bare number.

## Reuse across the platform

The same `app/risk_engine` module (not a copy, not a reimplementation) is
intended for reuse by:
- Vulnerability Management (Phase 4) - `threat_severity` from CVSS band, `known_exploited` from a KEV-style flag
- Vendor Risk (Phase 9) - vendor-specific inputs mapped onto the same likelihood/impact shape
- AI Security (Phase 10) - AI-system-specific risk factors mapped onto the same shape

This is why the engine's `RiskInput` fields are generic (criticality,
classification, exposure, severity, control effectiveness) rather than
asset-specific - see `docs/decisions/0004-modular-monolith.md`.
