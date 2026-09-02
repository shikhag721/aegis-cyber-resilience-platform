"""Security Monitoring & Incident Simulation (Section 15).

Deliberately named "simulation," not "SIEM" - see
docs/decisions/0005-synthetic-environment.md. Events are synthetic,
seeded data; the value demonstrated here is the CORRELATION logic
(app/services/monitoring.py::correlate), not log ingestion at scale.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SecurityEventType(StrEnum):
    FAILED_LOGIN = "failed_login"
    SUCCESSFUL_LOGIN = "successful_login"
    UNUSUAL_LOCATION = "unusual_location"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATABASE_ACCESS = "database_access"
    UNUSUAL_DATA_TRANSFER = "unusual_data_transfer"


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[SecurityEventType] = mapped_column(
        Enum(SecurityEventType, native_enum=False, length=32)
    )
    username: Mapped[str] = mapped_column(String(100), index=True)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    source_ip: Mapped[str] = mapped_column(String(45), default="")
    source_location: Mapped[str] = mapped_column(String(100), default="")
    details: Mapped[str] = mapped_column(Text, default="")
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["Asset | None"] = relationship()  # noqa: F821
