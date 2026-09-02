"""Incident Response lifecycle (Section 16)."""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IncidentStage(StrEnum):
    """Ordered lifecycle - see app/services/incident.py::advance_stage for
    the enforced forward-only transition order.
    """

    DETECTION = "detection"
    TRIAGE = "triage"
    INVESTIGATION = "investigation"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"


STAGE_ORDER = [
    IncidentStage.DETECTION,
    IncidentStage.TRIAGE,
    IncidentStage.INVESTIGATION,
    IncidentStage.CONTAINMENT,
    IncidentStage.ERADICATION,
    IncidentStage.RECOVERY,
    IncidentStage.LESSONS_LEARNED,
]


class IncidentSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity, native_enum=False, length=16))
    stage: Mapped[IncidentStage] = mapped_column(
        Enum(IncidentStage, native_enum=False, length=24), default=IncidentStage.DETECTION
    )
    affected_asset_ids: Mapped[list] = mapped_column(JSON, default=list)
    indicators: Mapped[list] = mapped_column(JSON, default=list)
    recommended_containment: Mapped[str] = mapped_column(Text, default="")
    remediation: Mapped[str] = mapped_column(Text, default="")
    lessons_learned: Mapped[str] = mapped_column(Text, default="")
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    timeline: Mapped[list["IncidentTimelineEntry"]] = relationship(
        back_populates="incident", order_by="IncidentTimelineEntry.occurred_at", cascade="all, delete-orphan"
    )


class IncidentTimelineEntry(Base):
    __tablename__ = "incident_timeline_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    stage: Mapped[IncidentStage] = mapped_column(Enum(IncidentStage, native_enum=False, length=24))
    description: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    incident: Mapped["Incident"] = relationship(back_populates="timeline")
