from pydantic import BaseModel, ConfigDict

from app.models.cloud import CloudFindingSeverity, CloudFindingStatus, CloudFindingType


class CloudFindingCreate(BaseModel):
    resource_name: str
    asset_id: int | None = None
    finding_type: CloudFindingType
    severity: CloudFindingSeverity
    description: str
    recommendation: str


class CloudFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_name: str
    asset_id: int | None
    finding_type: CloudFindingType
    severity: CloudFindingSeverity
    description: str
    recommendation: str
    status: CloudFindingStatus
