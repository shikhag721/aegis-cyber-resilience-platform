from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.identity import IAMFindingRead, IdentityAccountCreate, IdentityAccountRead
from app.services import iam as iam_service

router = APIRouter(prefix="/iam", tags=["iam"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/accounts", response_model=list[IdentityAccountRead])
def list_accounts(db: Session = Depends(get_db), _user=require_read):
    return iam_service.list_identity_accounts(db)


@router.post("/accounts", response_model=IdentityAccountRead, status_code=201)
def create_account(payload: IdentityAccountCreate, db: Session = Depends(get_db), _user=require_write):
    return iam_service.create_identity_account(db, payload.model_dump())


@router.get("/findings", response_model=list[IAMFindingRead])
def list_findings(db: Session = Depends(get_db), _user=require_read):
    return iam_service.analyze(db)
