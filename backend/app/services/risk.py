"""Risk Register business logic - bridges Asset data + the pure risk_engine
into a persisted, historical RiskRecord.
"""
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.risk import RiskRecord
from app.risk_engine import RiskAppetite, RiskInput, assess


def create_risk_record(db: Session, data: dict) -> RiskRecord:
    asset = db.get(Asset, data["asset_id"])
    if not asset:
        raise ValueError(f"Asset {data['asset_id']} not found")

    engine_input = RiskInput(
        asset_criticality=asset.criticality.value,
        data_classification=asset.data_classification.value,
        threat_severity=data["threat_severity"],
        internet_exposed=asset.internet_exposed,
        known_exploited=data.get("known_exploited", False),
        logging_enabled=asset.logging_enabled,
        control_effectiveness=data.get("control_effectiveness", 0.0),
    )
    appetite = RiskAppetite(data.get("risk_appetite", "moderate"))
    result = assess(engine_input, appetite)

    record = RiskRecord(
        title=data["title"],
        description=data["description"],
        asset_id=asset.id,
        threat_id=data.get("threat_id"),
        attack_path_id=data.get("attack_path_id"),
        asset_criticality=engine_input.asset_criticality,
        data_classification=engine_input.data_classification,
        threat_severity=engine_input.threat_severity,
        internet_exposed=engine_input.internet_exposed,
        known_exploited=engine_input.known_exploited,
        logging_enabled=engine_input.logging_enabled,
        control_effectiveness=engine_input.control_effectiveness,
        risk_appetite=appetite.value,
        likelihood=result.likelihood,
        impact=result.impact,
        inherent_score=result.inherent_score,
        inherent_rating=result.inherent_rating,
        residual_score=result.residual_score,
        residual_rating=result.residual_rating,
        contributing_factors=[
            {"name": f.name, "axis": f.axis, "weight": f.weight, "reason": f.reason}
            for f in result.contributing_factors
        ],
        primary_concern=result.primary_concern,
        recommended_treatment=result.recommended_treatment,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_risk_record(db: Session, risk_id: int) -> RiskRecord | None:
    return db.get(RiskRecord, risk_id)


def list_risk_records(
    db: Session, asset_id: int | None = None, status: str | None = None
) -> list[RiskRecord]:
    query = db.query(RiskRecord)
    if asset_id is not None:
        query = query.filter(RiskRecord.asset_id == asset_id)
    if status is not None:
        query = query.filter(RiskRecord.status == status)
    records = query.all()
    # Highest residual score first - what a reviewer should look at first.
    return sorted(records, key=lambda r: r.residual_score, reverse=True)


def update_treatment(db: Session, record: RiskRecord, changes: dict) -> RiskRecord:
    for field, value in changes.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record
