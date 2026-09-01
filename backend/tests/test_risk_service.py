import pytest

from app.db.session import SessionLocal
from app.models.asset import AssetType, Criticality, DataClassification, Environment
from app.models.risk import RiskStatus, TreatmentDecision
from app.services import asset as asset_service
from app.services import risk as risk_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def critical_asset(db_session):
    return asset_service.create_asset(
        db_session,
        dict(
            asset_tag="AST-RISK-1",
            name="Test Payment API",
            asset_type=AssetType.API,
            owner="Owner",
            business_unit="BU",
            environment=Environment.PRODUCTION,
            criticality=Criticality.CRITICAL,
            data_classification=DataClassification.RESTRICTED,
            internet_exposed=True,
            logging_enabled=True,
        ),
    )


def test_create_risk_record_pulls_criticality_from_asset(db_session, critical_asset):
    record = risk_service.create_risk_record(
        db_session,
        dict(
            title="Unpatched dependency",
            description="A moderate-severity dependency vulnerability.",
            asset_id=critical_asset.id,
            threat_severity="medium",
        ),
    )
    assert record.asset_criticality == "critical"
    assert record.data_classification == "restricted"
    assert record.internet_exposed is True
    assert record.inherent_score > 0


def test_create_risk_record_unknown_asset_raises():
    db = SessionLocal()
    try:
        with pytest.raises(ValueError):
            risk_service.create_risk_record(
                db,
                dict(
                    title="x",
                    description="x",
                    asset_id=999999,
                    threat_severity="low",
                ),
            )
    finally:
        db.close()


def test_list_risk_records_sorted_by_residual_score_desc(db_session, critical_asset):
    risk_service.create_risk_record(
        db_session,
        dict(title="Low severity", description="d", asset_id=critical_asset.id, threat_severity="low"),
    )
    risk_service.create_risk_record(
        db_session,
        dict(
            title="Critical severity",
            description="d",
            asset_id=critical_asset.id,
            threat_severity="critical",
            known_exploited=True,
        ),
    )
    results = risk_service.list_risk_records(db_session)
    assert results[0].title == "Critical severity"
    assert results[0].residual_score >= results[1].residual_score


def test_update_treatment_records_decision(db_session, critical_asset):
    record = risk_service.create_risk_record(
        db_session,
        dict(title="x", description="d", asset_id=critical_asset.id, threat_severity="high"),
    )
    updated = risk_service.update_treatment(
        db_session,
        record,
        dict(
            treatment_decision=TreatmentDecision.MITIGATE,
            treatment_reason="Patch scheduled for next maintenance window.",
            owner="Platform Engineering",
            target_date=None,
            status=RiskStatus.TREATMENT_IN_PROGRESS,
        ),
    )
    assert updated.treatment_decision == TreatmentDecision.MITIGATE
    assert updated.status == RiskStatus.TREATMENT_IN_PROGRESS
