"""Unit tests for the role-based authorization guard itself (app.core.deps.require_role),
independent of any specific business endpoint - future protected routers can
rely on this dependency having been verified here.
"""
import pytest
from fastapi import HTTPException

from app.core.deps import require_role
from app.models.user import ROLE_ADMIN, ROLE_VIEWER, User


def _make_user(role: str) -> User:
    return User(username="u", email="u@test.local", hashed_password="x", role=role)


def test_require_role_allows_matching_role():
    checker = require_role(ROLE_ADMIN)
    result = checker(current_user=_make_user(ROLE_ADMIN))
    assert result.role == ROLE_ADMIN


def test_require_role_allows_any_of_multiple_roles():
    checker = require_role(ROLE_ADMIN, ROLE_VIEWER)
    result = checker(current_user=_make_user(ROLE_VIEWER))
    assert result.role == ROLE_VIEWER


def test_require_role_rejects_non_matching_role():
    checker = require_role(ROLE_ADMIN)
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=_make_user(ROLE_VIEWER))
    assert exc_info.value.status_code == 403
