from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.asset import AssetType, Criticality, Environment
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.asset import (
    AssetCreate,
    AssetDependencyCreate,
    AssetDependencyRead,
    AssetRead,
    AssetUpdate,
)
from app.services import asset as asset_service

router = APIRouter(prefix="/assets", tags=["assets"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)
DELETE_ROLES = (ROLE_ADMIN,)

# Built once at import time (not inside a function signature) - ruff/bugbear
# flags a bare `Depends(require_role(...))` default as a function call in an
# argument default; a module-level singleton is the idiomatic fix and also
# means the role tuple is only parsed into a dependency once.
require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))
require_delete = Depends(require_role(*DELETE_ROLES))


@router.get("", response_model=list[AssetRead])
def list_assets(
    search: str | None = None,
    asset_type: AssetType | None = None,
    environment: Environment | None = None,
    criticality: Criticality | None = None,
    internet_exposed: bool | None = None,
    db: Session = Depends(get_db),
    _user=require_read,
):
    return asset_service.list_assets(db, search, asset_type, environment, criticality, internet_exposed)


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), _user=require_write):
    return asset_service.create_asset(db, payload.model_dump())


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db), _user=require_read):
    asset = asset_service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset(
    asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db), _user=require_write
):
    asset = asset_service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset_service.update_asset(db, asset, payload.model_dump(exclude_unset=True))


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db), _user=require_delete):
    asset = asset_service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset_service.delete_asset(db, asset)


@router.post(
    "/{asset_id}/dependencies", response_model=AssetDependencyRead, status_code=status.HTTP_201_CREATED
)
def add_dependency(
    asset_id: int, payload: AssetDependencyCreate, db: Session = Depends(get_db), _user=require_write
):
    if not asset_service.get_asset(db, asset_id) or not asset_service.get_asset(
        db, payload.depends_on_asset_id
    ):
        raise HTTPException(status_code=404, detail="Asset not found")
    try:
        return asset_service.add_dependency(db, asset_id, payload.depends_on_asset_id, payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
