"""AEGIS backend application factory.

Security controls applied here (see SECURITY.md):
- CORS restricted to configured origins only.
- Baseline security response headers on every response.
- No debug/reload in non-development environments (enforced by the
  Dockerfile/uvicorn invocation, not this module).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 - registers all ORM models on Base.metadata
from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AEGIS - Enterprise Cyber Resilience & AI Security Risk Platform",
        description=(
            "Portfolio project simulating the security and AI-risk program of a fictional "
            "financial services company. Not a production security product - see SECURITY.md."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
