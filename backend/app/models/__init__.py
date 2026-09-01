"""Import every model module here so Base.metadata (and Alembic
autogenerate) can discover all tables from a single import.
"""
from app.models.asset import Asset, AssetDependency  # noqa: F401
from app.models.risk import RiskRecord  # noqa: F401
from app.models.threat import AttackPath, AttackPathStep, Threat, ThreatActor  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.vulnerability import Vulnerability  # noqa: F401
