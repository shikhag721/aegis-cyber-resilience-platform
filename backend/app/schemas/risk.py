from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.risk import RiskStatus, TreatmentDecision

_VALID_SEVERITY = {"low", "medium", "high", "critical"}


class RiskAssessRequest(BaseModel):
    """Input to create a new risk record: engine inputs plus the linkage
    to what's being assessed. asset_criticality/data_classification are
    NOT accepted here - they are read from the linked Asset itself, so a
    risk record can never disagree with its own asset's inventory record.
    """

    title: str
    description: str
    asset_id: int
    threat_id: int | None = None
    attack_path_id: int | None = None
    threat_severity: str
    known_exploited: bool = False
    control_effectiveness: float = 0.0
    risk_appetite: str = "moderate"

    @field_validator("threat_severity")
    @classmethod
    def valid_severity(cls, value: str) -> str:
        if value not in _VALID_SEVERITY:
            raise ValueError(f"threat_severity must be one of {sorted(_VALID_SEVERITY)}")
        return value

    @field_validator("control_effectiveness")
    @classmethod
    def zero_to_one(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("control_effectiveness must be between 0.0 and 1.0")
        return value


class RiskTreatmentUpdate(BaseModel):
    treatment_decision: TreatmentDecision
    treatment_reason: str
    owner: str
    target_date: date | None = None
    status: RiskStatus = RiskStatus.TREATMENT_IN_PROGRESS

    @field_validator("treatment_reason")
    @classmethod
    def reason_required(cls, value: str) -> str:
        if len(value.strip()) < 10:
            raise ValueError("treatment_reason must explain the decision (at least 10 characters).")
        return value


class RiskRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    asset_id: int
    threat_id: int | None
    attack_path_id: int | None
    asset_criticality: str
    data_classification: str
    threat_severity: str
    internet_exposed: bool
    known_exploited: bool
    logging_enabled: bool
    control_effectiveness: float
    risk_appetite: str
    likelihood: int
    impact: int
    inherent_score: int
    inherent_rating: str
    residual_score: int
    residual_rating: str
    contributing_factors: list
    primary_concern: str
    recommended_treatment: str
    treatment_decision: TreatmentDecision | None
    treatment_reason: str
    owner: str
    target_date: date | None
    status: RiskStatus
