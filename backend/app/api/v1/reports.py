from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.dashboard import ExecutiveReportRead
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/reports", tags=["reports"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
require_read = Depends(require_role(*READ_ROLES))


@router.get("/executive-summary", response_model=ExecutiveReportRead)
def get_executive_report(db: Session = Depends(get_db), _user=require_read):
    summary = dashboard_service.build_executive_summary(db)
    return ExecutiveReportRead(
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        top_risks=dashboard_service.top_risk_highlights(db),
        top_control_gaps=dashboard_service.top_control_gap_highlights(db),
        top_ai_findings=dashboard_service.top_ai_highlights(db),
        recommended_actions=dashboard_service.recommended_actions(summary),
    )
