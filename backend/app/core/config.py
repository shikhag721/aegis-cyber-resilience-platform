"""Centralized application configuration.

All settings are read from environment variables (see .env.example).
Nothing here hardcodes a real secret - defaults are safe-for-local-dev
placeholders only, and production deployments must override every secret
value via the environment. See SECURITY.md.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./aegis_dev.db"

    jwt_secret_key: str = "insecure-dev-only-override-in-.env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_allowed_origins: str = "http://localhost:5173"

    # slowapi rate-limit string, e.g. "10/minute" - applied to /auth/login
    # to blunt credential-stuffing/brute-force attempts (Phase 14 hardening).
    login_rate_limit: str = "10/minute"
    # Disabled only by the test suite (conftest.py sets this before the app
    # is imported) - tests authenticate dozens of times per run via the
    # real /auth/login endpoint, which would otherwise trip the limiter.
    rate_limit_enabled: bool = True

    anthropic_api_key: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
