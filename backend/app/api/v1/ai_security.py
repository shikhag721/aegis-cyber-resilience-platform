from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.ai import AIInventoryFindingRead, AISecurityFindingCreate, AISecurityFindingRead
from app.services import ai as ai_service

router = APIRouter(prefix="/ai-security", tags=["ai-security"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/findings", response_model=list[AISecurityFindingRead])
def list_all_findings(db: Session = Depends(get_db), _user=require_read):
    return ai_service.list_all_findings(db)


@router.post(
    "/ai-systems/{ai_system_id}/findings", response_model=AISecurityFindingRead, status_code=201
)
def create_finding(
    ai_system_id: int, payload: AISecurityFindingCreate, db: Session = Depends(get_db), _user=require_write
):
    if not ai_service.get_ai_system(db, ai_system_id):
        raise HTTPException(status_code=404, detail="AI system not found")
    return ai_service.create_finding(db, ai_system_id, payload.model_dump())


@router.get("/gap-analysis", response_model=list[AIInventoryFindingRead])
def gap_analysis(db: Session = Depends(get_db), _user=require_read):
    return ai_service.analyze_ai_inventory(db)
