from pydantic import BaseModel, ConfigDict

from app.models.appsec import AppSecFindingType, FindingSeverity, FindingStatus, SecretType


class AppSecFindingCreate(BaseModel):
    resource_name: str
    asset_id: int | None = None
    finding_type: AppSecFindingType
    severity: FindingSeverity
    description: str
    owasp_reference: str = ""
    recommendation: str


class AppSecFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_name: str
    asset_id: int | None
    finding_type: AppSecFindingType
    severity: FindingSeverity
    description: str
    owasp_reference: str
    recommendation: str
    status: FindingStatus


class SecretFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    secret_type: SecretType
    location: str
    severity: FindingSeverity
    exposure: str
    redacted_snippet: str
    rotation_recommendation: str
    status: FindingStatus


class SecretScanRequest(BaseModel):
    text: str
    location: str
    exposure: str = "Internal repository scan"
