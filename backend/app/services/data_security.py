"""Data security cataloging and gap analysis (Section 21)."""
from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload

from app.models.data_security import DataAsset

_HIGH_SENSITIVITY_CLASSIFICATIONS = {"restricted", "highly_restricted"}


def create_data_asset(db: Session, data: dict) -> DataAsset:
    data_asset = DataAsset(**data)
    db.add(data_asset)
    db.commit()
    db.refresh(data_asset)
    return data_asset


def list_data_assets(db: Session) -> list[DataAsset]:
    return db.query(DataAsset).options(joinedload(DataAsset.asset)).all()


@dataclass
class DataSecurityFinding:
    data_asset_name: str
    finding_type: str
    severity: str
    detail: str


def analyze_data_security(db: Session) -> list[DataSecurityFinding]:
    findings: list[DataSecurityFinding] = []

    for data_asset in list_data_assets(db):
        is_sensitive = data_asset.classification.value in _HIGH_SENSITIVITY_CLASSIFICATIONS

        if is_sensitive and not data_asset.encrypted:
            findings.append(
                DataSecurityFinding(
                    data_asset_name=data_asset.name,
                    finding_type="unencrypted_sensitive_data",
                    severity="critical",
                    detail=(
                        f"'{data_asset.name}' is classified {data_asset.classification.value} but is "
                        "not encrypted."
                    ),
                )
            )

        if is_sensitive and not data_asset.access_controlled:
            findings.append(
                DataSecurityFinding(
                    data_asset_name=data_asset.name,
                    finding_type="missing_access_control",
                    severity="high",
                    detail=(
                        f"'{data_asset.name}' has no confirmed access control restricting who can read it."
                    ),
                )
            )

        if not data_asset.retention_defined:
            findings.append(
                DataSecurityFinding(
                    data_asset_name=data_asset.name,
                    finding_type="no_retention_policy",
                    severity="medium",
                    detail=f"'{data_asset.name}' has no defined data retention period.",
                )
            )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_rank.get(f.severity, 4))
    return findings
