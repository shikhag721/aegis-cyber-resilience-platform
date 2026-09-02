"""Audit log recording (Section 32).

Called by other services immediately before/alongside a state-changing
commit - see app/services/risk.py::update_treatment,
app/services/controls.py::update_assessment, and
app/services/incident.py::advance_stage for the call sites. Kept as a
single, simple `record()` function so every state change goes through one
code path rather than each service inventing its own audit format.
"""
from sqlalchemy.orm import Session

from app.models.audit import AuditLogEntry


def record(
    db: Session,
    actor: str,
    action: str,
    object_type: str,
    object_id: int,
    old_value: dict,
    new_value: dict,
    reason: str = "",
) -> AuditLogEntry:
    entry = AuditLogEntry(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=object_id,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_entries(
    db: Session, object_type: str | None = None, object_id: int | None = None
) -> list[AuditLogEntry]:
    query = db.query(AuditLogEntry)
    if object_type is not None:
        query = query.filter(AuditLogEntry.object_type == object_type)
    if object_id is not None:
        query = query.filter(AuditLogEntry.object_id == object_id)
    return query.order_by(AuditLogEntry.occurred_at.desc()).all()
