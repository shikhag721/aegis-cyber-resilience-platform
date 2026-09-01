"""Seed demo users and the Northstar Financial Services asset inventory for
local/demo use.

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
from app.services import asset as asset_service
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


def seed_assets(db) -> None:
    if asset_service.list_assets(db):
        print("Assets already seeded - skipping.")
        return

    tag_to_id = {}
    for data in NORTHSTAR_ASSETS:
        asset = asset_service.create_asset(db, data)
        tag_to_id[asset.asset_tag] = asset.id
    print(f"Created {len(NORTHSTAR_ASSETS)} Northstar Financial Services assets.")

    for from_tag, to_tag, description in NORTHSTAR_ASSET_DEPENDENCIES:
        asset_service.add_dependency(db, tag_to_id[from_tag], tag_to_id[to_tag], description)
    print(f"Created {len(NORTHSTAR_ASSET_DEPENDENCIES)} asset dependencies.")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
        seed_assets(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
