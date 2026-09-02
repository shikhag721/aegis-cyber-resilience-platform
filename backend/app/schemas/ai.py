from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.ai import AIDeploymentEnvironment, AIFindingType, AIRiskLens, RegulatoryRiskTier


class AISystemCreate(BaseModel):
    # model_provider legitimately starts with "model_" (it names the AI
    # model's provider) - not one of Pydantic's own reserved model_* methods,
    # so the protected-namespace warning is disabled here rather than
    # renaming a field that reads naturally in this domain.
    model_config = ConfigDict(protected_namespaces=())

    name: str
    business_owner: str
    technical_owner: str
    purpose: str
    model_provider: str
    data_processed: str
    user_base: str
    integrations: list[str] = []
    tools_available: list[str] = []
    permissions_summary: str = ""
    deployment_environment: AIDeploymentEnvironment
    human_oversight: bool = False
    monitoring_enabled: bool = False
    influences_decisions: bool = False
    regulatory_risk_tier: RegulatoryRiskTier = RegulatoryRiskTier.MINIMAL
    asset_id: int | None = None


class AISecurityFindingCreate(BaseModel):
    risk_lens: AIRiskLens
    finding_type: AIFindingType
    severity: str
    description: str
    recommendation: str


class AISecurityFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ai_system_id: int
    risk_lens: AIRiskLens
    finding_type: AIFindingType
    severity: str
    description: str
    recommendation: str
    status: str
    discovered_at: datetime


class AISystemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    name: str
    business_owner: str
    technical_owner: str
    purpose: str
    model_provider: str
    data_processed: str
    user_base: str
    integrations: list[str]
    tools_available: list[str]
    permissions_summary: str
    deployment_environment: AIDeploymentEnvironment
    human_oversight: bool
    monitoring_enabled: bool
    influences_decisions: bool
    regulatory_risk_tier: RegulatoryRiskTier
    asset_id: int | None
    findings: list[AISecurityFindingRead]


class AIInventoryFindingRead(BaseModel):
    ai_system_name: str
    finding_type: str
    severity: str
    detail: str
