from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.control import (
    ControlAssessmentCreate,
    ControlAssessmentRead,
    ControlAssessmentUpdate,
    ControlCreate,
    ControlGapFindingRead,
    ControlRead,
)
from app.services import controls as controls_service

router = APIRouter(prefix="/controls", tags=["controls"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[ControlRead])
def list_controls(db: Session = Depends(get_db), _user=require_read):
    return controls_service.list_controls(db)


@router.post("", response_model=ControlRead, status_code=201)
def create_control(payload: ControlCreate, db: Session = Depends(get_db), _user=require_write):
    return controls_service.create_control(db, payload.model_dump())


@router.get("/assessments", response_model=list[ControlAssessmentRead])
def list_assessments(control_id: int | None = None, db: Session = Depends(get_db), _user=require_read):
    return controls_service.list_assessments(db, control_id)


@router.post("/assessments", response_model=ControlAssessmentRead, status_code=201)
def create_assessment(
    payload: ControlAssessmentCreate, db: Session = Depends(get_db), _user=require_write
):
    assessment = controls_service.create_assessment(db, payload.model_dump())
    return controls_service.get_assessment(db, assessment.id)


@router.get("/assessments/{assessment_id}", response_model=ControlAssessmentRead)
def get_assessment(assessment_id: int, db: Session = Depends(get_db), _user=require_read):
    assessment = controls_service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Control assessment not found")
    return assessment


@router.patch("/assessments/{assessment_id}", response_model=ControlAssessmentRead)
def update_assessment(
    assessment_id: int,
    payload: ControlAssessmentUpdate,
    db: Session = Depends(get_db),
    current_user=require_write,
):
    assessment = controls_service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Control assessment not found")
    changes = payload.model_dump(exclude={"reason"}, exclude_unset=True)
    controls_service.update_assessment(
        db, assessment, changes, actor=current_user.username, reason=payload.reason
    )
    return controls_service.get_assessment(db, assessment_id)


@router.get("/gap-analysis", response_model=list[ControlGapFindingRead])
def gap_analysis(db: Session = Depends(get_db), _user=require_read):
    return controls_service.analyze_control_gaps(db)
