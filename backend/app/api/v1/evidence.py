from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.control import EvidenceStatus
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.control import EvidenceCreate, EvidenceRead
from app.services import evidence as evidence_service

router = APIRouter(prefix="/evidence", tags=["evidence"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[EvidenceRead])
def list_evidence(
    control_assessment_id: int | None = None, db: Session = Depends(get_db), _user=require_read
):
    evidence_service.refresh_expired_status(db)
    return evidence_service.list_evidence(db, control_assessment_id)


@router.post("", response_model=EvidenceRead, status_code=201)
def create_evidence(payload: EvidenceCreate, db: Session = Depends(get_db), _user=require_write):
    data = payload.model_dump(exclude={"control_assessment_id"})
    return evidence_service.create_evidence(db, payload.control_assessment_id, data)


@router.patch("/{evidence_id}/status", response_model=EvidenceRead)
def update_status(
    evidence_id: int, status: EvidenceStatus, db: Session = Depends(get_db), _user=require_write
):
    evidence = evidence_service.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence_service.mark_status(db, evidence, status)
