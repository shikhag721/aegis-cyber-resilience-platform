from datetime import date, timedelta

import pytest

from app.db.session import SessionLocal
from app.models.asset import AssetType, Criticality, DataClassification, Environment
from app.services import asset as asset_service
from app.services import continuity as continuity_service
from app.services import data_security as data_security_service


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
            asset_tag="AST-P9-1",
            name="Test Customer Database",
            asset_type=AssetType.DATABASE,
            owner="o",
            business_unit="bu",
            environment=Environment.PRODUCTION,
            criticality=Criticality.CRITICAL,
            data_classification=DataClassification.RESTRICTED,
        ),
    )


def test_unencrypted_sensitive_data_flagged_critical(db_session, critical_asset):
    data_security_service.create_data_asset(
        db_session,
        dict(
            name="Customer PII",
            category="pii",
            classification="restricted",
            asset_id=critical_asset.id,
            encrypted=False,
            access_controlled=True,
            retention_defined=True,
        ),
    )
    findings = data_security_service.analyze_data_security(db_session)
    assert any(f.finding_type == "unencrypted_sensitive_data" for f in findings)


def test_encrypted_sensitive_data_not_flagged(db_session, critical_asset):
    data_security_service.create_data_asset(
        db_session,
        dict(
            name="Customer PII",
            category="pii",
            classification="restricted",
            asset_id=critical_asset.id,
            encrypted=True,
            access_controlled=True,
            retention_defined=True,
        ),
    )
    findings = data_security_service.analyze_data_security(db_session)
    assert not any(f.finding_type == "unencrypted_sensitive_data" for f in findings)


def test_missing_retention_policy_flagged(db_session, critical_asset):
    data_security_service.create_data_asset(
        db_session,
        dict(
            name="Internal business data",
            category="business_data",
            classification="internal",
            asset_id=critical_asset.id,
            encrypted=True,
            access_controlled=True,
            retention_defined=False,
        ),
    )
    findings = data_security_service.analyze_data_security(db_session)
    assert any(f.finding_type == "no_retention_policy" for f in findings)


def test_missing_rto_rpo_flagged_for_critical_asset(db_session, critical_asset):
    continuity_service.create_plan(db_session, dict(asset_id=critical_asset.id))
    findings = continuity_service.analyze_continuity(db_session)
    assert any(f.finding_type == "missing_rto_rpo" and f.severity == "high" for f in findings)


def test_recent_tests_not_flagged(db_session, critical_asset):
    continuity_service.create_plan(
        db_session,
        dict(
            asset_id=critical_asset.id,
            rto_hours=4,
            rpo_hours=1,
            last_backup_tested_at=date.today() - timedelta(days=10),
            last_dr_test_at=date.today() - timedelta(days=30),
        ),
    )
    findings = continuity_service.analyze_continuity(db_session)
    stale_types = ("missing_rto_rpo", "stale_backup_test", "stale_dr_test")
    assert not any(f.finding_type in stale_types for f in findings)


def test_stale_dr_test_flagged_critical_for_critical_asset(db_session, critical_asset):
    continuity_service.create_plan(
        db_session,
        dict(
            asset_id=critical_asset.id,
            rto_hours=4,
            rpo_hours=1,
            last_backup_tested_at=date.today(),
            last_dr_test_at=date.today() - timedelta(days=400),
        ),
    )
    findings = continuity_service.analyze_continuity(db_session)
    match = next(f for f in findings if f.finding_type == "stale_dr_test")
    assert match.severity == "critical"
