"""Import every model module here so Base.metadata (and Alembic
autogenerate) can discover all tables from a single import.
"""
from app.models.appsec import AppSecFinding, SecretFinding  # noqa: F401
from app.models.asset import Asset, AssetDependency  # noqa: F401
from app.models.audit import AuditLogEntry  # noqa: F401
from app.models.cloud import CloudFinding  # noqa: F401
from app.models.continuity import ContinuityPlan  # noqa: F401
from app.models.control import Control, ControlAssessment, Evidence  # noqa: F401
from app.models.data_security import DataAsset  # noqa: F401
from app.models.identity import IdentityAccount  # noqa: F401
from app.models.incident import Incident, IncidentTimelineEntry  # noqa: F401
from app.models.monitoring import SecurityEvent  # noqa: F401
from app.models.risk import RiskRecord  # noqa: F401
from app.models.threat import AttackPath, AttackPathStep, Threat, ThreatActor  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.vendor import Vendor, VendorAssessment  # noqa: F401
from app.models.vulnerability import Vulnerability  # noqa: F401
