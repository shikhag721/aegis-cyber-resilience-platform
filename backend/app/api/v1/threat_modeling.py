from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.threat import (
    AttackPathCreate,
    AttackPathRead,
    ThreatActorCreate,
    ThreatActorRead,
    ThreatCreate,
    ThreatRead,
)
from app.services import threat as threat_service

router = APIRouter(tags=["threat-modeling"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/threat-actors", response_model=list[ThreatActorRead])
def list_threat_actors(db: Session = Depends(get_db), _user=require_read):
    return threat_service.list_threat_actors(db)


@router.post("/threat-actors", response_model=ThreatActorRead, status_code=status.HTTP_201_CREATED)
def create_threat_actor(payload: ThreatActorCreate, db: Session = Depends(get_db), _user=require_write):
    return threat_service.create_threat_actor(db, payload.model_dump())


@router.get("/threats", response_model=list[ThreatRead])
def list_threats(db: Session = Depends(get_db), _user=require_read):
    return threat_service.list_threats(db)


@router.post("/threats", response_model=ThreatRead, status_code=status.HTTP_201_CREATED)
def create_threat(payload: ThreatCreate, db: Session = Depends(get_db), _user=require_write):
    return threat_service.create_threat(db, payload.model_dump())


@router.get("/attack-paths", response_model=list[AttackPathRead])
def list_attack_paths(
    target_asset_id: int | None = None, db: Session = Depends(get_db), _user=require_read
):
    return threat_service.list_attack_paths(db, target_asset_id)


@router.get("/attack-paths/{attack_path_id}", response_model=AttackPathRead)
def get_attack_path(attack_path_id: int, db: Session = Depends(get_db), _user=require_read):
    attack_path = threat_service.get_attack_path(db, attack_path_id)
    if not attack_path:
        raise HTTPException(status_code=404, detail="Attack path not found")
    return attack_path


@router.post("/attack-paths", response_model=AttackPathRead, status_code=status.HTTP_201_CREATED)
def create_attack_path(payload: AttackPathCreate, db: Session = Depends(get_db), _user=require_write):
    data = payload.model_dump()
    data["steps"] = [s for s in data["steps"]]
    attack_path = threat_service.create_attack_path(db, data)
    return threat_service.get_attack_path(db, attack_path.id)
