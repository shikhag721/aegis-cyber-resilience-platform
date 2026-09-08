import pytest

from app.db.session import SessionLocal
from app.services import asset as asset_service
from app.services import dashboard as dashboard_service
from app.services import risk as risk_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _asset(**overrides) -> dict:
    defaults = dict(
        asset_tag="AST-DASH-1",
        name="Test Asset",
        asset_type="server",
        owner="o",
        business_unit="bu",
        environment="production",
        criticality="critical",
        data_classification="restricted",
    )
    defaults.update(overrides)
    return defaults


def test_empty_database_produces_zeroed_summary(db_session):
    summary = dashboard_service.build_executive_summary(db_session)
    assert summary.assets_total == 0
    assert summary.risks_open == 0
    assert summary.assets_by_criticality == {}


def test_asset_counted_by_criticality(db_session):
    asset_service.create_asset(db_session, _asset())
    summary = dashboard_service.build_executive_summary(db_session)
    assert summary.assets_total == 1
    assert summary.assets_by_criticality == {"critical": 1}


def test_open_risk_counted_closed_risk_excluded(db_session):
    asset = asset_service.create_asset(db_session, _asset())
    open_risk = risk_service.create_risk_record(
        db_session,
        dict(
            title="Open risk",
            description="d",
            asset_id=asset.id,
            threat_id=None,
            threat_severity="high",
            known_exploited=False,
            control_effectiveness=2,
        ),
    )
    closed_risk = risk_service.create_risk_record(
        db_session,
        dict(
            title="Closed risk",
            description="d",
            asset_id=asset.id,
            threat_id=None,
            threat_severity="high",
            known_exploited=False,
            control_effectiveness=2,
        ),
    )
    risk_service.update_treatment(db_session, closed_risk, {"status": "closed"})

    summary = dashboard_service.build_executive_summary(db_session)
    assert summary.risks_open == 1
    assert sum(summary.risks_by_residual_rating.values()) == 1
    assert open_risk.id != closed_risk.id


def test_recommended_actions_empty_summary_has_default_message():
    summary = dashboard_service.ExecutiveSummary()
    actions = dashboard_service.recommended_actions(summary)
    assert actions == ["No threshold-triggered actions - overall posture is within acceptable ranges."]


def test_recommended_actions_flags_critical_risk():
    summary = dashboard_service.ExecutiveSummary(risks_by_residual_rating={"Critical": 2})
    actions = dashboard_service.recommended_actions(summary)
    assert any("Critical-residual-risk" in a for a in actions)


def test_top_risk_highlights_sorted_critical_first(db_session):
    asset = asset_service.create_asset(db_session, _asset())
    risk_service.create_risk_record(
        db_session,
        dict(
            title="Low severity",
            description="d",
            asset_id=asset.id,
            threat_id=None,
            threat_severity="low",
            known_exploited=False,
            control_effectiveness=5,
        ),
    )
    risk_service.create_risk_record(
        db_session,
        dict(
            title="High severity",
            description="d",
            asset_id=asset.id,
            threat_id=None,
            threat_severity="critical",
            known_exploited=True,
            control_effectiveness=0,
        ),
    )
    highlights = dashboard_service.top_risk_highlights(db_session)
    assert highlights[0].title == "High severity"
