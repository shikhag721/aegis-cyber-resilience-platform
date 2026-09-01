"""Test configuration.

Forces an isolated, file-based SQLite test database BEFORE any app module
is imported, so the test suite never touches a developer's local Postgres
data. CI overrides DATABASE_URL to a real Postgres service container for
the subset of tests that need to exercise Postgres-specific behaviour
(see docs/testing/README.md).
"""
import os
import tempfile

TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "aegis_backend_test.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-not-for-production")

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    """Truncates every table before each test so fixtures like
    tests/test_auth.py::admin_user can insert the same username across
    multiple tests without a UNIQUE-constraint collision, and so no test
    can observe data left behind by another. Runs in reverse dependency
    order to respect foreign keys.
    """
    yield
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def make_auth_headers(client):
    """Factory fixture: make_auth_headers("admin") -> creates a fresh user
    with that role and returns {"Authorization": "Bearer <token>"},
    reusable by every domain's API tests for RBAC assertions.
    """
    from app.db.session import SessionLocal
    from app.services.auth import create_user

    counter = {"n": 0}

    def _make(role: str) -> dict:
        counter["n"] += 1
        username = f"{role}_user_{counter['n']}"
        db = SessionLocal()
        try:
            create_user(db, username, f"{username}@test.local", "TestPassword123!", role)
        finally:
            db.close()
        login = client.post(
            "/api/v1/auth/login", data={"username": username, "password": "TestPassword123!"}
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make
