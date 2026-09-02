from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.appsec import FindingStatus
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.appsec import (
    AppSecFindingCreate,
    AppSecFindingRead,
    SecretFindingRead,
    SecretScanRequest,
)
from app.services import appsec as appsec_service

router = APIRouter(prefix="/app-security", tags=["app-security"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/findings", response_model=list[AppSecFindingRead])
def list_findings(
    status_filter: FindingStatus | None = None, db: Session = Depends(get_db), _user=require_read
):
    return appsec_service.list_appsec_findings(db, status_filter)


@router.post("/findings", response_model=AppSecFindingRead, status_code=201)
def create_finding(payload: AppSecFindingCreate, db: Session = Depends(get_db), _user=require_write):
    return appsec_service.create_appsec_finding(db, payload.model_dump())


@router.patch("/findings/{finding_id}/status", response_model=AppSecFindingRead)
def update_status(
    finding_id: int, status: FindingStatus, db: Session = Depends(get_db), _user=require_write
):
    finding = appsec_service.get_appsec_finding(db, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return appsec_service.update_appsec_status(db, finding, status)


@router.get("/secrets", response_model=list[SecretFindingRead])
def list_secrets(db: Session = Depends(get_db), _user=require_read):
    return appsec_service.list_secret_findings(db)


@router.post("/secrets/scan", response_model=list[SecretFindingRead], status_code=201)
def scan_for_secrets(payload: SecretScanRequest, db: Session = Depends(get_db), _user=require_write):
    """Runs the regex-based detector over the submitted text and persists
    any matches found. Intended for pasting a config file or code snippet
    to check before committing it - see docs/decisions/0007-app-security-route.md.
    """
    return appsec_service.scan_and_record(db, payload.text, payload.location, payload.exposure)
