"""Risk Register (Section 10/20): persists a risk_engine assessment against
an asset, plus the human treatment decision layered on top of the engine's
suggestion. See docs/risk-methodology/.
"""
from datetime import date, datetime, timezone
from enum import StrEnum

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TreatmentDecision(StrEnum):
    MITIGATE = "mitigate"
    ACCEPT = "accept"
    TRANSFER = "transfer"
    AVOID = "avoid"


class RiskStatus(StrEnum):
    OPEN = "open"
    TREATMENT_IN_PROGRESS = "treatment_in_progress"
    CLOSED = "closed"


class RiskRecord(Base):
    __tablename__ = "risk_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    threat_id: Mapped[int | None] = mapped_column(ForeignKey("threats.id"), nullable=True)
    attack_path_id: Mapped[int | None] = mapped_column(ForeignKey("attack_paths.id"), nullable=True)

    # Snapshot of the inputs used, so a historical record stays meaningful
    # even if the underlying asset's fields change later.
    asset_criticality: Mapped[str] = mapped_column(String(16))
    data_classification: Mapped[str] = mapped_column(String(24))
    threat_severity: Mapped[str] = mapped_column(String(16))
    internet_exposed: Mapped[bool] = mapped_column(default=False)
    known_exploited: Mapped[bool] = mapped_column(default=False)
    logging_enabled: Mapped[bool] = mapped_column(default=True)
    control_effectiveness: Mapped[float] = mapped_column(default=0.0)
    risk_appetite: Mapped[str] = mapped_column(String(16), default="moderate")

    likelihood: Mapped[int] = mapped_column(Integer)
    impact: Mapped[int] = mapped_column(Integer)
    inherent_score: Mapped[int] = mapped_column(Integer)
    inherent_rating: Mapped[str] = mapped_column(String(16))
    residual_score: Mapped[int] = mapped_column(Integer)
    residual_rating: Mapped[str] = mapped_column(String(16))
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list)
    primary_concern: Mapped[str] = mapped_column(Text, default="")
    recommended_treatment: Mapped[str] = mapped_column(Text, default="")

    treatment_decision: Mapped[TreatmentDecision | None] = mapped_column(
        Enum(TreatmentDecision, native_enum=False, length=16), nullable=True
    )
    treatment_reason: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(String(150), default="")
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[RiskStatus] = mapped_column(
        Enum(RiskStatus, native_enum=False, length=24), default=RiskStatus.OPEN
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["Asset"] = relationship()  # noqa: F821
