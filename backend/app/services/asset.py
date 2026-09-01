"""Asset inventory business logic - kept out of the router so it is
directly unit-testable without spinning up HTTP.
"""
from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetDependency, AssetType, Criticality, Environment

# Criticality is stored as its string value (native_enum=False), so a plain
# alphabetical ORDER BY would sort "critical" before "high" incorrectly
# (c < h < l < m). This CASE expression orders by actual severity instead -
# getting risk-relevant ordering right at the query level matters
# throughout this project (see Section 9's CVSS-vs-business-risk example).
_CRITICALITY_RANK = case(
    (Asset.criticality == Criticality.CRITICAL, 4),
    (Asset.criticality == Criticality.HIGH, 3),
    (Asset.criticality == Criticality.MEDIUM, 2),
    (Asset.criticality == Criticality.LOW, 1),
    else_=0,
)


def create_asset(db: Session, data: dict) -> Asset:
    asset = Asset(**data)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_asset(db: Session, asset_id: int) -> Asset | None:
    return db.get(Asset, asset_id)


def update_asset(db: Session, asset: Asset, changes: dict) -> Asset:
    for field, value in changes.items():
        if value is not None:
            setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset: Asset) -> None:
    db.delete(asset)
    db.commit()


def list_assets(
    db: Session,
    search: str | None = None,
    asset_type: AssetType | None = None,
    environment: Environment | None = None,
    criticality: Criticality | None = None,
    internet_exposed: bool | None = None,
) -> list[Asset]:
    query = db.query(Asset)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(Asset.name.ilike(like), Asset.asset_tag.ilike(like), Asset.owner.ilike(like))
        )
    if asset_type is not None:
        query = query.filter(Asset.asset_type == asset_type)
    if environment is not None:
        query = query.filter(Asset.environment == environment)
    if criticality is not None:
        query = query.filter(Asset.criticality == criticality)
    if internet_exposed is not None:
        query = query.filter(Asset.internet_exposed == internet_exposed)

    return query.order_by(_CRITICALITY_RANK.desc(), Asset.name).all()


def add_dependency(db: Session, asset_id: int, depends_on_asset_id: int, description: str) -> AssetDependency:
    if asset_id == depends_on_asset_id:
        raise ValueError("An asset cannot depend on itself.")
    dependency = AssetDependency(
        asset_id=asset_id, depends_on_asset_id=depends_on_asset_id, description=description
    )
    db.add(dependency)
    db.commit()
    db.refresh(dependency)
    return dependency
