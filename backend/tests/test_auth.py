import pytest

from app.db.session import SessionLocal
from app.models.user import ROLE_ADMIN, ROLE_VIEWER
from app.services.auth import create_user


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def admin_user(db_session):
    return create_user(db_session, "test_admin", "admin@test.local", "CorrectHorse123!", ROLE_ADMIN)


@pytest.fixture
def viewer_user(db_session):
    return create_user(db_session, "test_viewer", "viewer@test.local", "CorrectHorse123!", ROLE_VIEWER)


def test_login_success(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin", "password": "CorrectHorse123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_unknown_user_fails_with_same_message_as_wrong_password(client):
    """Guards against username enumeration: both failure modes must return
    the same status/detail.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "does_not_exist", "password": "whatever"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client, admin_user):
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin", "password": "CorrectHorse123!"},
    )
    token = login.json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "test_admin"
    assert response.json()["role"] == ROLE_ADMIN


def test_me_rejects_invalid_token(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_inactive_user_cannot_login(client, db_session):
    user = create_user(db_session, "inactive_user", "inactive@test.local", "CorrectHorse123!", ROLE_VIEWER)
    user.is_active = False
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "inactive_user", "password": "CorrectHorse123!"},
    )
    assert response.status_code == 401
