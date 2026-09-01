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
