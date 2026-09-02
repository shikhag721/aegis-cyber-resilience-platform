from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.risk import RiskStatus
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.risk import RiskAssessRequest, RiskRecordRead, RiskTreatmentUpdate
from app.services import risk as risk_service

router = APIRouter(prefix="/risk-register", tags=["risk-register"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[RiskRecordRead])
def list_risk_records(
    asset_id: int | None = None,
    status_filter: RiskStatus | None = None,
    db: Session = Depends(get_db),
    _user=require_read,
):
    return risk_service.list_risk_records(db, asset_id, status_filter)


@router.post("", response_model=RiskRecordRead, status_code=status.HTTP_201_CREATED)
def create_risk_record(payload: RiskAssessRequest, db: Session = Depends(get_db), _user=require_write):
    try:
        return risk_service.create_risk_record(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{risk_id}", response_model=RiskRecordRead)
def get_risk_record(risk_id: int, db: Session = Depends(get_db), _user=require_read):
    record = risk_service.get_risk_record(db, risk_id)
    if not record:
        raise HTTPException(status_code=404, detail="Risk record not found")
    return record


@router.patch("/{risk_id}/treatment", response_model=RiskRecordRead)
def update_treatment(
    risk_id: int, payload: RiskTreatmentUpdate, db: Session = Depends(get_db), current_user=require_write
):
    record = risk_service.get_risk_record(db, risk_id)
    if not record:
        raise HTTPException(status_code=404, detail="Risk record not found")
    return risk_service.update_treatment(db, record, payload.model_dump(), actor=current_user.username)
