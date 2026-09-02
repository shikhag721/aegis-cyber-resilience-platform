from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.data_security import DataAssetCreate, DataAssetRead, DataSecurityFindingRead
from app.services import data_security as data_security_service

router = APIRouter(prefix="/data-security", tags=["data-security"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/data-assets", response_model=list[DataAssetRead])
def list_data_assets(db: Session = Depends(get_db), _user=require_read):
    return data_security_service.list_data_assets(db)


@router.post("/data-assets", response_model=DataAssetRead, status_code=201)
def create_data_asset(payload: DataAssetCreate, db: Session = Depends(get_db), _user=require_write):
    return data_security_service.create_data_asset(db, payload.model_dump())


@router.get("/findings", response_model=list[DataSecurityFindingRead])
def list_findings(db: Session = Depends(get_db), _user=require_read):
    return data_security_service.analyze_data_security(db)
