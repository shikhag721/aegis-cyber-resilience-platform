"""Application/API security findings (Section 13) and secrets/key
management findings (Section 14). See docs/decisions/0007-app-security-route.md
for why these live under their own route rather than being folded into
Vulnerability Management or Cloud Security.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AppSecFindingType(StrEnum):
    BROKEN_AUTHENTICATION = "broken_authentication"
    BROKEN_AUTHORIZATION = "broken_authorization"
    INJECTION = "injection"
    INSECURE_CONFIGURATION = "insecure_configuration"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    MISSING_RATE_LIMITING = "missing_rate_limiting"
    SESSION_SECURITY = "session_security"


class FindingSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(StrEnum):
    OPEN = "open"
    REMEDIATED = "remediated"
    ACCEPTED_RISK = "accepted_risk"


class AppSecFinding(Base):
    __tablename__ = "appsec_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_name: Mapped[str] = mapped_column(String(200))  # e.g. "POST /api/v1/accounts/{id}/transfer"
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    finding_type: Mapped[AppSecFindingType] = mapped_column(
        Enum(AppSecFindingType, native_enum=False, length=32)
    )
    severity: Mapped[FindingSeverity] = mapped_column(Enum(FindingSeverity, native_enum=False, length=16))
    description: Mapped[str] = mapped_column(Text)
    owasp_reference: Mapped[str] = mapped_column(String(100), default="")
    recommendation: Mapped[str] = mapped_column(Text)
    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus, native_enum=False, length=16), default=FindingStatus.OPEN
    )
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["Asset | None"] = relationship()  # noqa: F821


class SecretType(StrEnum):
    AWS_ACCESS_KEY = "aws_access_key"
    GENERIC_API_KEY = "generic_api_key"
    SLACK_TOKEN = "slack_token"  # nosec B105 - enum member name, not a credential
    PRIVATE_KEY = "private_key"
    PASSWORD_ASSIGNMENT = "password_assignment"  # nosec B105 - enum member name, not a credential


class SecretFinding(Base):
    __tablename__ = "secret_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    secret_type: Mapped[SecretType] = mapped_column(Enum(SecretType, native_enum=False, length=32))
    location: Mapped[str] = mapped_column(String(255))  # e.g. "repo:northstar/legacy-app, config.py:14"
    severity: Mapped[FindingSeverity] = mapped_column(Enum(FindingSeverity, native_enum=False, length=16))
    exposure: Mapped[str] = mapped_column(String(255))  # e.g. "public GitHub repository"
    redacted_snippet: Mapped[str] = mapped_column(String(120))
    rotation_recommendation: Mapped[str] = mapped_column(Text)
    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus, native_enum=False, length=16), default=FindingStatus.OPEN
    )
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
