"""Threat modeling and attack-path business logic."""
from sqlalchemy.orm import Session, joinedload

from app.models.threat import AttackPath, AttackPathStep, Threat, ThreatActor


def create_threat_actor(db: Session, data: dict) -> ThreatActor:
    actor = ThreatActor(**data)
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor


def list_threat_actors(db: Session) -> list[ThreatActor]:
    return db.query(ThreatActor).order_by(ThreatActor.name).all()


def create_threat(db: Session, data: dict) -> Threat:
    threat = Threat(**data)
    db.add(threat)
    db.commit()
    db.refresh(threat)
    return threat


def list_threats(db: Session) -> list[Threat]:
    return db.query(Threat).order_by(Threat.name).all()


def get_threat(db: Session, threat_id: int) -> Threat | None:
    return db.get(Threat, threat_id)


def create_attack_path(db: Session, data: dict) -> AttackPath:
    steps_data = data.pop("steps", [])
    attack_path = AttackPath(**data)
    db.add(attack_path)
    db.flush()  # assigns attack_path.id without committing yet

    for step_data in steps_data:
        db.add(AttackPathStep(attack_path_id=attack_path.id, **step_data))

    db.commit()
    db.refresh(attack_path)
    return attack_path


def get_attack_path(db: Session, attack_path_id: int) -> AttackPath | None:
    return (
        db.query(AttackPath)
        .options(joinedload(AttackPath.steps))
        .filter(AttackPath.id == attack_path_id)
        .first()
    )


def list_attack_paths(db: Session, target_asset_id: int | None = None) -> list[AttackPath]:
    query = db.query(AttackPath).options(joinedload(AttackPath.steps))
    if target_asset_id is not None:
        query = query.filter(AttackPath.target_asset_id == target_asset_id)
    # Highest score (likelihood x impact) first - the paths most worth a reviewer's attention.
    paths = query.all()
    return sorted(paths, key=lambda p: p.score, reverse=True)
