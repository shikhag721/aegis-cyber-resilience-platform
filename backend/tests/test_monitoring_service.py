from datetime import datetime, timedelta, timezone

import pytest

from app.db.session import SessionLocal
from app.models.monitoring import SecurityEventType
from app.services import monitoring as monitoring_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _event_at(username: str, event_type: SecurityEventType, offset_minutes: int) -> dict:
    base = datetime.now(timezone.utc)
    return dict(
        event_type=event_type,
        username=username,
        occurred_at=base + timedelta(minutes=offset_minutes),
    )


def test_isolated_event_produces_no_finding(db_session):
    monitoring_service.create_event(db_session, _event_at("u1", SecurityEventType.DATABASE_ACCESS, 0))
    findings = monitoring_service.correlate(db_session)
    assert findings == []


def test_full_compromise_chain_detected_as_critical(db_session):
    monitoring_service.create_event(db_session, _event_at("u2", SecurityEventType.FAILED_LOGIN, 0))
    monitoring_service.create_event(db_session, _event_at("u2", SecurityEventType.FAILED_LOGIN, 2))
    monitoring_service.create_event(db_session, _event_at("u2", SecurityEventType.SUCCESSFUL_LOGIN, 5))
    monitoring_service.create_event(db_session, _event_at("u2", SecurityEventType.UNUSUAL_LOCATION, 6))
    monitoring_service.create_event(db_session, _event_at("u2", SecurityEventType.DATABASE_ACCESS, 10))

    findings = monitoring_service.correlate(db_session)
    assert len(findings) == 1
    assert findings[0].username == "u2"
    assert findings[0].severity == "critical"


def test_partial_chain_without_data_access_is_high_not_critical(db_session):
    monitoring_service.create_event(db_session, _event_at("u3", SecurityEventType.FAILED_LOGIN, 0))
    monitoring_service.create_event(db_session, _event_at("u3", SecurityEventType.SUCCESSFUL_LOGIN, 5))
    monitoring_service.create_event(db_session, _event_at("u3", SecurityEventType.PRIVILEGE_ESCALATION, 6))

    findings = monitoring_service.correlate(db_session)
    assert len(findings) == 1
    assert findings[0].severity == "high"


def test_events_outside_correlation_window_not_linked(db_session):
    monitoring_service.create_event(db_session, _event_at("u4", SecurityEventType.FAILED_LOGIN, 0))
    # 25 hours later - outside the 24h correlation window
    monitoring_service.create_event(
        db_session, _event_at("u4", SecurityEventType.SUCCESSFUL_LOGIN, 25 * 60)
    )
    monitoring_service.create_event(
        db_session, _event_at("u4", SecurityEventType.UNUSUAL_LOCATION, 25 * 60 + 5)
    )

    findings = monitoring_service.correlate(db_session)
    assert findings == []


def test_successful_login_only_account_not_flagged(db_session):
    monitoring_service.create_event(db_session, _event_at("u5", SecurityEventType.SUCCESSFUL_LOGIN, 0))
    monitoring_service.create_event(db_session, _event_at("u5", SecurityEventType.DATABASE_ACCESS, 5))
    findings = monitoring_service.correlate(db_session)
    assert findings == []


def test_findings_sorted_by_severity(db_session):
    # High severity account
    monitoring_service.create_event(db_session, _event_at("high1", SecurityEventType.FAILED_LOGIN, 0))
    monitoring_service.create_event(db_session, _event_at("high1", SecurityEventType.SUCCESSFUL_LOGIN, 5))
    monitoring_service.create_event(
        db_session, _event_at("high1", SecurityEventType.PRIVILEGE_ESCALATION, 6)
    )
    # Critical severity account
    monitoring_service.create_event(db_session, _event_at("crit1", SecurityEventType.FAILED_LOGIN, 0))
    monitoring_service.create_event(db_session, _event_at("crit1", SecurityEventType.SUCCESSFUL_LOGIN, 5))
    monitoring_service.create_event(
        db_session, _event_at("crit1", SecurityEventType.UNUSUAL_LOCATION, 6)
    )
    monitoring_service.create_event(
        db_session, _event_at("crit1", SecurityEventType.UNUSUAL_DATA_TRANSFER, 10)
    )

    findings = monitoring_service.correlate(db_session)
    assert findings[0].username == "crit1"
    assert findings[0].severity == "critical"
