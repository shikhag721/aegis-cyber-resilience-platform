"""GRC control assessment (Section 17).

Deliberately separates design effectiveness from operating effectiveness -
a control can be well-designed on paper (design_effectiveness=effective)
while not actually functioning in practice (operating_effectiveness=
ineffective, e.g. no one has checked in 8 months). Section 17 explicitly
warns against reducing GRC to a compliance checklist; this distinction is
the mechanism that prevents that reduction, mirrored from the same
design-vs-operating distinction risk practitioners actually use.
"""
from datetime import date, datetime, timezone
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ControlEffectiveness(StrEnum):
    EFFECTIVE = "effective"
    PARTIALLY_EFFECTIVE = "partially_effective"
    INEFFECTIVE = "ineffective"
    NOT_ASSESSED = "not_assessed"


class Control(Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. "CTRL-01"
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    control_objective: Mapped[str] = mapped_column(Text)
    framework_reference: Mapped[str] = mapped_column(Text)
    test_procedure: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(150), default="")
    review_frequency_days: Mapped[int] = mapped_column(default=180)

    assessments: Mapped[list["ControlAssessment"]] = relationship(back_populates="control")


class ControlAssessment(Base):
    __tablename__ = "control_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"))
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    design_effectiveness: Mapped[ControlEffectiveness] = mapped_column(
        Enum(ControlEffectiveness, native_enum=False, length=24), default=ControlEffectiveness.NOT_ASSESSED
    )
    operating_effectiveness: Mapped[ControlEffectiveness] = mapped_column(
        Enum(ControlEffectiveness, native_enum=False, length=24), default=ControlEffectiveness.NOT_ASSESSED
    )
    notes: Mapped[str] = mapped_column(Text, default="")
    last_reviewed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    control: Mapped["Control"] = relationship(back_populates="assessments")
    asset: Mapped["Asset | None"] = relationship()  # noqa: F821
    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="control_assessment", cascade="all, delete-orphan"
    )

    @property
    def overall_status(self) -> str:
        """The single, risk-relevant answer to 'is this control actually
        working' - not a restatement of either sub-field, but the
        conservative combination of both (a control is only as good as
        its weakest dimension).
        """
        design, operating = self.design_effectiveness, self.operating_effectiveness
        if design == ControlEffectiveness.NOT_ASSESSED or operating == ControlEffectiveness.NOT_ASSESSED:
            return "Not Assessed"
        if design == ControlEffectiveness.INEFFECTIVE or operating == ControlEffectiveness.INEFFECTIVE:
            return "Ineffective"
        if (
            design == ControlEffectiveness.EFFECTIVE
            and operating == ControlEffectiveness.EFFECTIVE
        ):
            return "Effective"
        return "Partially Effective"


class EvidenceStatus(StrEnum):
    VALID = "valid"
    EXPIRED = "expired"
    PENDING_REVIEW = "pending_review"


class Evidence(Base):
    __tablename__ = "control_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_assessment_id: Mapped[int] = mapped_column(ForeignKey("control_assessments.id"))
    evidence_type: Mapped[str] = mapped_column(String(150))  # e.g. "Access review export"
    source: Mapped[str] = mapped_column(String(200))  # e.g. "Okta admin console export"
    owner: Mapped[str] = mapped_column(String(150), default="")
    collected_at: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[EvidenceStatus] = mapped_column(
        Enum(EvidenceStatus, native_enum=False, length=20), default=EvidenceStatus.PENDING_REVIEW
    )
    notes: Mapped[str] = mapped_column(Text, default="")

    control_assessment: Mapped["ControlAssessment"] = relationship(back_populates="evidence")
