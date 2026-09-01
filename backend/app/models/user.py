"""User identity model.

Roles are a plain string column (not a separate roles/permissions table
yet) - deliberately minimal for Phase 0. Phase 5 (IAM) introduces the
richer roles/permissions/groups model described in docs/architecture/;
this model is the seed that IAM risk analysis will later examine (e.g.
"orphan account," "missing MFA") rather than a placeholder to be thrown
away.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

ROLE_ADMIN = "admin"
ROLE_RISK_ANALYST = "risk_analyst"
ROLE_VIEWER = "viewer"

VALID_ROLES = {ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default=ROLE_VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
