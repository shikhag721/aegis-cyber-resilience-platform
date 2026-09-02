"""AI agent security (Section 27).

Deliberately NOT reusing app/risk_engine/'s RiskInput shape - agent blast
radius factors (autonomy level, irreversible actions, financial-transaction
capability, guardrails) don't map cleanly onto asset-based likelihood/impact
inputs. This follows the same parallel-scorer pattern as vendor risk
(app/services/vendor.py) - see
docs/decisions/0009-agent-blast-radius-not-reusing-risk-engine.md.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AutonomyLevel(StrEnum):
    OBSERVATION_ONLY = "observation_only"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    AUTONOMOUS_WITHIN_GUARDRAILS = "autonomous_within_guardrails"
    FULLY_AUTONOMOUS = "fully_autonomous"


class AIAgent(Base):
    __tablename__ = "ai_agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    ai_system_id: Mapped[int | None] = mapped_column(ForeignKey("ai_systems.id"), nullable=True)
    purpose: Mapped[str] = mapped_column(Text)
    tools_available: Mapped[list] = mapped_column(JSON, default=list)
    autonomy_level: Mapped[AutonomyLevel] = mapped_column(
        Enum(AutonomyLevel, native_enum=False, length=32), default=AutonomyLevel.HUMAN_APPROVAL_REQUIRED
    )
    can_take_irreversible_actions: Mapped[bool] = mapped_column(Boolean, default=False)
    can_initiate_financial_transactions: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    data_access_scope: Mapped[str] = mapped_column(Text, default="")
    guardrails_description: Mapped[str] = mapped_column(Text, default="")

    ai_system: Mapped["AISystem | None"] = relationship()  # noqa: F821
    assessments: Mapped[list["AgentAssessment"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan"
    )


class AgentAssessment(Base):
    __tablename__ = "agent_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("ai_agents.id"))
    likelihood: Mapped[int] = mapped_column()
    impact: Mapped[int] = mapped_column()
    score: Mapped[int] = mapped_column()
    rating: Mapped[str] = mapped_column(String(16))
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(80))
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    agent: Mapped["AIAgent"] = relationship(back_populates="assessments")
