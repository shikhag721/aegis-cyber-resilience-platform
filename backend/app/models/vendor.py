"""Third-party / vendor risk (Section 20).

Deliberately NOT reusing app/risk_engine/'s RiskInput shape directly -
vendor risk factors (subprocessors, certifications, contractual terms,
incident history) don't map cleanly onto asset-based likelihood/impact
inputs. Instead this module implements a small, parallel scorer
(app/services/vendor.py) using the same explainable-factors design pattern
as the risk engine, without forcing a semantic fit that isn't there. See
docs/decisions/0008-vendor-risk-not-reusing-risk-engine.md.
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.asset import Criticality, DataClassification


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    service_description: Mapped[str] = mapped_column(Text)
    business_criticality: Mapped[Criticality] = mapped_column(Enum(Criticality, native_enum=False, length=16))
    data_access: Mapped[bool] = mapped_column(Boolean, default=True)
    data_classification_handled: Mapped[DataClassification] = mapped_column(
        Enum(DataClassification, native_enum=False, length=24)
    )
    security_controls_summary: Mapped[str] = mapped_column(Text, default="")
    certifications: Mapped[str] = mapped_column(String(255), default="")
    has_incident_history: Mapped[bool] = mapped_column(Boolean, default=False)
    incident_history_notes: Mapped[str] = mapped_column(Text, default="")
    subprocessors: Mapped[str] = mapped_column(Text, default="")
    availability_sla_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    contractual_security_clause: Mapped[bool] = mapped_column(Boolean, default=False)
    data_retention_policy: Mapped[str] = mapped_column(Text, default="")
    exit_strategy_defined: Mapped[bool] = mapped_column(Boolean, default=False)

    assessments: Mapped[list["VendorAssessment"]] = relationship(
        back_populates="vendor", cascade="all, delete-orphan"
    )


class VendorAssessment(Base):
    __tablename__ = "vendor_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    likelihood: Mapped[int] = mapped_column()
    impact: Mapped[int] = mapped_column()
    score: Mapped[int] = mapped_column()
    rating: Mapped[str] = mapped_column(String(16))
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(60))
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    vendor: Mapped["Vendor"] = relationship(back_populates="assessments")
