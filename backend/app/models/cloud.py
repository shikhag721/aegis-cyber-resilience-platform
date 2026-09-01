"""Cloud Security Posture (Section 12): structured findings, not a live
AWS/Azure/GCP integration - see docs/decisions/0005-synthetic-environment.md.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CloudFindingType(StrEnum):
    PUBLIC_EXPOSURE = "public_exposure"
    OVERLY_PERMISSIVE_IAM = "overly_permissive_iam"
    UNENCRYPTED_DATA = "unencrypted_data"
    MISSING_LOGGING = "missing_logging"
    OPEN_SECURITY_GROUP = "open_security_group"
    CONFIGURATION_DRIFT = "configuration_drift"
    EXPOSED_SECRET = "exposed_secret"  # nosec B105 - enum member name, not a credential


class CloudFindingSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CloudFindingStatus(StrEnum):
    OPEN = "open"
    REMEDIATED = "remediated"
    ACCEPTED_RISK = "accepted_risk"


class CloudFinding(Base):
    __tablename__ = "cloud_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_name: Mapped[str] = mapped_column(String(200))
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    finding_type: Mapped[CloudFindingType] = mapped_column(
        Enum(CloudFindingType, native_enum=False, length=32)
    )
    severity: Mapped[CloudFindingSeverity] = mapped_column(
        Enum(CloudFindingSeverity, native_enum=False, length=16)
    )
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    status: Mapped[CloudFindingStatus] = mapped_column(
        Enum(CloudFindingStatus, native_enum=False, length=16), default=CloudFindingStatus.OPEN
    )
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["Asset | None"] = relationship()  # noqa: F821
