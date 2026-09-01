"""Password hashing and JWT issuance/verification.

Cybersecurity concept: passwords are never stored or compared in plaintext.
Argon2id (via argon2-cffi) is used rather than bcrypt/passlib - it is
OWASP's current first-choice recommendation for password storage (memory-
hard, resistant to GPU/ASIC cracking), and avoids a known compatibility
bug between the unmaintained `passlib` library and modern `bcrypt`
releases (passlib's internal self-test raises ValueError against
bcrypt>=4.1 - see docs/decisions/ for this exact incident). JWTs here
carry only a username and role claim - never a password or secret.
"""
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
