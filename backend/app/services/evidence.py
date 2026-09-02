"""Evidence management (Section 19) - evidence records always belong to a
ControlAssessment; this module is a thin, focused surface over that
relationship for the dedicated /evidence route.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models.control import Evidence, EvidenceStatus


def create_evidence(db: Session, control_assessment_id: int, data: dict) -> Evidence:
    evidence = Evidence(control_assessment_id=control_assessment_id, **data)
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def list_evidence(db: Session, control_assessment_id: int | None = None) -> list[Evidence]:
    query = db.query(Evidence)
    if control_assessment_id is not None:
        query = query.filter(Evidence.control_assessment_id == control_assessment_id)
    return query.order_by(Evidence.collected_at.desc()).all()


def get_evidence(db: Session, evidence_id: int) -> Evidence | None:
    return db.get(Evidence, evidence_id)


def mark_status(db: Session, evidence: Evidence, status: EvidenceStatus) -> Evidence:
    evidence.status = status
    db.commit()
    db.refresh(evidence)
    return evidence


def refresh_expired_status(db: Session) -> int:
    """Sweeps all evidence and flips any past-due VALID record to EXPIRED.
    Called once at the start of any evidence listing so status always
    reflects today's date, not just whatever it was set to at creation.
    """
    today = date.today()
    updated = 0
    for evidence in db.query(Evidence).filter(Evidence.status == EvidenceStatus.VALID).all():
        if evidence.valid_until and evidence.valid_until < today:
            evidence.status = EvidenceStatus.EXPIRED
            updated += 1
    if updated:
        db.commit()
    return updated
