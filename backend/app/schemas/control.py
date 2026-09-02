from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.control import ControlEffectiveness, EvidenceStatus


class ControlCreate(BaseModel):
    control_id: str
    title: str
    description: str
    control_objective: str
    framework_reference: str
    test_procedure: str
    owner: str = ""
    review_frequency_days: int = 180


class ControlRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    control_id: str
    title: str
    description: str
    control_objective: str
    framework_reference: str
    test_procedure: str
    owner: str
    review_frequency_days: int


class ControlAssessmentCreate(BaseModel):
    control_id: int
    asset_id: int | None = None
    design_effectiveness: ControlEffectiveness = ControlEffectiveness.NOT_ASSESSED
    operating_effectiveness: ControlEffectiveness = ControlEffectiveness.NOT_ASSESSED
    notes: str = ""
    last_reviewed_at: date | None = None


class ControlAssessmentUpdate(BaseModel):
    design_effectiveness: ControlEffectiveness | None = None
    operating_effectiveness: ControlEffectiveness | None = None
    notes: str | None = None
    last_reviewed_at: date | None = None
    reason: str = ""


class EvidenceCreate(BaseModel):
    control_assessment_id: int
    evidence_type: str
    source: str
    owner: str = ""
    collected_at: date
    valid_until: date | None = None
    status: EvidenceStatus = EvidenceStatus.PENDING_REVIEW
    notes: str = ""


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    control_assessment_id: int
    evidence_type: str
    source: str
    owner: str
    collected_at: date
    valid_until: date | None
    status: EvidenceStatus
    notes: str


class ControlAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    control_id: int
    asset_id: int | None
    design_effectiveness: ControlEffectiveness
    operating_effectiveness: ControlEffectiveness
    overall_status: str
    notes: str
    last_reviewed_at: date | None
    control: ControlRead
    evidence: list[EvidenceRead]


class ControlGapFindingRead(BaseModel):
    control_id: str
    control_title: str
    assessment_id: int
    finding_type: str
    severity: str
    detail: str


class AuditLogEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    object_type: str
    object_id: int
    old_value: dict
    new_value: dict
    reason: str
    occurred_at: datetime
