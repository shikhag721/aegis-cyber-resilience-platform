"""Data Security (Section 21): a catalog of WHERE specific sensitive data
categories actually live, distinct from Asset.data_classification (which
describes an asset's overall handling tier). A single asset can hold
multiple data categories with different exposure profiles - e.g. the
Customer Database holds both PII and financial data, each independently
assessed here.
"""
from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.asset import DataClassification


class DataCategory(StrEnum):
    PII = "pii"
    FINANCIAL_DATA = "financial_data"
    CREDENTIALS = "credentials"
    SECRETS = "secrets"
    BUSINESS_DATA = "business_data"
    AI_DATA = "ai_data"


class DataAsset(Base):
    __tablename__ = "data_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))  # e.g. "Customer PII in Customer Database"
    category: Mapped[DataCategory] = mapped_column(Enum(DataCategory, native_enum=False, length=24))
    classification: Mapped[DataClassification] = mapped_column(
        Enum(DataClassification, native_enum=False, length=24)
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    access_controlled: Mapped[bool] = mapped_column(Boolean, default=False)
    retention_defined: Mapped[bool] = mapped_column(Boolean, default=False)
    retention_period_days: Mapped[int | None] = mapped_column(nullable=True)
    exposure_notes: Mapped[str] = mapped_column(Text, default="")

    asset: Mapped["Asset"] = relationship()  # noqa: F821
