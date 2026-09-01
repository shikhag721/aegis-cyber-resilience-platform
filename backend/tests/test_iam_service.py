from datetime import datetime, timedelta, timezone

import pytest

from app.db.session import SessionLocal
from app.models.identity import AccountType, EmploymentStatus
from app.services import iam as iam_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _account(**overrides) -> dict:
    defaults = dict(
        username="jdoe",
        display_name="Jane Doe",
        account_type=AccountType.HUMAN,
        department="Engineering",
        employment_status=EmploymentStatus.ACTIVE,
        is_enabled=True,
        is_privileged=False,
        mfa_enabled=True,
        production_access=False,
        permissions=[],
        # Recent login by default so tests targeting a different finding type
        # don't also incidentally trip the inactive-account rule.
        last_login_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    defaults.update(overrides)
    return defaults


def test_orphan_account_detected(db_session):
    iam_service.create_identity_account(
        db_session, _account(username="left1", employment_status=EmploymentStatus.TERMINATED, is_enabled=True)
    )
    findings = iam_service.analyze(db_session)
    assert any(f.finding_type == "orphan_account" and f.account_username == "left1" for f in findings)


def test_terminated_but_disabled_account_not_flagged_as_orphan(db_session):
    iam_service.create_identity_account(
        db_session,
        _account(username="left2", employment_status=EmploymentStatus.TERMINATED, is_enabled=False),
    )
    findings = iam_service.analyze(db_session)
    assert not any(f.account_username == "left2" for f in findings)


def test_privileged_without_mfa_flagged_critical(db_session):
    iam_service.create_identity_account(
        db_session, _account(username="priv1", is_privileged=True, mfa_enabled=False)
    )
    findings = iam_service.analyze(db_session)
    match = next(f for f in findings if f.account_username == "priv1")
    assert match.finding_type == "missing_mfa"
    assert match.severity == "critical"


def test_inactive_account_detected(db_session):
    old_login = datetime.now(timezone.utc) - timedelta(days=200)
    iam_service.create_identity_account(db_session, _account(username="stale1", last_login_at=old_login))
    findings = iam_service.analyze(db_session)
    assert any(f.finding_type == "inactive_account" and f.account_username == "stale1" for f in findings)


def test_recent_login_not_flagged_inactive(db_session):
    recent_login = datetime.now(timezone.utc) - timedelta(days=5)
    iam_service.create_identity_account(db_session, _account(username="fresh1", last_login_at=recent_login))
    findings = iam_service.analyze(db_session)
    assert not any(f.account_username == "fresh1" for f in findings)


def test_inappropriate_production_access_detected(db_session):
    iam_service.create_identity_account(
        db_session,
        _account(username="mkt1", department="Marketing", production_access=True, is_privileged=False),
    )
    findings = iam_service.analyze(db_session)
    assert any(f.finding_type == "inappropriate_production_access" for f in findings)


def test_production_access_in_eligible_department_not_flagged(db_session):
    iam_service.create_identity_account(
        db_session,
        _account(
            username="eng1",
            department="Platform Engineering",
            production_access=True,
            is_privileged=False,
        ),
    )
    findings = iam_service.analyze(db_session)
    assert not any(f.finding_type == "inappropriate_production_access" for f in findings)


def test_service_account_privilege_escalation_path(db_session):
    iam_service.create_identity_account(
        db_session,
        _account(
            username="svc1",
            account_type=AccountType.SERVICE,
            department="Platform Engineering",
            is_privileged=True,
            production_access=True,
            mfa_enabled=False,
        ),
    )
    findings = iam_service.analyze(db_session)
    assert any(f.finding_type == "privilege_escalation_path" for f in findings)


def test_conflicting_privileges_detected(db_session):
    iam_service.create_identity_account(
        db_session,
        _account(username="fin1", permissions=["initiate_payment", "approve_payment"]),
    )
    findings = iam_service.analyze(db_session)
    assert any(f.finding_type == "conflicting_privileges" and f.account_username == "fin1" for f in findings)


def test_single_permission_not_flagged_as_conflict(db_session):
    iam_service.create_identity_account(
        db_session, _account(username="fin2", permissions=["initiate_payment"])
    )
    findings = iam_service.analyze(db_session)
    assert not any(f.account_username == "fin2" for f in findings)


def test_findings_sorted_by_severity(db_session):
    stale_login = datetime.now(timezone.utc) - timedelta(days=200)
    iam_service.create_identity_account(db_session, _account(username="stale2", last_login_at=stale_login))
    iam_service.create_identity_account(
        db_session, _account(username="priv2", is_privileged=True, mfa_enabled=False)
    )
    findings = iam_service.analyze(db_session)
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ranks = [severity_rank[f.severity] for f in findings]
    assert ranks == sorted(ranks)
