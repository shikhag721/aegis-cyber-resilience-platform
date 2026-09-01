"""Authentication service logic - kept out of the router so it's unit
testable without spinning up FastAPI's request/response cycle.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, email: str, password: str, role: str) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Returns the user only if the account exists, is active, and the
    password is correct. Deliberately returns the same generic failure
    (None) for "no such user" and "wrong password" so a login endpoint
    cannot be used to enumerate valid usernames.
    """
    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return user
