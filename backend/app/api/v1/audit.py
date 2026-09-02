from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.control import AuditLogEntryRead
from app.services import audit as audit_service

router = APIRouter(prefix="/audit-log", tags=["audit-log"])

# Audit log is read-only via the API by design - entries are only ever
# created as a side effect of another service's state-changing action
# (see app/services/risk.py, controls.py, incident.py), never directly.
require_read = Depends(require_role(ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER))


@router.get("", response_model=list[AuditLogEntryRead])
def list_audit_log(
    object_type: str | None = None,
    object_id: int | None = None,
    db: Session = Depends(get_db),
    _user=require_read,
):
    return audit_service.list_entries(db, object_type, object_id)
