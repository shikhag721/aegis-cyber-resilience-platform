"""Asset inventory model (Section 7 of the project brief).

An "asset" here is deliberately broad - a server, endpoint, API, database,
cloud resource, container, identity, SaaS product, network device, or AI
system. Later phases (vulnerabilities, IAM, cloud, AI) all point back to
an Asset row rather than duplicating ownership/criticality/exposure
fields, so "what's the business impact if this is compromised" always has
one authoritative place to look.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssetType(StrEnum):
    SERVER = "server"
    ENDPOINT = "endpoint"
    API = "api"
    APPLICATION = "application"
    DATABASE = "database"
    CLOUD_RESOURCE = "cloud_resource"
    CONTAINER = "container"
    IDENTITY = "identity"
    SAAS = "saas"
    NETWORK_DEVICE = "network_device"
    AI_SYSTEM = "ai_system"


class Environment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TEST = "test"


class Criticality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataClassification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    HIGHLY_RESTRICTED = "highly_restricted"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType, native_enum=False, length=32))
    owner: Mapped[str] = mapped_column(String(150))
    business_unit: Mapped[str] = mapped_column(String(150))
    environment: Mapped[Environment] = mapped_column(Enum(Environment, native_enum=False, length=16))
    criticality: Mapped[Criticality] = mapped_column(Enum(Criticality, native_enum=False, length=16))
    data_classification: Mapped[DataClassification] = mapped_column(
        Enum(DataClassification, native_enum=False, length=24)
    )
    internet_exposed: Mapped[bool] = mapped_column(default=False)
    technology: Mapped[str] = mapped_column(String(200), default="")
    authentication_method: Mapped[str] = mapped_column(String(100), default="Unknown")
    encrypted: Mapped[bool] = mapped_column(default=False)
    logging_enabled: Mapped[bool] = mapped_column(default=False)
    backup_enabled: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    dependencies: Mapped[list["AssetDependency"]] = relationship(
        back_populates="asset", foreign_keys="AssetDependency.asset_id", cascade="all, delete-orphan"
    )


class AssetDependency(Base):
    """A directed edge: `asset` depends on `depends_on_asset`.

    Modeled as its own table (not a self-referential FK column) so an
    asset can depend on multiple others - this is what threat modeling
    (Phase 2) walks to build a data-flow / attack-path graph, e.g.
    "API Gateway depends_on Application depends_on Database."
    """

    __tablename__ = "asset_dependencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    depends_on_asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    description: Mapped[str] = mapped_column(String(255), default="")

    asset: Mapped["Asset"] = relationship(foreign_keys=[asset_id], back_populates="dependencies")
    depends_on_asset: Mapped["Asset"] = relationship(foreign_keys=[depends_on_asset_id])
