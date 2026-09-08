"""In-memory rate limiting (slowapi/limits) for brute-force protection on
authentication endpoints. In-memory storage is a documented, accepted
tradeoff for this single-process demo deployment - see
docs/architecture/limitations.md; a real multi-instance deployment would
need a shared backend (Redis) instead.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

limiter = Limiter(key_func=get_remote_address, enabled=get_settings().rate_limit_enabled)
