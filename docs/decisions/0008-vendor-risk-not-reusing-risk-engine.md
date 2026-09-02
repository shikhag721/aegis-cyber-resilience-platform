# ADR 0008: Vendor risk gets its own scorer, not a forced fit into risk_engine

## Status
Accepted

## Context
`docs/risk-methodology/README.md` (Phase 3) explicitly named Vendor Risk as
a candidate reuse target for `app/risk_engine/`'s `RiskInput` shape
(criticality, data classification, exposure, threat severity, control
effectiveness). When actually building Phase 9, the vendor risk factors
that matter - subprocessors, certifications, contractual security clauses,
incident history, exit strategy - don't map cleanly onto that shape.
Forcing "does the vendor have a signed security clause" into a field
called `logging_enabled`, for example, would work mechanically but
misrepresent what's actually being measured, and would confuse a reader
trying to understand the score's reasoning.

## Decision
`app/services/vendor.py` implements its own small, deterministic scorer
using the *same design pattern* as `app/risk_engine/` (likelihood/impact
built from named, explainable, capped factors; a 1-25 score; the same
Low/Moderate/High/Critical bands) but with vendor-specific field names and
factors, not a literal call into `risk_engine.assess()`.

## Why this isn't a contradiction of "don't scatter risk calculations"
(Section 10 asks for "a dedicated risk engine," not literally one function
used everywhere.) The *pattern* is centralized and consistently applied
(every scorer in this codebase produces the same shape of explainable
result); the *inputs* are allowed to be domain-specific where the domains
genuinely differ. This is the same reasoning IAM risk
(`app/services/iam.py`) and cloud/app-security findings already followed -
neither of those forced their findings through `risk_engine` either.

## Consequences
Anyone extending this pattern to a new domain (e.g. a future module) should
ask: do this domain's real risk factors actually correspond to asset
criticality/exposure/severity, or are they a different shape entirely? If
different, follow this file's precedent - a small parallel scorer with the
same explainability contract - rather than force a resemblance that isn't
there.
