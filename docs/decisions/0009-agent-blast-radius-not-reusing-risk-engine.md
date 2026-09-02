# ADR 0009: AI agent blast-radius gets its own scorer, following the vendor-risk precedent

## Status
Accepted

## Context
Phase 11 (Section 27) needs to assess how much damage an AI agent could
cause if it were manipulated or simply malfunctioned - its "blast radius."
The factors that actually matter here - autonomy level, whether a human
approves actions before they take effect, whether actions are reversible,
whether the agent can move money, how many tools it can reach, whether any
guardrails are documented - are agent-specific and don't correspond to
asset-based likelihood/impact inputs any more than vendor risk factors did
(see `docs/decisions/0008-vendor-risk-not-reusing-risk-engine.md`).

## Decision
`app/services/agent.py::assess_agent()` implements its own small,
deterministic scorer using the same design pattern as `app/risk_engine/`
and `app/services/vendor.py` - likelihood/impact built from named,
explainable, capped factors; a 1-25 score; the same Low/Moderate/High/
Critical bands - with agent-specific factors and a recommendation
vocabulary suited to agent governance ("Halt autonomous operation pending
governance review" rather than "Escalate").

## Why
This is the third instance of the same pattern (risk engine → vendor risk
→ agent blast radius), which confirms it as the house style rather than a
one-off: centralize the *shape* of explainable scoring, let the *inputs*
be domain-specific where domains genuinely differ. Likelihood here answers
"how likely is this agent to act on a bad instruction without being
caught first" (autonomy level, human-approval requirement, documented
guardrails); impact answers "how bad is it if it does" (irreversibility,
financial capability, breadth of tool access) - a deliberately different
question from asset-based risk, IAM risk, or vendor risk, but scored with
the same explainability contract.

## Consequences
The AI Agent Security frontend page can display `contributing_factors`
identically to how the Vendor Risk page already renders vendor factors -
no bespoke rendering logic needed for a "new shape" of risk result. Anyone
adding a fourth domain-specific scorer should keep following this
precedent rather than inventing a fourth shape.
