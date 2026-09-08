"""Verifies /auth/login is actually rate-limited (Phase 14 hardening).

The rest of the suite disables rate limiting globally (conftest.py sets
RATE_LIMIT_ENABLED=false) because make_auth_headers() calls the real
login endpoint dozens of times per run. This file re-enables the shared
limiter for its own tests only, and always restores it afterward.
"""
import pytest

from app.core.rate_limit import limiter
from app.db.session import SessionLocal
from app.services.auth import create_user


@pytest.fixture
def _enable_rate_limiting():
    limiter.enabled = True
    limiter.reset()
    yield
    limiter.reset()
    limiter.enabled = False


def test_login_is_rate_limited_after_threshold(client, _enable_rate_limiting):
    db = SessionLocal()
    try:
        create_user(db, "ratelimit_user", "ratelimit@test.local", "TestPassword123!", "viewer")
    finally:
        db.close()

    statuses = [
        client.post(
            "/api/v1/auth/login",
            data={"username": "ratelimit_user", "password": "wrong-password"},
        ).status_code
        for _ in range(15)
    ]

    assert 401 in statuses  # failed-auth attempts still reach the handler until the limit trips
    assert 429 in statuses  # and the limiter eventually kicks in
    assert statuses.index(429) > statuses.index(401)


def test_login_disabled_by_default_in_test_suite(client):
    """Sanity check on the opt-in fixture above: without it, rate limiting
    is off, so far more than the configured limit succeeds through to the
    real auth check (401 for bad creds, never 429)."""
    statuses = [
        client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent_user", "password": "wrong-password"},
        ).status_code
        for _ in range(15)
    ]
    assert all(s == 401 for s in statuses)
