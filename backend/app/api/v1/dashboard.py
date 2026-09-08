from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.dashboard import ExecutiveSummaryRead
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
require_read = Depends(require_role(*READ_ROLES))


@router.get("/summary", response_model=ExecutiveSummaryRead)
def get_summary(db: Session = Depends(get_db), _user=require_read):
    return dashboard_service.build_executive_summary(db)
