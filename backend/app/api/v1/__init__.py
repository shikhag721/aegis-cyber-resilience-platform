"""API v1 router aggregation.

Each domain module owns one router file here and is mounted in
app/main.py. Keeping this file as the single place that lists every
mounted domain router makes it easy to see the full API surface at a
glance rather than hunting through main.py.
"""
from fastapi import APIRouter

from app.api.v1 import (
    app_security,
    assets,
    audit,
    auth,
    cloud,
    continuity,
    controls,
    data_security,
    evidence,
    health,
    iam,
    incidents,
    monitoring,
    risk,
    threat_modeling,
    vendors,
    vulnerabilities,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(assets.router)
api_router.include_router(threat_modeling.router)
api_router.include_router(risk.router)
api_router.include_router(vulnerabilities.router)
api_router.include_router(iam.router)
api_router.include_router(cloud.router)
api_router.include_router(app_security.router)
api_router.include_router(monitoring.router)
api_router.include_router(incidents.router)
api_router.include_router(controls.router)
api_router.include_router(evidence.router)
api_router.include_router(audit.router)
api_router.include_router(vendors.router)
api_router.include_router(data_security.router)
api_router.include_router(continuity.router)
