from datetime import date, timedelta

import pytest

from app.db.session import SessionLocal
from app.models.control import EvidenceStatus
from app.services import controls as controls_service
from app.services import evidence as evidence_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def assessment(db_session):
    control = controls_service.create_control(
        db_session,
        dict(
            control_id="CTRL-EV-1",
            title="x",
            description="d",
            control_objective="o",
            framework_reference="r",
            test_procedure="t",
        ),
    )
    return controls_service.create_assessment(db_session, dict(control_id=control.id))


def test_create_and_list_evidence(db_session, assessment):
    evidence_service.create_evidence(
        db_session,
        assessment.id,
        dict(evidence_type="Access review", source="Okta", collected_at=date.today()),
    )
    results = evidence_service.list_evidence(db_session, assessment.id)
    assert len(results) == 1


def test_refresh_expired_status_flips_past_due_valid_evidence(db_session, assessment):
    ev = evidence_service.create_evidence(
        db_session,
        assessment.id,
        dict(
            evidence_type="Access review",
            source="Okta",
            collected_at=date.today() - timedelta(days=200),
            valid_until=date.today() - timedelta(days=10),
            status=EvidenceStatus.VALID,
        ),
    )
    updated_count = evidence_service.refresh_expired_status(db_session)
    assert updated_count == 1
    refreshed = evidence_service.get_evidence(db_session, ev.id)
    assert refreshed.status == EvidenceStatus.EXPIRED


def test_refresh_expired_status_leaves_current_evidence_alone(db_session, assessment):
    ev = evidence_service.create_evidence(
        db_session,
        assessment.id,
        dict(
            evidence_type="Access review",
            source="Okta",
            collected_at=date.today(),
            valid_until=date.today() + timedelta(days=30),
            status=EvidenceStatus.VALID,
        ),
    )
    evidence_service.refresh_expired_status(db_session)
    refreshed = evidence_service.get_evidence(db_session, ev.id)
    assert refreshed.status == EvidenceStatus.VALID


def test_mark_status(db_session, assessment):
    ev = evidence_service.create_evidence(
        db_session,
        assessment.id,
        dict(evidence_type="x", source="x", collected_at=date.today()),
    )
    updated = evidence_service.mark_status(db_session, ev, EvidenceStatus.VALID)
    assert updated.status == EvidenceStatus.VALID
