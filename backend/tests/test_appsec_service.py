import pytest

from app.db.session import SessionLocal
from app.models.appsec import AppSecFindingType, FindingSeverity, FindingStatus
from app.services import appsec as appsec_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _finding(**overrides) -> dict:
    defaults = dict(
        resource_name="POST /api/v1/accounts/{id}/transfer",
        finding_type=AppSecFindingType.BROKEN_AUTHORIZATION,
        severity=FindingSeverity.HIGH,
        description="d",
        owasp_reference="OWASP API1:2023",
        recommendation="r",
    )
    defaults.update(overrides)
    return defaults


def test_list_findings_sorted_by_severity(db_session):
    appsec_service.create_appsec_finding(
        db_session, _finding(resource_name="low", severity=FindingSeverity.LOW)
    )
    appsec_service.create_appsec_finding(
        db_session, _finding(resource_name="crit", severity=FindingSeverity.CRITICAL)
    )
    results = appsec_service.list_appsec_findings(db_session)
    assert results[0].resource_name == "crit"


def test_update_status(db_session):
    finding = appsec_service.create_appsec_finding(db_session, _finding())
    updated = appsec_service.update_appsec_status(db_session, finding, FindingStatus.REMEDIATED)
    assert updated.status == FindingStatus.REMEDIATED


def test_scan_and_record_persists_findings(db_session):
    text = "aws_key = 'AKIAIOSFODNN7EXAMPLE'"
    findings = appsec_service.scan_and_record(db_session, text, "config.py", "Internal repo")
    assert len(findings) == 1
    persisted = appsec_service.list_secret_findings(db_session)
    assert len(persisted) == 1
    assert "AKIAIOSFODNN7EXAMPLE" not in persisted[0].redacted_snippet


def test_scan_and_record_no_matches_creates_nothing(db_session):
    findings = appsec_service.scan_and_record(db_session, "clean code here", "app.py", "Internal repo")
    assert findings == []
