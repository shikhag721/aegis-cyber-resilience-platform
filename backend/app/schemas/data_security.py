from pydantic import BaseModel, ConfigDict

from app.models.asset import DataClassification
from app.models.data_security import DataCategory


class DataAssetCreate(BaseModel):
    name: str
    category: DataCategory
    classification: DataClassification
    asset_id: int
    encrypted: bool = False
    access_controlled: bool = False
    retention_defined: bool = False
    retention_period_days: int | None = None
    exposure_notes: str = ""


class DataAssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: DataCategory
    classification: DataClassification
    asset_id: int
    encrypted: bool
    access_controlled: bool
    retention_defined: bool
    retention_period_days: int | None
    exposure_notes: str


class DataSecurityFindingRead(BaseModel):
    data_asset_name: str
    finding_type: str
    severity: str
    detail: str
