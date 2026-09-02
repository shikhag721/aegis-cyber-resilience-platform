from datetime import date, timedelta

import pytest

from app.db.session import SessionLocal
from app.models.control import ControlEffectiveness
from app.services import audit as audit_service
from app.services import controls as controls_service
from app.services import evidence as evidence_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def control(db_session):
    return controls_service.create_control(
        db_session,
        dict(
            control_id="CTRL-TEST-1",
            title="MFA Enforcement",
            description="d",
            control_objective="o",
            framework_reference="NIST CSF PR.AC-7",
            test_procedure="Sample privileged accounts and confirm MFA is enrolled.",
        ),
    )


def test_overall_status_effective_when_both_effective(db_session, control):
    assessment = controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.EFFECTIVE,
            operating_effectiveness=ControlEffectiveness.EFFECTIVE,
        ),
    )
    assert assessment.overall_status == "Effective"


def test_overall_status_ineffective_if_either_dimension_ineffective(db_session, control):
    assessment = controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.EFFECTIVE,
            operating_effectiveness=ControlEffectiveness.INEFFECTIVE,
        ),
    )
    assert assessment.overall_status == "Ineffective"


def test_overall_status_not_assessed_when_either_unassessed(db_session, control):
    assessment = controls_service.create_assessment(db_session, dict(control_id=control.id))
    assert assessment.overall_status == "Not Assessed"


def test_overall_status_partially_effective_when_mismatched(db_session, control):
    assessment = controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.EFFECTIVE,
            operating_effectiveness=ControlEffectiveness.PARTIALLY_EFFECTIVE,
        ),
    )
    assert assessment.overall_status == "Partially Effective"


def test_update_assessment_writes_audit_entry_on_status_change(db_session, control):
    assessment = controls_service.create_assessment(db_session, dict(control_id=control.id))
    controls_service.update_assessment(
        db_session,
        assessment,
        {
            "design_effectiveness": ControlEffectiveness.EFFECTIVE,
            "operating_effectiveness": ControlEffectiveness.EFFECTIVE,
        },
        actor="risk_analyst",
        reason="Verified via access review sample.",
    )
    entries = audit_service.list_entries(db_session, object_type="ControlAssessment", object_id=assessment.id)
    assert len(entries) == 1
    assert entries[0].new_value["overall_status"] == "Effective"
    assert entries[0].old_value["overall_status"] == "Not Assessed"
    assert entries[0].actor == "risk_analyst"


def test_update_assessment_no_audit_entry_if_status_unchanged(db_session, control):
    assessment = controls_service.create_assessment(
        db_session, dict(control_id=control.id, notes="initial")
    )
    controls_service.update_assessment(db_session, assessment, {"notes": "updated note"}, actor="x")
    entries = audit_service.list_entries(db_session, object_type="ControlAssessment", object_id=assessment.id)
    assert entries == []


def test_gap_analysis_flags_ineffective_control(db_session, control):
    controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.INEFFECTIVE,
            operating_effectiveness=ControlEffectiveness.INEFFECTIVE,
        ),
    )
    findings = controls_service.analyze_control_gaps(db_session)
    assert any(f.finding_type == "ineffective" for f in findings)


def test_gap_analysis_flags_missing_evidence(db_session, control):
    controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.EFFECTIVE,
            operating_effectiveness=ControlEffectiveness.EFFECTIVE,
        ),
    )
    findings = controls_service.analyze_control_gaps(db_session)
    assert any(f.finding_type == "evidence_missing" for f in findings)


def test_gap_analysis_does_not_flag_missing_evidence_when_evidence_exists(db_session, control):
    assessment = controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.EFFECTIVE,
            operating_effectiveness=ControlEffectiveness.EFFECTIVE,
        ),
    )
    evidence_service.create_evidence(
        db_session,
        assessment.id,
        dict(evidence_type="Access review", source="Okta export", collected_at=date.today()),
    )
    findings = controls_service.analyze_control_gaps(db_session)
    assert not any(f.finding_type == "evidence_missing" for f in findings)


def test_gap_analysis_flags_overdue_review(db_session, control):
    assessment = controls_service.create_assessment(
        db_session,
        dict(
            control_id=control.id,
            design_effectiveness=ControlEffectiveness.EFFECTIVE,
            operating_effectiveness=ControlEffectiveness.EFFECTIVE,
            last_reviewed_at=date.today() - timedelta(days=control.review_frequency_days + 10),
        ),
    )
    evidence_service.create_evidence(
        db_session,
        assessment.id,
        dict(evidence_type="Access review", source="x", collected_at=date.today()),
    )
    findings = controls_service.analyze_control_gaps(db_session)
    assert any(f.finding_type == "overdue_review" for f in findings)
