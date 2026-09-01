import pytest

from app.db.session import SessionLocal
from app.models.cloud import CloudFindingSeverity, CloudFindingStatus, CloudFindingType
from app.services import cloud as cloud_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _finding(**overrides) -> dict:
    defaults = dict(
        resource_name="test-bucket",
        finding_type=CloudFindingType.PUBLIC_EXPOSURE,
        severity=CloudFindingSeverity.HIGH,
        description="d",
        recommendation="r",
    )
    defaults.update(overrides)
    return defaults


def test_list_findings_sorted_by_severity_desc(db_session):
    cloud_service.create_finding(db_session, _finding(resource_name="low", severity=CloudFindingSeverity.LOW))
    cloud_service.create_finding(
        db_session, _finding(resource_name="crit", severity=CloudFindingSeverity.CRITICAL)
    )
    results = cloud_service.list_findings(db_session)
    assert results[0].resource_name == "crit"


def test_update_finding_status(db_session):
    finding = cloud_service.create_finding(db_session, _finding())
    updated = cloud_service.update_finding_status(db_session, finding, CloudFindingStatus.REMEDIATED)
    assert updated.status == CloudFindingStatus.REMEDIATED


def test_filter_findings_by_status(db_session):
    f1 = cloud_service.create_finding(db_session, _finding(resource_name="a"))
    cloud_service.create_finding(db_session, _finding(resource_name="b"))
    cloud_service.update_finding_status(db_session, f1, CloudFindingStatus.REMEDIATED)

    open_findings = cloud_service.list_findings(db_session, CloudFindingStatus.OPEN)
    assert len(open_findings) == 1
    assert open_findings[0].resource_name == "b"
