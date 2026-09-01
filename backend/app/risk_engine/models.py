from dataclasses import dataclass, field
from enum import StrEnum


class RiskAppetite(StrEnum):
    """The organization's tolerance threshold. Anything scoring above this
    rating should not simply be Accepted - see suggest_treatment().
    """

    LOW = "low"  # only accepts Low risk without action
    MODERATE = "moderate"  # accepts up to Moderate
    HIGH = "high"  # accepts up to High (aggressive risk tolerance)


@dataclass
class RiskFactor:
    name: str
    axis: str  # "likelihood" or "impact"
    weight: int
    reason: str


@dataclass
class RiskInput:
    """Everything the engine needs to score one risk. Every field maps
    directly to something already captured elsewhere in the system (Asset
    criticality/exposure/classification from Phase 1, threat_severity from
    a Threat or a CVE's CVSS band in Phase 4) - the engine never invents
    its own notion of these concepts.
    """

    asset_criticality: str  # low/medium/high/critical
    data_classification: str  # public/internal/confidential/restricted/highly_restricted
    threat_severity: str  # low/medium/high/critical - e.g. derived from CVSS band or threat assessment
    internet_exposed: bool = False
    known_exploited: bool = False  # e.g. CISA KEV-style flag (Phase 4)
    logging_enabled: bool = True
    control_effectiveness: float = 0.0  # 0.0-1.0, see compute_residual
    context: str = ""  # free-text, surfaced in the primary_concern if most-weighted factor is generic


@dataclass
class RiskResult:
    likelihood: int
    impact: int
    inherent_score: int
    inherent_rating: str
    residual_score: int
    residual_rating: str
    contributing_factors: list[RiskFactor] = field(default_factory=list)
    primary_concern: str = ""
    recommended_treatment: str = ""
