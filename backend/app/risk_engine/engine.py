"""Risk scoring logic.

Methodology (see docs/risk-methodology/ for the full write-up): likelihood
and impact are each built from named, explainable factors and capped at 5,
then multiplied for a 1-25 inherent score. Residual score applies control
effectiveness. This is a documented, illustrative methodology - NOT a
certified industry standard (Section 10) - and should be calibrated to a
real organization's own risk appetite and loss data before being used for
an actual decision.

Critically: Technical Severity (threat_severity, e.g. a CVSS band) is only
ONE input alongside asset criticality, data classification, and exposure -
never the whole score by itself. This is what lets the engine correctly
express Section 9's example: a CVSS 9.8 on an isolated low-value asset can
score lower overall than a CVSS 7 on an internet-facing, sensitive-data,
critical asset.
"""
from app.risk_engine.models import RiskAppetite, RiskFactor, RiskInput, RiskResult

RATING_BANDS = [
    (1, 4, "Low"),
    (5, 9, "Moderate"),
    (10, 16, "High"),
    (17, 25, "Critical"),
]

_CRITICALITY_BASE_IMPACT = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_CLASSIFICATION_IMPACT_BONUS = {
    "public": 0,
    "internal": 0,
    "confidential": 1,
    "restricted": 1,
    "highly_restricted": 2,
}
_SEVERITY_BASE_LIKELIHOOD = {"low": 1, "medium": 2, "high": 3, "critical": 4}

_RATING_RANK = {"Low": 0, "Moderate": 1, "High": 2, "Critical": 3}
_APPETITE_MAX_ACCEPTABLE_RANK = {
    RiskAppetite.LOW: 0,  # only "Low" is acceptable without treatment
    RiskAppetite.MODERATE: 1,  # up to "Moderate"
    RiskAppetite.HIGH: 2,  # up to "High"
}


def rating_for_score(score: int) -> str:
    for low, high, rating in RATING_BANDS:
        if low <= score <= high:
            return rating
    return "Critical"


def compute_impact(data: RiskInput) -> tuple[int, list[RiskFactor]]:
    factors: list[RiskFactor] = []
    raw = _CRITICALITY_BASE_IMPACT.get(data.asset_criticality, 1)
    factors.append(
        RiskFactor(
            name=f"Asset criticality: {data.asset_criticality}",
            axis="impact",
            weight=raw,
            reason=f"The affected asset is classified as {data.asset_criticality} criticality.",
        )
    )

    bonus = _CLASSIFICATION_IMPACT_BONUS.get(data.data_classification, 0)
    if bonus:
        raw += bonus
        factors.append(
            RiskFactor(
                name=f"Data classification: {data.data_classification}",
                axis="impact",
                weight=bonus,
                reason=f"The asset processes {data.data_classification} data.",
            )
        )

    return min(raw, 5), factors


def compute_likelihood(data: RiskInput) -> tuple[int, list[RiskFactor]]:
    factors: list[RiskFactor] = []
    raw = _SEVERITY_BASE_LIKELIHOOD.get(data.threat_severity, 1)
    factors.append(
        RiskFactor(
            name=f"Threat/vulnerability severity: {data.threat_severity}",
            axis="likelihood",
            weight=raw,
            reason=f"The underlying threat or vulnerability is rated {data.threat_severity} severity.",
        )
    )

    if data.internet_exposed:
        raw += 1
        factors.append(
            RiskFactor(
                name="Internet exposed",
                axis="likelihood",
                weight=1,
                reason="The asset is directly reachable from the internet, widening the attacker pool.",
            )
        )

    if data.known_exploited:
        raw += 2
        factors.append(
            RiskFactor(
                name="Known exploited",
                axis="likelihood",
                weight=2,
                reason="This vulnerability/technique has confirmed real-world exploitation activity.",
            )
        )

    if not data.logging_enabled:
        raw += 1
        factors.append(
            RiskFactor(
                name="Logging not enabled",
                axis="likelihood",
                weight=1,
                reason="Without logging, an attempt against this asset is unlikely to be detected quickly.",
            )
        )

    return min(raw, 5), factors


def compute_residual(inherent_score: int, control_effectiveness: float) -> tuple[int, str]:
    """control_effectiveness is 0.0 (no effective controls) to 1.0 (fully
    effective controls), typically derived from Phase 8's control
    assessment (design AND operating effectiveness, evidenced - not just
    "a control exists"). Controls can reduce inherent risk by at most 60%
    - a documented, simple, transparent reduction model, not a
    probabilistic risk model. See docs/risk-methodology/.
    """
    control_effectiveness = max(0.0, min(1.0, control_effectiveness))
    reduction = 1.0 - (control_effectiveness * 0.6)
    residual_score = max(1, round(inherent_score * reduction))
    return residual_score, rating_for_score(residual_score)


def suggest_treatment(residual_rating: str, risk_appetite: RiskAppetite = RiskAppetite.MODERATE) -> str:
    """A suggestion only - Section 20/23 both require this to remain
    decision support, never an automatic, binding treatment decision.
    """
    residual_rank = _RATING_RANK[residual_rating]
    max_acceptable = _APPETITE_MAX_ACCEPTABLE_RANK[risk_appetite]

    if residual_rank <= max_acceptable:
        return "Accept"
    if residual_rank == 3:  # Critical - prefer Mitigate over Transfer/Avoid
        return "Mitigate (or Avoid if mitigation is not feasible)"
    return (
        "Mitigate (or Transfer, e.g. via insurance/contractual risk-shifting, "
        "if mitigation is not cost-effective)"
    )


def assess(data: RiskInput, risk_appetite: RiskAppetite = RiskAppetite.MODERATE) -> RiskResult:
    impact, impact_factors = compute_impact(data)
    likelihood, likelihood_factors = compute_likelihood(data)
    factors = likelihood_factors + impact_factors

    inherent_score = likelihood * impact
    inherent_rating = rating_for_score(inherent_score)

    residual_score, residual_rating = compute_residual(inherent_score, data.control_effectiveness)

    primary = max(factors, key=lambda f: f.weight) if factors else None
    primary_concern = primary.reason if primary else "No significant risk factors identified."

    return RiskResult(
        likelihood=likelihood,
        impact=impact,
        inherent_score=inherent_score,
        inherent_rating=inherent_rating,
        residual_score=residual_score,
        residual_rating=residual_rating,
        contributing_factors=factors,
        primary_concern=primary_concern,
        recommended_treatment=suggest_treatment(residual_rating, risk_appetite),
    )
