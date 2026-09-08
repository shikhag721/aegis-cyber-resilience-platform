"""Executive dashboard + reports (Phase 13). Pure aggregation over data
already produced by every other domain module - no new state, no new
scoring logic. Every number here is either a stored field (asset
criticality, risk residual rating) or the output of an existing
deterministic analyzer (analyze_ai_inventory, analyze_control_gaps, etc.),
never a new judgment call invented for the dashboard itself.
"""
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.services import agent as agent_service
from app.services import ai as ai_service
from app.services import appsec as appsec_service
from app.services import asset as asset_service
from app.services import cloud as cloud_service
from app.services import continuity as continuity_service
from app.services import controls as controls_service
from app.services import data_security as data_security_service
from app.services import iam as iam_service
from app.services import incident as incident_service
from app.services import rag as rag_service
from app.services import risk as risk_service
from app.services import vendor as vendor_service
from app.services import vulnerability as vuln_service

_OPEN_INCIDENT_STAGES = {"detection", "triage", "investigation", "containment", "eradication", "recovery"}
_OPEN_VULN_STATUSES = {"open", "in_progress"}
_HIGH_OR_CRITICAL = {"high", "critical"}


@dataclass
class ExecutiveSummary:
    assets_total: int = 0
    assets_by_criticality: dict = field(default_factory=dict)

    risks_open: int = 0
    risks_by_residual_rating: dict = field(default_factory=dict)

    vulnerabilities_open: int = 0
    vulnerabilities_overdue: int = 0
    vulnerabilities_known_exploited_open: int = 0

    iam_findings_total: int = 0
    iam_findings_critical: int = 0
    cloud_findings_open: int = 0
    appsec_findings_open: int = 0
    secrets_open: int = 0

    incidents_open: int = 0
    incidents_open_high_or_critical: int = 0

    control_gaps_total: int = 0
    control_gaps_critical: int = 0

    vendors_high_or_critical: int = 0
    data_security_findings: int = 0
    continuity_findings: int = 0

    ai_governance_gaps: int = 0
    ai_governance_gaps_critical: int = 0
    rag_findings: int = 0
    agents_high_or_critical: int = 0


def build_executive_summary(db: Session) -> ExecutiveSummary:
    summary = ExecutiveSummary()

    assets = asset_service.list_assets(db)
    summary.assets_total = len(assets)
    for asset in assets:
        key = asset.criticality.value
        summary.assets_by_criticality[key] = summary.assets_by_criticality.get(key, 0) + 1

    risks = [r for r in risk_service.list_risk_records(db) if r.status.value != "closed"]
    summary.risks_open = len(risks)
    for risk in risks:
        summary.risks_by_residual_rating[risk.residual_rating] = (
            summary.risks_by_residual_rating.get(risk.residual_rating, 0) + 1
        )

    today = date.today()
    open_vulns = [
        v for v in vuln_service.list_vulnerabilities(db) if v.remediation_status.value in _OPEN_VULN_STATUSES
    ]
    summary.vulnerabilities_open = len(open_vulns)
    summary.vulnerabilities_overdue = sum(1 for v in open_vulns if v.due_date and v.due_date < today)
    summary.vulnerabilities_known_exploited_open = sum(1 for v in open_vulns if v.known_exploited)

    iam_findings = iam_service.analyze(db)
    summary.iam_findings_total = len(iam_findings)
    summary.iam_findings_critical = sum(1 for f in iam_findings if f.severity in _HIGH_OR_CRITICAL)

    summary.cloud_findings_open = len(cloud_service.list_findings(db, status="open"))
    summary.appsec_findings_open = len(appsec_service.list_appsec_findings(db, status="open"))
    summary.secrets_open = len(appsec_service.list_secret_findings(db))

    incidents = incident_service.list_incidents(db)
    open_incidents = [i for i in incidents if i.stage.value in _OPEN_INCIDENT_STAGES]
    summary.incidents_open = len(open_incidents)
    summary.incidents_open_high_or_critical = sum(
        1 for i in open_incidents if i.severity.value in _HIGH_OR_CRITICAL
    )

    control_gaps = controls_service.analyze_control_gaps(db)
    summary.control_gaps_total = len(control_gaps)
    summary.control_gaps_critical = sum(1 for g in control_gaps if g.severity == "critical")

    for vendor in vendor_service.list_vendors(db):
        latest = vendor_service.latest_assessment(db, vendor.id)
        if latest and latest.rating in ("High", "Critical"):
            summary.vendors_high_or_critical += 1

    summary.data_security_findings = len(data_security_service.analyze_data_security(db))
    summary.continuity_findings = len(continuity_service.analyze_continuity(db))

    ai_gaps = ai_service.analyze_ai_inventory(db)
    summary.ai_governance_gaps = len(ai_gaps)
    summary.ai_governance_gaps_critical = sum(1 for f in ai_gaps if f.severity == "critical")
    summary.rag_findings = len(rag_service.analyze_all_rag_pipelines(db))

    for agent in agent_service.list_agents(db):
        latest = agent_service.latest_assessment(db, agent.id)
        if latest and latest.rating in ("High", "Critical"):
            summary.agents_high_or_critical += 1

    return summary


@dataclass
class ReportHighlight:
    category: str
    title: str
    severity: str
    detail: str


def top_risk_highlights(db: Session, limit: int = 5) -> list[ReportHighlight]:
    rank = {"Critical": 0, "High": 1, "Moderate": 2, "Low": 3}
    open_risks = [r for r in risk_service.list_risk_records(db) if r.status.value != "closed"]
    open_risks.sort(key=lambda r: (rank.get(r.residual_rating, 99), -r.residual_score))
    return [
        ReportHighlight(
            category="Risk Register",
            title=r.title,
            severity=r.residual_rating.lower(),
            detail=f"Residual score {r.residual_score}/25 ({r.residual_rating}) - {r.primary_concern}",
        )
        for r in open_risks[:limit]
    ]


def top_control_gap_highlights(db: Session, limit: int = 5) -> list[ReportHighlight]:
    rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps = sorted(controls_service.analyze_control_gaps(db), key=lambda g: rank.get(g.severity, 99))
    return [
        ReportHighlight(category="Controls", title=g.control_title, severity=g.severity, detail=g.detail)
        for g in gaps[:limit]
    ]


def top_ai_highlights(db: Session, limit: int = 5) -> list[ReportHighlight]:
    rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings = sorted(ai_service.analyze_ai_inventory(db), key=lambda f: rank.get(f.severity, 99))
    return [
        ReportHighlight(
            category="AI Governance", title=f.ai_system_name, severity=f.severity, detail=f.detail
        )
        for f in findings[:limit]
    ]


def recommended_actions(summary: ExecutiveSummary) -> list[str]:
    """Deterministic, threshold-based recommendations - never an LLM
    judgment call. Each rule maps directly to a summary field."""
    actions: list[str] = []

    if summary.risks_by_residual_rating.get("Critical", 0) > 0:
        actions.append(
            f"Prioritize remediation of {summary.risks_by_residual_rating['Critical']} "
            "Critical-residual-risk item(s) in the risk register."
        )
    if summary.vulnerabilities_known_exploited_open > 0:
        actions.append(
            f"{summary.vulnerabilities_known_exploited_open} open vulnerabilit"
            f"{'y is' if summary.vulnerabilities_known_exploited_open == 1 else 'ies are'} "
            "known-exploited - treat as priority regardless of CVSS score alone."
        )
    if summary.vulnerabilities_overdue > 0:
        actions.append(
            f"{summary.vulnerabilities_overdue} vulnerability remediation(s) are past due date."
        )
    if summary.control_gaps_critical > 0:
        actions.append(
            f"{summary.control_gaps_critical} control(s) are assessed Ineffective - review immediately."
        )
    if summary.incidents_open_high_or_critical > 0:
        actions.append(
            f"{summary.incidents_open_high_or_critical} High/Critical incident(s) remain open - "
            "confirm active response."
        )
    if summary.ai_governance_gaps_critical > 0:
        actions.append(
            f"{summary.ai_governance_gaps_critical} Critical AI governance gap(s) - see AI Security for "
            "excessive-agency and unreviewed-decision-influence findings."
        )
    if summary.vendors_high_or_critical > 0:
        actions.append(
            f"{summary.vendors_high_or_critical} vendor(s) assessed High/Critical risk - "
            "review contracts and controls."
        )
    if not actions:
        actions.append("No threshold-triggered actions - overall posture is within acceptable ranges.")

    return actions
