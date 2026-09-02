from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.agent import AgentAssessmentRead, AIAgentCreate, AIAgentRead
from app.services import agent as agent_service

router = APIRouter(prefix="/agent-security", tags=["agent-security"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/agents", response_model=list[AIAgentRead])
def list_agents(db: Session = Depends(get_db), _user=require_read):
    return agent_service.list_agents(db)


@router.post("/agents", response_model=AIAgentRead, status_code=201)
def create_agent(payload: AIAgentCreate, db: Session = Depends(get_db), _user=require_write):
    return agent_service.create_agent(db, payload.model_dump())


@router.get("/agents/{agent_id}", response_model=AIAgentRead)
def get_agent(agent_id: int, db: Session = Depends(get_db), _user=require_read):
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return agent


@router.get("/agents/{agent_id}/assessments/latest", response_model=AgentAssessmentRead)
def get_latest_assessment(agent_id: int, db: Session = Depends(get_db), _user=require_read):
    assessment = agent_service.latest_assessment(db, agent_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment on file for this agent")
    return assessment


@router.post("/agents/{agent_id}/assessments", response_model=AgentAssessmentRead, status_code=201)
def create_assessment(agent_id: int, db: Session = Depends(get_db), _user=require_write):
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return agent_service.run_assessment(db, agent)
