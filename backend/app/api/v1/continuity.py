from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.continuity import ContinuityFindingRead, ContinuityPlanCreate, ContinuityPlanRead
from app.services import continuity as continuity_service

router = APIRouter(prefix="/business-continuity", tags=["business-continuity"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/plans", response_model=list[ContinuityPlanRead])
def list_plans(db: Session = Depends(get_db), _user=require_read):
    return continuity_service.list_plans(db)


@router.post("/plans", response_model=ContinuityPlanRead, status_code=201)
def create_plan(payload: ContinuityPlanCreate, db: Session = Depends(get_db), _user=require_write):
    return continuity_service.create_plan(db, payload.model_dump())


@router.get("/findings", response_model=list[ContinuityFindingRead])
def list_findings(db: Session = Depends(get_db), _user=require_read):
    return continuity_service.analyze_continuity(db)
