from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.agent import AutonomyLevel


class AIAgentCreate(BaseModel):
    name: str
    ai_system_id: int | None = None
    purpose: str
    tools_available: list[str] = []
    autonomy_level: AutonomyLevel = AutonomyLevel.HUMAN_APPROVAL_REQUIRED
    can_take_irreversible_actions: bool = False
    can_initiate_financial_transactions: bool = False
    requires_human_approval: bool = True
    data_access_scope: str = ""
    guardrails_description: str = ""


class AgentAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_id: int
    likelihood: int
    impact: int
    score: int
    rating: str
    contributing_factors: list
    recommendation: str
    assessed_at: datetime


class AIAgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ai_system_id: int | None
    purpose: str
    tools_available: list[str]
    autonomy_level: AutonomyLevel
    can_take_irreversible_actions: bool
    can_initiate_financial_transactions: bool
    requires_human_approval: bool
    data_access_scope: str
    guardrails_description: str
