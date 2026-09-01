from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.cloud import CloudFindingStatus
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.cloud import CloudFindingCreate, CloudFindingRead
from app.services import cloud as cloud_service

router = APIRouter(prefix="/cloud", tags=["cloud"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/findings", response_model=list[CloudFindingRead])
def list_findings(
    status_filter: CloudFindingStatus | None = None, db: Session = Depends(get_db), _user=require_read
):
    return cloud_service.list_findings(db, status_filter)


@router.post("/findings", response_model=CloudFindingRead, status_code=201)
def create_finding(payload: CloudFindingCreate, db: Session = Depends(get_db), _user=require_write):
    return cloud_service.create_finding(db, payload.model_dump())


@router.patch("/findings/{finding_id}/status", response_model=CloudFindingRead)
def update_status(
    finding_id: int, status: CloudFindingStatus, db: Session = Depends(get_db), _user=require_write
):
    finding = cloud_service.get_finding(db, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return cloud_service.update_finding_status(db, finding, status)
