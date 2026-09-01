"""Dedicated, dependency-free risk scoring engine (Section 10).

Deliberately has NO imports from FastAPI, SQLAlchemy, or any other app
module - it takes plain values in and returns plain dataclasses out, so it
can be unit tested with zero infrastructure and reused identically by
Vulnerability Management (Phase 4), IAM Risk (Phase 5), Vendor Risk
(Phase 9), and AI Security (Phase 10) rather than each reimplementing its
own scoring logic. See docs/decisions/0004-modular-monolith.md and
docs/risk-methodology/ for the full write-up.
"""
from app.risk_engine.engine import (
    RATING_BANDS,
    assess,
    compute_impact,
    compute_likelihood,
    compute_residual,
    rating_for_score,
    suggest_treatment,
)
from app.risk_engine.models import RiskAppetite, RiskFactor, RiskInput, RiskResult

__all__ = [
    "RATING_BANDS",
    "RiskAppetite",
    "RiskFactor",
    "RiskInput",
    "RiskResult",
    "assess",
    "compute_impact",
    "compute_likelihood",
    "compute_residual",
    "rating_for_score",
    "suggest_treatment",
]
