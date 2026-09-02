from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.monitoring import CorrelationFindingRead, SecurityEventCreate, SecurityEventRead
from app.services import monitoring as monitoring_service

router = APIRouter(prefix="/security-events", tags=["monitoring"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[SecurityEventRead])
def list_events(username: str | None = None, db: Session = Depends(get_db), _user=require_read):
    return monitoring_service.list_events(db, username)


@router.post("", response_model=SecurityEventRead, status_code=201)
def create_event(payload: SecurityEventCreate, db: Session = Depends(get_db), _user=require_write):
    return monitoring_service.create_event(db, payload.model_dump())


@router.get("/correlate", response_model=list[CorrelationFindingRead])
def correlate(db: Session = Depends(get_db), _user=require_read):
    return monitoring_service.correlate(db)
