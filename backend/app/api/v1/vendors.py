from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.vendor import VendorAssessmentRead, VendorCreate, VendorRead
from app.services import vendor as vendor_service

router = APIRouter(prefix="/vendors", tags=["vendors"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[VendorRead])
def list_vendors(db: Session = Depends(get_db), _user=require_read):
    return vendor_service.list_vendors(db)


@router.post("", response_model=VendorRead, status_code=201)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db), _user=require_write):
    return vendor_service.create_vendor(db, payload.model_dump())


@router.get("/{vendor_id}", response_model=VendorRead)
def get_vendor(vendor_id: int, db: Session = Depends(get_db), _user=require_read):
    vendor = vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.get("/{vendor_id}/assessments/latest", response_model=VendorAssessmentRead)
def get_latest_assessment(vendor_id: int, db: Session = Depends(get_db), _user=require_read):
    assessment = vendor_service.latest_assessment(db, vendor_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment on file for this vendor")
    return assessment


@router.post("/{vendor_id}/assessments", response_model=VendorAssessmentRead, status_code=201)
def create_assessment(vendor_id: int, db: Session = Depends(get_db), _user=require_write):
    vendor = vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor_service.run_assessment(db, vendor)
