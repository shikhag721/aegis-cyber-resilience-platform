"""IAM Risk (Section 11): models Northstar's own identity environment -
distinct from AEGIS's own `User`/auth model, the same way an asset
inventory models the organization's systems rather than this tool's own
infrastructure.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AccountType(StrEnum):
    HUMAN = "human"
    SERVICE = "service"


class EmploymentStatus(StrEnum):
    ACTIVE = "active"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    N_A = "n_a"  # service accounts


class IdentityAccount(Base):
    __tablename__ = "identity_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    display_name: Mapped[str] = mapped_column(String(150))
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType, native_enum=False, length=16))
    department: Mapped[str] = mapped_column(String(150))
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus, native_enum=False, length=16)
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    production_access: Mapped[bool] = mapped_column(Boolean, default=False)
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    associated_asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    associated_asset: Mapped["Asset | None"] = relationship()  # noqa: F821
