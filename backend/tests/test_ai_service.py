import pytest

from app.db.session import SessionLocal
from app.services import ai as ai_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _ai_system(**overrides) -> dict:
    defaults = dict(
        name="Test AI Assistant",
        business_owner="o",
        technical_owner="t",
        purpose="p",
        model_provider="Internal model",
        data_processed="d",
        user_base="Internal staff",
        integrations=[],
        tools_available=[],
        deployment_environment="production",
        human_oversight=True,
        monitoring_enabled=True,
        influences_decisions=False,
        regulatory_risk_tier="minimal",
    )
    defaults.update(overrides)
    return defaults


def test_create_and_get_ai_system(db_session):
    ai_system = ai_service.create_ai_system(db_session, _ai_system())
    fetched = ai_service.get_ai_system(db_session, ai_system.id)
    assert fetched.name == "Test AI Assistant"


def test_tool_access_without_oversight_flagged_excessive_agency(db_session):
    ai_service.create_ai_system(
        db_session,
        _ai_system(tools_available=["database_query"], human_oversight=False),
    )
    findings = ai_service.analyze_ai_inventory(db_session)
    assert any(f.finding_type == "excessive_agency_risk" for f in findings)


def test_tool_access_with_oversight_not_flagged(db_session):
    ai_service.create_ai_system(
        db_session,
        _ai_system(tools_available=["database_query"], human_oversight=True),
    )
    findings = ai_service.analyze_ai_inventory(db_session)
    assert not any(f.finding_type == "excessive_agency_risk" for f in findings)


def test_decision_influence_without_oversight_flagged(db_session):
    ai_service.create_ai_system(
        db_session, _ai_system(influences_decisions=True, human_oversight=False)
    )
    findings = ai_service.analyze_ai_inventory(db_session)
    assert any(f.finding_type == "unreviewed_decision_influence" for f in findings)


def test_no_monitoring_flagged_medium(db_session):
    ai_service.create_ai_system(db_session, _ai_system(monitoring_enabled=False))
    findings = ai_service.analyze_ai_inventory(db_session)
    match = next(f for f in findings if f.finding_type == "no_monitoring")
    assert match.severity == "medium"


def test_high_tier_third_party_no_oversight_flagged(db_session):
    ai_service.create_ai_system(
        db_session,
        _ai_system(
            model_provider="Third-party LLM API",
            regulatory_risk_tier="high",
            human_oversight=False,
        ),
    )
    findings = ai_service.analyze_ai_inventory(db_session)
    assert any(f.finding_type == "high_tier_third_party_no_oversight" for f in findings)


def test_well_governed_system_produces_no_findings(db_session):
    ai_service.create_ai_system(db_session, _ai_system())
    findings = ai_service.analyze_ai_inventory(db_session)
    assert findings == []


def test_create_finding_and_list_all(db_session):
    ai_system = ai_service.create_ai_system(db_session, _ai_system())
    ai_service.create_finding(
        db_session,
        ai_system.id,
        dict(
            risk_lens="application",
            finding_type="prompt_injection",
            severity="high",
            description="d",
            recommendation="r",
        ),
    )
    findings = ai_service.list_all_findings(db_session)
    assert len(findings) == 1
    assert findings[0].risk_lens.value == "application"
