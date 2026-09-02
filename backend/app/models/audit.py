"""Append-only-style audit log (Section 32).

Not enforced as literally immutable at the database level in this
portfolio project (that would need a dedicated append-only storage engine
or DB-level triggers revoking UPDATE/DELETE grants - see
docs/architecture/limitations.md) - but the application layer never
updates or deletes an AuditLogEntry once written; every audit-relevant
service function only ever calls record(), never an update.
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(100))  # e.g. "risk_treatment_update"
    object_type: Mapped[str] = mapped_column(String(50))  # e.g. "RiskRecord"
    object_id: Mapped[int] = mapped_column()
    old_value: Mapped[dict] = mapped_column(JSON, default=dict)
    new_value: Mapped[dict] = mapped_column(JSON, default=dict)
    reason: Mapped[str] = mapped_column(Text, default="")
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
