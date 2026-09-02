"""AI Inventory and AI Security (Sections 24-25).

AISecurityFinding.risk_lens implements Section 25's explicit requirement to
distinguish Model / Application / Data / Identity / Infrastructure / Tool /
Third-Party / Governance risk - a finding is never just "AI risk," it is
always attributed to a specific one of these eight lenses.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIDeploymentEnvironment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class RegulatoryRiskTier(StrEnum):
    """Mirrors EU AI Act risk-tier language as an illustrative reference
    only - "resembles," never a determination of actual legal status. See
    docs/ai-security/ for the full disclaimer.
    """

    MINIMAL = "minimal"
    LIMITED = "limited"
    HIGH = "high"


class AISystem(Base):
    __tablename__ = "ai_systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    business_owner: Mapped[str] = mapped_column(String(150))
    technical_owner: Mapped[str] = mapped_column(String(150))
    purpose: Mapped[str] = mapped_column(Text)
    model_provider: Mapped[str] = mapped_column(String(200))  # e.g. "Third-party LLM API", "Internal model"
    data_processed: Mapped[str] = mapped_column(Text)
    user_base: Mapped[str] = mapped_column(String(200))
    integrations: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["Customer Database"]
    tools_available: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["database_query"]
    permissions_summary: Mapped[str] = mapped_column(Text, default="")
    deployment_environment: Mapped[AIDeploymentEnvironment] = mapped_column(
        Enum(AIDeploymentEnvironment, native_enum=False, length=16)
    )
    human_oversight: Mapped[bool] = mapped_column(Boolean, default=False)
    monitoring_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    influences_decisions: Mapped[bool] = mapped_column(Boolean, default=False)
    regulatory_risk_tier: Mapped[RegulatoryRiskTier] = mapped_column(
        Enum(RegulatoryRiskTier, native_enum=False, length=16), default=RegulatoryRiskTier.MINIMAL
    )
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)

    asset: Mapped["Asset | None"] = relationship()  # noqa: F821
    findings: Mapped[list["AISecurityFinding"]] = relationship(
        back_populates="ai_system", cascade="all, delete-orphan"
    )


class AIRiskLens(StrEnum):
    MODEL = "model"
    APPLICATION = "application"
    DATA = "data"
    IDENTITY = "identity"
    INFRASTRUCTURE = "infrastructure"
    TOOL = "tool"
    THIRD_PARTY = "third_party"
    GOVERNANCE = "governance"


class AIFindingType(StrEnum):
    PROMPT_INJECTION = "prompt_injection"
    SENSITIVE_INFO_DISCLOSURE = "sensitive_info_disclosure"
    INSECURE_OUTPUT_HANDLING = "insecure_output_handling"
    SUPPLY_CHAIN = "supply_chain"
    EXCESSIVE_AGENCY = "excessive_agency"
    IMPROPER_AUTHORIZATION = "improper_authorization"
    DATA_POISONING = "data_poisoning"
    MODEL_MANIPULATION = "model_manipulation"
    INSECURE_INTEGRATION = "insecure_integration"
    AVAILABILITY = "availability"


class AISecurityFinding(Base):
    __tablename__ = "ai_security_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    ai_system_id: Mapped[int] = mapped_column(ForeignKey("ai_systems.id"))
    risk_lens: Mapped[AIRiskLens] = mapped_column(Enum(AIRiskLens, native_enum=False, length=20))
    finding_type: Mapped[AIFindingType] = mapped_column(Enum(AIFindingType, native_enum=False, length=32))
    severity: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="open")
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    ai_system: Mapped["AISystem"] = relationship(back_populates="findings")
