from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.ai import AISystemCreate, AISystemRead
from app.services import ai as ai_service

router = APIRouter(prefix="/ai-inventory", tags=["ai-inventory"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[AISystemRead])
def list_ai_systems(db: Session = Depends(get_db), _user=require_read):
    return ai_service.list_ai_systems(db)


@router.post("", response_model=AISystemRead, status_code=201)
def create_ai_system(payload: AISystemCreate, db: Session = Depends(get_db), _user=require_write):
    ai_system = ai_service.create_ai_system(db, payload.model_dump())
    return ai_service.get_ai_system(db, ai_system.id)


@router.get("/{ai_system_id}", response_model=AISystemRead)
def get_ai_system(ai_system_id: int, db: Session = Depends(get_db), _user=require_read):
    ai_system = ai_service.get_ai_system(db, ai_system_id)
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI system not found")
    return ai_system
