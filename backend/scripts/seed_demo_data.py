"""Seed an initial demo admin user for local/demo use.

Run: python scripts/seed_demo_data.py (from backend/)

The password below is a LOCAL DEMO CREDENTIAL for the fictional Northstar
Financial Services environment, not a real secret - it is only usable
against your own local Docker Compose stack. Override via
DEMO_ADMIN_PASSWORD if you want a different one. See SECURITY.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import ROLE_ADMIN
from app.services.auth import create_user, get_user_by_username

DEMO_ADMIN_USERNAME = "admin"
DEMO_ADMIN_EMAIL = "admin@northstar-financial.example"
DEMO_ADMIN_PASSWORD = os.getenv("DEMO_ADMIN_PASSWORD", "ChangeMe123!")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if get_user_by_username(db, DEMO_ADMIN_USERNAME):
            print(f"Demo admin user '{DEMO_ADMIN_USERNAME}' already exists - skipping.")
            return
        create_user(db, DEMO_ADMIN_USERNAME, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD, ROLE_ADMIN)
        print(f"Created demo admin user '{DEMO_ADMIN_USERNAME}' (local/demo use only).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
