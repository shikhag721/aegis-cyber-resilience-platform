from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.models.vulnerability import RemediationStatus
from app.schemas.risk import RiskRecordRead
from app.schemas.vulnerability import (
    VulnerabilityAssessRequest,
    VulnerabilityCreate,
    VulnerabilityRead,
    VulnerabilityUpdate,
)
from app.services import vulnerability as vuln_service

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[VulnerabilityRead])
def list_vulnerabilities(
    asset_id: int | None = None,
    remediation_status: RemediationStatus | None = None,
    db: Session = Depends(get_db),
    _user=require_read,
):
    return vuln_service.list_vulnerabilities(db, asset_id, remediation_status)


@router.post("", response_model=VulnerabilityRead, status_code=status.HTTP_201_CREATED)
def create_vulnerability(
    payload: VulnerabilityCreate, db: Session = Depends(get_db), _user=require_write
):
    return vuln_service.create_vulnerability(db, payload.model_dump())


@router.get("/{vuln_id}", response_model=VulnerabilityRead)
def get_vulnerability(vuln_id: int, db: Session = Depends(get_db), _user=require_read):
    vuln = vuln_service.get_vulnerability(db, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln


@router.patch("/{vuln_id}", response_model=VulnerabilityRead)
def update_vulnerability(
    vuln_id: int, payload: VulnerabilityUpdate, db: Session = Depends(get_db), _user=require_write
):
    vuln = vuln_service.get_vulnerability(db, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln_service.update_vulnerability(db, vuln, payload.model_dump(exclude_unset=True))


@router.post("/{vuln_id}/assess", response_model=RiskRecordRead, status_code=status.HTTP_201_CREATED)
def assess_vulnerability(
    vuln_id: int,
    payload: VulnerabilityAssessRequest,
    db: Session = Depends(get_db),
    _user=require_write,
):
    vuln = vuln_service.get_vulnerability(db, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln_service.assess_vulnerability(
        db, vuln, payload.control_effectiveness, payload.risk_appetite
    )
