from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.identity import AccountType, EmploymentStatus


class IdentityAccountCreate(BaseModel):
    username: str
    display_name: str
    account_type: AccountType
    department: str
    employment_status: EmploymentStatus
    is_enabled: bool = True
    is_privileged: bool = False
    mfa_enabled: bool = False
    production_access: bool = False
    permissions: list[str] = []
    last_login_at: datetime | None = None
    associated_asset_id: int | None = None


class IdentityAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    account_type: AccountType
    department: str
    employment_status: EmploymentStatus
    is_enabled: bool
    is_privileged: bool
    mfa_enabled: bool
    production_access: bool
    permissions: list[str]
    last_login_at: datetime | None
    associated_asset_id: int | None


class IAMFindingRead(BaseModel):
    account_username: str
    finding_type: str
    severity: str
    detail: str
