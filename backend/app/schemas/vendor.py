from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.asset import Criticality, DataClassification


class VendorCreate(BaseModel):
    name: str
    service_description: str
    business_criticality: Criticality
    data_access: bool = True
    data_classification_handled: DataClassification
    security_controls_summary: str = ""
    certifications: str = ""
    has_incident_history: bool = False
    incident_history_notes: str = ""
    subprocessors: str = ""
    availability_sla_percent: float | None = None
    contractual_security_clause: bool = False
    data_retention_policy: str = ""
    exit_strategy_defined: bool = False


class VendorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    service_description: str
    business_criticality: Criticality
    data_access: bool
    data_classification_handled: DataClassification
    security_controls_summary: str
    certifications: str
    has_incident_history: bool
    incident_history_notes: str
    subprocessors: str
    availability_sla_percent: float | None
    contractual_security_clause: bool
    data_retention_policy: str
    exit_strategy_defined: bool


class VendorAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    likelihood: int
    impact: int
    score: int
    rating: str
    contributing_factors: list
    recommendation: str
    assessed_at: datetime
