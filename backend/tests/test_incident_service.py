import pytest

from app.db.session import SessionLocal
from app.models.incident import STAGE_ORDER, IncidentSeverity, IncidentStage
from app.services import incident as incident_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _incident(**overrides) -> dict:
    defaults = dict(
        title="Compromised privileged account",
        description="Anomalous login pattern detected for a.singh.",
        severity=IncidentSeverity.CRITICAL,
        affected_asset_ids=[],
        indicators=["failed_login", "successful_login", "unusual_location"],
        recommended_containment="Force password reset and revoke active sessions.",
    )
    defaults.update(overrides)
    return defaults


def test_create_incident_starts_at_detection_with_timeline_entry(db_session):
    incident = incident_service.create_incident(db_session, _incident())
    assert incident.stage == IncidentStage.DETECTION
    fetched = incident_service.get_incident(db_session, incident.id)
    assert len(fetched.timeline) == 1
    assert fetched.timeline[0].stage == IncidentStage.DETECTION


def test_advance_stage_moves_forward_one_step(db_session):
    incident = incident_service.create_incident(db_session, _incident())
    updated = incident_service.advance_stage(db_session, incident, "Triaged as high priority.")
    assert updated.stage == IncidentStage.TRIAGE

    fetched = incident_service.get_incident(db_session, incident.id)
    assert len(fetched.timeline) == 2
    assert fetched.timeline[1].stage == IncidentStage.TRIAGE


def test_advance_stage_cannot_skip_stages(db_session):
    """Guards the Section 16 lifecycle - advance_stage only ever moves to
    the NEXT stage in STAGE_ORDER, never an arbitrary one.
    """
    incident = incident_service.create_incident(db_session, _incident())
    updated = incident_service.advance_stage(db_session, incident, "Moving to triage.")
    assert STAGE_ORDER.index(updated.stage) == STAGE_ORDER.index(IncidentStage.DETECTION) + 1


def test_cannot_advance_past_final_stage(db_session):
    incident = incident_service.create_incident(db_session, _incident())
    for _ in range(len(STAGE_ORDER) - 1):
        incident = incident_service.advance_stage(db_session, incident, "Progressing.")
    assert incident.stage == IncidentStage.LESSONS_LEARNED

    with pytest.raises(ValueError):
        incident_service.advance_stage(db_session, incident, "Trying to go further.")


def test_list_incidents_sorted_by_severity(db_session):
    incident_service.create_incident(db_session, _incident(title="low one", severity=IncidentSeverity.LOW))
    incident_service.create_incident(
        db_session, _incident(title="critical one", severity=IncidentSeverity.CRITICAL)
    )
    results = incident_service.list_incidents(db_session)
    assert results[0].title == "critical one"


def test_update_incident_fields(db_session):
    incident = incident_service.create_incident(db_session, _incident())
    updated = incident_service.update_incident_fields(
        db_session, incident, {"remediation": "Reset credentials and enabled MFA.", "lessons_learned": None}
    )
    assert updated.remediation == "Reset credentials and enabled MFA."
