from datetime import date

from pydantic import BaseModel, ConfigDict


class ContinuityPlanCreate(BaseModel):
    asset_id: int
    rto_hours: int | None = None
    rpo_hours: int | None = None
    backup_frequency: str = ""
    last_backup_tested_at: date | None = None
    last_dr_test_at: date | None = None
    dr_test_result: str = ""
    recovery_dependencies: list[str] = []
    business_impact_if_unavailable: str = ""


class ContinuityPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    rto_hours: int | None
    rpo_hours: int | None
    backup_frequency: str
    last_backup_tested_at: date | None
    last_dr_test_at: date | None
    dr_test_result: str
    recovery_dependencies: list[str]
    business_impact_if_unavailable: str


class ContinuityFindingRead(BaseModel):
    asset_name: str
    finding_type: str
    severity: str
    detail: str
