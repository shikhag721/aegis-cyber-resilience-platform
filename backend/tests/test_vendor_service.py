import pytest

from app.db.session import SessionLocal
from app.services import vendor as vendor_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _vendor(**overrides) -> dict:
    defaults = dict(
        name="Test Vendor",
        service_description="A test SaaS vendor",
        business_criticality="medium",
        data_access=True,
        data_classification_handled="internal",
        security_controls_summary="Documented security program",
        certifications="SOC 2 Type II",
        has_incident_history=False,
        subprocessors="",
        contractual_security_clause=True,
        exit_strategy_defined=True,
    )
    defaults.update(overrides)
    return defaults


def test_well_governed_vendor_scores_low(db_session):
    vendor = vendor_service.create_vendor(db_session, _vendor())
    result = vendor_service.assess_vendor(vendor)
    assert result.rating == "Low"
    assert result.recommendation == "Approve"


def test_poorly_governed_vendor_scores_high_or_critical(db_session):
    vendor = vendor_service.create_vendor(
        db_session,
        _vendor(
            business_criticality="critical",
            data_classification_handled="restricted",
            certifications="",
            contractual_security_clause=False,
            has_incident_history=True,
            incident_history_notes="Data breach disclosed in 2024.",
            subprocessors="Unknown third-party analytics provider",
            exit_strategy_defined=False,
        ),
    )
    result = vendor_service.assess_vendor(vendor)
    assert result.rating in ("High", "Critical")
    assert result.recommendation in ("Approve with conditions", "Escalate")
    assert len(result.contributing_factors) >= 4


def test_incident_history_increases_likelihood(db_session):
    clean = vendor_service.create_vendor(db_session, _vendor(name="clean"))
    incident = vendor_service.create_vendor(
        db_session, _vendor(name="incident", has_incident_history=True)
    )
    clean_result = vendor_service.assess_vendor(clean)
    incident_result = vendor_service.assess_vendor(incident)
    assert incident_result.likelihood > clean_result.likelihood


def test_run_assessment_persists_result(db_session):
    vendor = vendor_service.create_vendor(db_session, _vendor())
    assessment = vendor_service.run_assessment(db_session, vendor)
    fetched = vendor_service.latest_assessment(db_session, vendor.id)
    assert fetched.id == assessment.id
    assert fetched.score == assessment.score


def test_score_is_capped_likelihood_times_impact(db_session):
    vendor = vendor_service.create_vendor(
        db_session,
        _vendor(
            business_criticality="critical",
            data_classification_handled="highly_restricted",
            certifications="",
            contractual_security_clause=False,
            has_incident_history=True,
            subprocessors="many",
            exit_strategy_defined=False,
        ),
    )
    result = vendor_service.assess_vendor(vendor)
    assert result.likelihood <= 5
    assert result.impact <= 5
    assert 1 <= result.score <= 25
