import pytest

from app.db.session import SessionLocal
from app.services import agent as agent_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _agent(**overrides) -> dict:
    defaults = dict(
        name="Test Agent",
        purpose="A test AI agent",
        tools_available=["lookup"],
        autonomy_level="human_approval_required",
        can_take_irreversible_actions=False,
        can_initiate_financial_transactions=False,
        requires_human_approval=True,
        data_access_scope="Read-only test data",
        guardrails_description="Restricted to read-only tools; all actions logged.",
    )
    defaults.update(overrides)
    return defaults


def test_well_governed_agent_scores_low(db_session):
    agent = agent_service.create_agent(db_session, _agent())
    result = agent_service.assess_agent(agent)
    assert result.rating == "Low"
    assert result.recommendation == "Approve for current scope"


def test_fully_autonomous_agent_with_no_guardrails_scores_high_or_critical(db_session):
    agent = agent_service.create_agent(
        db_session,
        _agent(
            tools_available=["execute_trade", "transfer_funds", "send_email"],
            autonomy_level="fully_autonomous",
            can_take_irreversible_actions=True,
            can_initiate_financial_transactions=True,
            requires_human_approval=False,
            guardrails_description="",
        ),
    )
    result = agent_service.assess_agent(agent)
    assert result.rating in ("High", "Critical")
    assert result.recommendation in (
        "Require human-in-the-loop before any irreversible action",
        "Halt autonomous operation pending governance review",
    )
    assert len(result.contributing_factors) >= 4


def test_no_human_approval_increases_likelihood(db_session):
    approved = agent_service.create_agent(db_session, _agent(name="approved"))
    unapproved = agent_service.create_agent(
        db_session, _agent(name="unapproved", requires_human_approval=False)
    )
    approved_result = agent_service.assess_agent(approved)
    unapproved_result = agent_service.assess_agent(unapproved)
    assert unapproved_result.likelihood > approved_result.likelihood


def test_financial_and_irreversible_actions_increase_impact(db_session):
    safe = agent_service.create_agent(db_session, _agent(name="safe"))
    risky = agent_service.create_agent(
        db_session,
        _agent(
            name="risky",
            can_take_irreversible_actions=True,
            can_initiate_financial_transactions=True,
        ),
    )
    safe_result = agent_service.assess_agent(safe)
    risky_result = agent_service.assess_agent(risky)
    assert risky_result.impact > safe_result.impact


def test_run_assessment_persists_result(db_session):
    agent = agent_service.create_agent(db_session, _agent())
    assessment = agent_service.run_assessment(db_session, agent)
    fetched = agent_service.latest_assessment(db_session, agent.id)
    assert fetched.id == assessment.id
    assert fetched.score == assessment.score


def test_score_is_capped_likelihood_times_impact(db_session):
    agent = agent_service.create_agent(
        db_session,
        _agent(
            tools_available=["a", "b", "c", "d"],
            autonomy_level="fully_autonomous",
            can_take_irreversible_actions=True,
            can_initiate_financial_transactions=True,
            requires_human_approval=False,
            guardrails_description="",
        ),
    )
    result = agent_service.assess_agent(agent)
    assert result.likelihood <= 5
    assert result.impact <= 5
    assert 1 <= result.score <= 25
