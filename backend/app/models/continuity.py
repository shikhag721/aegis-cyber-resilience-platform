"""Business Continuity & Disaster Recovery (Section 22)."""
from datetime import date

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ContinuityPlan(Base):
    __tablename__ = "continuity_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), unique=True)
    rto_hours: Mapped[int | None] = mapped_column(nullable=True)  # Recovery Time Objective
    rpo_hours: Mapped[int | None] = mapped_column(nullable=True)  # Recovery Point Objective
    backup_frequency: Mapped[str] = mapped_column(String(50), default="")
    last_backup_tested_at: Mapped[date | None] = mapped_column(nullable=True)
    last_dr_test_at: Mapped[date | None] = mapped_column(nullable=True)
    dr_test_result: Mapped[str] = mapped_column(Text, default="")
    recovery_dependencies: Mapped[list] = mapped_column(JSON, default=list)
    business_impact_if_unavailable: Mapped[str] = mapped_column(Text, default="")

    asset: Mapped["Asset"] = relationship()  # noqa: F821
