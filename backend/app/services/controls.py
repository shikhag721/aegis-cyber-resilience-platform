"""Control library, control assessment, and control-gap analysis
(Section 17). Every effectiveness change is written to the audit log
(Section 32) - see update_assessment().
"""
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models.control import Control, ControlAssessment
from app.services import audit as audit_service


def create_control(db: Session, data: dict) -> Control:
    control = Control(**data)
    db.add(control)
    db.commit()
    db.refresh(control)
    return control


def list_controls(db: Session) -> list[Control]:
    return db.query(Control).order_by(Control.control_id).all()


def get_control(db: Session, control_id: int) -> Control | None:
    return db.get(Control, control_id)


def create_assessment(db: Session, data: dict) -> ControlAssessment:
    assessment = ControlAssessment(**data)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db: Session, assessment_id: int) -> ControlAssessment | None:
    return (
        db.query(ControlAssessment)
        .options(joinedload(ControlAssessment.evidence), joinedload(ControlAssessment.control))
        .filter(ControlAssessment.id == assessment_id)
        .first()
    )


def list_assessments(db: Session, control_id: int | None = None) -> list[ControlAssessment]:
    query = db.query(ControlAssessment).options(
        joinedload(ControlAssessment.evidence), joinedload(ControlAssessment.control)
    )
    if control_id is not None:
        query = query.filter(ControlAssessment.control_id == control_id)
    return query.all()


def update_assessment(
    db: Session, assessment: ControlAssessment, changes: dict, actor: str, reason: str = ""
) -> ControlAssessment:
    old_status = assessment.overall_status
    old_value = {
        "design_effectiveness": assessment.design_effectiveness.value,
        "operating_effectiveness": assessment.operating_effectiveness.value,
    }

    for field, value in changes.items():
        if value is not None:
            setattr(assessment, field, value)
    db.commit()
    db.refresh(assessment)

    new_value = {
        "design_effectiveness": assessment.design_effectiveness.value,
        "operating_effectiveness": assessment.operating_effectiveness.value,
    }
    new_status = assessment.overall_status

    if old_status != new_status:
        audit_service.record(
            db,
            actor=actor,
            action="control_assessment_status_change",
            object_type="ControlAssessment",
            object_id=assessment.id,
            old_value={**old_value, "overall_status": old_status},
            new_value={**new_value, "overall_status": new_status},
            reason=reason,
        )
    return assessment


@dataclass
class ControlGapFinding:
    control_id: str
    control_title: str
    assessment_id: int
    finding_type: str  # ineffective / not_assessed / evidence_missing / evidence_expired / overdue_review
    severity: str
    detail: str


def analyze_control_gaps(db: Session) -> list[ControlGapFinding]:
    findings: list[ControlGapFinding] = []
    today = date.today()

    for assessment in list_assessments(db):
        control = assessment.control
        status = assessment.overall_status

        if status == "Ineffective":
            findings.append(
                ControlGapFinding(
                    control_id=control.control_id,
                    control_title=control.title,
                    assessment_id=assessment.id,
                    finding_type="ineffective",
                    severity="critical",
                    detail=f"{control.control_id} ({control.title}) is assessed as Ineffective.",
                )
            )
        elif status == "Not Assessed":
            findings.append(
                ControlGapFinding(
                    control_id=control.control_id,
                    control_title=control.title,
                    assessment_id=assessment.id,
                    finding_type="not_assessed",
                    severity="medium",
                    detail=f"{control.control_id} ({control.title}) has never been assessed.",
                )
            )
        elif status == "Partially Effective":
            findings.append(
                ControlGapFinding(
                    control_id=control.control_id,
                    control_title=control.title,
                    assessment_id=assessment.id,
                    finding_type="partially_effective",
                    severity="high",
                    detail=(
                        f"{control.control_id} ({control.title}) is only Partially Effective - "
                        "design and operating effectiveness disagree."
                    ),
                )
            )

        if not assessment.evidence:
            findings.append(
                ControlGapFinding(
                    control_id=control.control_id,
                    control_title=control.title,
                    assessment_id=assessment.id,
                    finding_type="evidence_missing",
                    severity="high",
                    detail=(
                        f"{control.control_id} ({control.title}) has an effectiveness rating but no "
                        "evidence on file to support it - a claim without evidence is not a control."
                    ),
                )
            )
        else:
            for evidence in assessment.evidence:
                if evidence.valid_until and evidence.valid_until < today:
                    findings.append(
                        ControlGapFinding(
                            control_id=control.control_id,
                            control_title=control.title,
                            assessment_id=assessment.id,
                            finding_type="evidence_expired",
                            severity="medium",
                            detail=(
                                f"Evidence '{evidence.evidence_type}' for {control.control_id} expired "
                                f"on {evidence.valid_until.isoformat()}."
                            ),
                        )
                    )

        if assessment.last_reviewed_at:
            overdue_by = today - assessment.last_reviewed_at - timedelta(days=control.review_frequency_days)
            if overdue_by.days > 0:
                findings.append(
                    ControlGapFinding(
                        control_id=control.control_id,
                        control_title=control.title,
                        assessment_id=assessment.id,
                        finding_type="overdue_review",
                        severity="medium",
                        detail=(
                            f"{control.control_id} ({control.title}) review is {overdue_by.days} day(s) "
                            f"overdue (review frequency: {control.review_frequency_days} days)."
                        ),
                    )
                )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_rank.get(f.severity, 4))
    return findings
