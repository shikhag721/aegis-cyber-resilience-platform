"""Seed demo users, the Northstar Financial Services asset inventory, and
its threat model for local/demo use.

Run: python scripts/seed_demo_data.py (from backend/)

Passwords below are LOCAL DEMO CREDENTIALS for the fictional Northstar
Financial Services environment, not real secrets - usable only against
your own local Docker Compose stack. Override via the DEMO_*_PASSWORD env
vars if you want different ones. See SECURITY.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.seed_data.northstar_assets import NORTHSTAR_ASSET_DEPENDENCIES, NORTHSTAR_ASSETS
from app.seed_data.northstar_threats import (
    NORTHSTAR_ATTACK_PATHS,
    NORTHSTAR_THREAT_ACTORS,
    NORTHSTAR_THREATS,
)
from app.services import asset as asset_service
from app.services import threat as threat_service
from app.services.auth import create_user, get_user_by_username

DEMO_USERS = [
    (
        "admin",
        "admin@northstar-financial.example",
        ROLE_ADMIN,
        os.getenv("DEMO_ADMIN_PASSWORD", "ChangeMe123!"),
    ),
    (
        "risk_analyst",
        "risk.analyst@northstar-financial.example",
        ROLE_RISK_ANALYST,
        os.getenv("DEMO_ANALYST_PASSWORD", "ChangeMe123!"),
    ),
    (
        "viewer",
        "viewer@northstar-financial.example",
        ROLE_VIEWER,
        os.getenv("DEMO_VIEWER_PASSWORD", "ChangeMe123!"),
    ),
]


def seed_users(db) -> None:
    for username, email, role, password in DEMO_USERS:
        if get_user_by_username(db, username):
            print(f"User '{username}' already exists - skipping.")
            continue
        create_user(db, username, email, password, role)
        print(f"Created demo user '{username}' ({role}) - local/demo use only.")


def seed_assets(db) -> dict[str, int]:
    existing = asset_service.list_assets(db)
    if existing:
        print("Assets already seeded - skipping.")
        return {a.asset_tag: a.id for a in existing}

    tag_to_id = {}
    for data in NORTHSTAR_ASSETS:
        asset = asset_service.create_asset(db, data)
        tag_to_id[asset.asset_tag] = asset.id
    print(f"Created {len(NORTHSTAR_ASSETS)} Northstar Financial Services assets.")

    for from_tag, to_tag, description in NORTHSTAR_ASSET_DEPENDENCIES:
        asset_service.add_dependency(db, tag_to_id[from_tag], tag_to_id[to_tag], description)
    print(f"Created {len(NORTHSTAR_ASSET_DEPENDENCIES)} asset dependencies.")

    return tag_to_id


def seed_threats(db, tag_to_id: dict[str, int]) -> None:
    if threat_service.list_threat_actors(db):
        print("Threat model already seeded - skipping.")
        return

    actor_name_to_id = {}
    for data in NORTHSTAR_THREAT_ACTORS:
        actor = threat_service.create_threat_actor(db, data)
        actor_name_to_id[actor.name] = actor.id
    print(f"Created {len(NORTHSTAR_THREAT_ACTORS)} threat actors.")

    threat_name_to_id = {}
    for name, description, mitre_id, mitre_name, why_relevant, actor_name in NORTHSTAR_THREATS:
        threat = threat_service.create_threat(
            db,
            dict(
                name=name,
                description=description,
                mitre_technique_id=mitre_id,
                mitre_technique_name=mitre_name,
                why_relevant=why_relevant,
                threat_actor_id=actor_name_to_id.get(actor_name) if actor_name else None,
            ),
        )
        threat_name_to_id[threat.name] = threat.id
    print(f"Created {len(NORTHSTAR_THREATS)} threats.")

    for path_data in NORTHSTAR_ATTACK_PATHS:
        steps = [
            {
                "sequence": step["sequence"],
                "description": step["description"],
                "asset_id": tag_to_id.get(step["asset_tag"]) if step.get("asset_tag") else None,
                "threat_id": threat_name_to_id.get(step["threat_name"]) if step.get("threat_name") else None,
            }
            for step in path_data["steps"]
        ]
        threat_service.create_attack_path(
            db,
            dict(
                name=path_data["name"],
                description=path_data["description"],
                entry_point=path_data["entry_point"],
                target_asset_id=tag_to_id[path_data["target_asset_tag"]],
                likelihood=path_data["likelihood"],
                impact=path_data["impact"],
                notes=path_data["notes"],
                steps=steps,
            ),
        )
    print(f"Created {len(NORTHSTAR_ATTACK_PATHS)} attack paths.")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
        tag_to_id = seed_assets(db)
        seed_threats(db, tag_to_id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
