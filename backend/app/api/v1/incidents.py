from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.incident import (
    IncidentAdvanceRequest,
    IncidentCreate,
    IncidentRead,
    IncidentUpdate,
)
from app.services import incident as incident_service

router = APIRouter(prefix="/incidents", tags=["incidents"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db), _user=require_read):
    return incident_service.list_incidents(db)


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db), _user=require_write):
    incident = incident_service.create_incident(db, payload.model_dump())
    return incident_service.get_incident(db, incident.id)


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db), _user=require_read):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/{incident_id}/advance", response_model=IncidentRead)
def advance_incident(
    incident_id: int, payload: IncidentAdvanceRequest, db: Session = Depends(get_db), _user=require_write
):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    try:
        incident_service.advance_stage(db, incident, payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return incident_service.get_incident(db, incident_id)


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db), _user=require_write
):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident_service.update_incident_fields(db, incident, payload.model_dump(exclude_unset=True))
    return incident_service.get_incident(db, incident_id)
