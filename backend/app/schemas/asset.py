from pydantic import BaseModel, ConfigDict

from app.models.asset import AssetType, Criticality, DataClassification, Environment


class AssetCreate(BaseModel):
    asset_tag: str
    name: str
    asset_type: AssetType
    owner: str
    business_unit: str
    environment: Environment
    criticality: Criticality
    data_classification: DataClassification
    internet_exposed: bool = False
    technology: str = ""
    authentication_method: str = "Unknown"
    encrypted: bool = False
    logging_enabled: bool = False
    backup_enabled: bool = False
    notes: str = ""


class AssetUpdate(BaseModel):
    """All fields optional - PATCH semantics."""

    name: str | None = None
    owner: str | None = None
    business_unit: str | None = None
    environment: Environment | None = None
    criticality: Criticality | None = None
    data_classification: DataClassification | None = None
    internet_exposed: bool | None = None
    technology: str | None = None
    authentication_method: str | None = None
    encrypted: bool | None = None
    logging_enabled: bool | None = None
    backup_enabled: bool | None = None
    notes: str | None = None


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_tag: str
    name: str
    asset_type: AssetType
    owner: str
    business_unit: str
    environment: Environment
    criticality: Criticality
    data_classification: DataClassification
    internet_exposed: bool
    technology: str
    authentication_method: str
    encrypted: bool
    logging_enabled: bool
    backup_enabled: bool
    notes: str


class AssetDependencyCreate(BaseModel):
    depends_on_asset_id: int
    description: str = ""


class AssetDependencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    depends_on_asset_id: int
    description: str
