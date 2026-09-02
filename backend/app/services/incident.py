"""Incident Response lifecycle management (Section 16)."""
from sqlalchemy.orm import Session, joinedload

from app.models.incident import STAGE_ORDER, Incident, IncidentStage, IncidentTimelineEntry
from app.services import audit as audit_service


def create_incident(db: Session, data: dict) -> Incident:
    incident = Incident(**data)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    add_timeline_entry(db, incident, IncidentStage.DETECTION, "Incident detected and logged.")
    return incident


def get_incident(db: Session, incident_id: int) -> Incident | None:
    return (
        db.query(Incident)
        .options(joinedload(Incident.timeline))
        .filter(Incident.id == incident_id)
        .first()
    )


def list_incidents(db: Session) -> list[Incident]:
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    incidents = db.query(Incident).options(joinedload(Incident.timeline)).all()
    return sorted(incidents, key=lambda i: severity_rank.get(i.severity.value, 4))


def add_timeline_entry(
    db: Session, incident: Incident, stage: IncidentStage, description: str
) -> IncidentTimelineEntry:
    entry = IncidentTimelineEntry(incident_id=incident.id, stage=stage, description=description)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def advance_stage(db: Session, incident: Incident, description: str, actor: str = "system") -> Incident:
    """Moves the incident to the NEXT stage in STAGE_ORDER only - lifecycle
    stages cannot be skipped or reordered, matching how a real IR process
    requires each phase to actually be worked, not just labeled.
    """
    current_index = STAGE_ORDER.index(incident.stage)
    if current_index >= len(STAGE_ORDER) - 1:
        raise ValueError(f"Incident is already at its final stage ({incident.stage.value}).")

    old_stage = incident.stage
    next_stage = STAGE_ORDER[current_index + 1]
    incident.stage = next_stage
    db.commit()
    db.refresh(incident)
    add_timeline_entry(db, incident, next_stage, description)
    audit_service.record(
        db,
        actor=actor,
        action="incident_stage_advance",
        object_type="Incident",
        object_id=incident.id,
        old_value={"stage": old_stage.value},
        new_value={"stage": next_stage.value},
        reason=description,
    )
    return incident


def update_incident_fields(db: Session, incident: Incident, changes: dict) -> Incident:
    for field, value in changes.items():
        if value is not None:
            setattr(incident, field, value)
    db.commit()
    db.refresh(incident)
    return incident
