"""Pure unit tests for app/risk_engine/ - deliberately import nothing from
app.db, app.models, or FastAPI, proving the engine has zero infrastructure
dependency (see docs/decisions/0004-modular-monolith.md).
"""
from app.risk_engine import RiskAppetite, RiskInput, assess, compute_residual, rating_for_score


def _input(**overrides) -> RiskInput:
    defaults = dict(
        asset_criticality="low",
        data_classification="internal",
        threat_severity="low",
        internet_exposed=False,
        known_exploited=False,
        logging_enabled=True,
        control_effectiveness=0.0,
    )
    defaults.update(overrides)
    return RiskInput(**defaults)


def test_baseline_low_risk():
    result = assess(_input())
    assert result.likelihood == 1
    assert result.impact == 1
    assert result.inherent_score == 1
    assert result.inherent_rating == "Low"


def test_score_is_likelihood_times_impact():
    result = assess(_input(asset_criticality="high", threat_severity="high", internet_exposed=True))
    assert result.inherent_score == result.likelihood * result.impact


def test_rating_bands():
    assert rating_for_score(1) == "Low"
    assert rating_for_score(4) == "Low"
    assert rating_for_score(5) == "Moderate"
    assert rating_for_score(9) == "Moderate"
    assert rating_for_score(10) == "High"
    assert rating_for_score(16) == "High"
    assert rating_for_score(17) == "Critical"
    assert rating_for_score(25) == "Critical"


def test_cvss_vs_business_risk_worked_example():
    """Section 9's exact example: a low-severity finding on a critical,
    internet-facing, sensitive-data asset should outrank a high-severity
    finding on an isolated, low-value asset.
    """
    isolated_low_value_high_severity = assess(
        _input(
            asset_criticality="low",
            data_classification="internal",
            threat_severity="critical",  # e.g. CVSS 9.8
            internet_exposed=False,
        )
    )
    internet_facing_payment_api_moderate_severity = assess(
        _input(
            asset_criticality="critical",
            data_classification="restricted",
            threat_severity="medium",  # e.g. CVSS 7
            internet_exposed=True,
        )
    )
    assert (
        internet_facing_payment_api_moderate_severity.inherent_score
        > isolated_low_value_high_severity.inherent_score
    )


def test_known_exploited_increases_likelihood():
    without_kev = assess(_input(threat_severity="medium"))
    with_kev = assess(_input(threat_severity="medium", known_exploited=True))
    assert with_kev.likelihood > without_kev.likelihood


def test_missing_logging_increases_likelihood():
    with_logging = assess(_input(threat_severity="medium"))
    without_logging = assess(_input(threat_severity="medium", logging_enabled=False))
    assert without_logging.likelihood > with_logging.likelihood


def test_likelihood_and_impact_capped_at_five():
    result = assess(
        _input(
            asset_criticality="critical",
            data_classification="highly_restricted",
            threat_severity="critical",
            internet_exposed=True,
            known_exploited=True,
            logging_enabled=False,
        )
    )
    assert result.likelihood == 5
    assert result.impact == 5
    assert result.inherent_score == 25
    assert result.inherent_rating == "Critical"


def test_compute_residual_reduces_score_with_effective_controls():
    residual_full, _ = compute_residual(20, control_effectiveness=1.0)
    residual_none, _ = compute_residual(20, control_effectiveness=0.0)
    assert residual_full < residual_none
    assert residual_none == 20


def test_residual_never_reduced_to_zero():
    residual, rating = compute_residual(1, control_effectiveness=1.0)
    assert residual >= 1
    assert rating == "Low"


def test_treatment_accept_when_within_appetite():
    result = assess(_input(), risk_appetite=RiskAppetite.HIGH)
    assert result.recommended_treatment == "Accept"


def test_treatment_mitigate_when_above_appetite():
    result = assess(
        _input(
            asset_criticality="critical",
            data_classification="restricted",
            threat_severity="critical",
            internet_exposed=True,
        ),
        risk_appetite=RiskAppetite.LOW,
    )
    assert "Mitigate" in result.recommended_treatment


def test_no_llm_or_randomness_same_input_same_output():
    """Guards the Section 50 principle: deterministic scoring only."""
    a = assess(_input(threat_severity="high", internet_exposed=True))
    b = assess(_input(threat_severity="high", internet_exposed=True))
    assert a.inherent_score == b.inherent_score
    assert a.residual_rating == b.residual_rating


def test_contributing_factors_explain_the_score():
    result = assess(_input(asset_criticality="critical", internet_exposed=True, known_exploited=True))
    factor_names = {f.name for f in result.contributing_factors}
    assert any("critical" in n for n in factor_names)
    assert "Internet exposed" in factor_names
    assert "Known exploited" in factor_names
