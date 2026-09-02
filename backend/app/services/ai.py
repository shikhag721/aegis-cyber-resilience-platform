"""AI inventory management and deterministic AI-inventory gap detection
(Section 25). Judgment-based findings (e.g. "this specific integration is
vulnerable to prompt injection") are recorded as AISecurityFinding rows,
the same CRUD pattern as AppSecFinding/CloudFinding - they require an
assessor's judgment, not a mechanical rule. The composite conditions below
ARE mechanically detectable from inventory fields alone, the same way
IAM Risk's findings are - so they are computed, not stored, following the
same pattern as app/services/iam.py::analyze.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload

from app.models.ai import AISecurityFinding, AISystem


def create_ai_system(db: Session, data: dict) -> AISystem:
    ai_system = AISystem(**data)
    db.add(ai_system)
    db.commit()
    db.refresh(ai_system)
    return ai_system


def list_ai_systems(db: Session) -> list[AISystem]:
    return db.query(AISystem).options(joinedload(AISystem.findings)).order_by(AISystem.name).all()


def get_ai_system(db: Session, ai_system_id: int) -> AISystem | None:
    return (
        db.query(AISystem)
        .options(joinedload(AISystem.findings))
        .filter(AISystem.id == ai_system_id)
        .first()
    )


def create_finding(db: Session, ai_system_id: int, data: dict) -> AISecurityFinding:
    finding = AISecurityFinding(ai_system_id=ai_system_id, **data)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


def list_all_findings(db: Session) -> list[AISecurityFinding]:
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings = db.query(AISecurityFinding).options(joinedload(AISecurityFinding.ai_system)).all()
    return sorted(findings, key=lambda f: severity_rank.get(f.severity, 4))


@dataclass
class AIInventoryFinding:
    ai_system_name: str
    finding_type: str
    severity: str
    detail: str


def analyze_ai_inventory(db: Session) -> list[AIInventoryFinding]:
    findings: list[AIInventoryFinding] = []

    for system in list_ai_systems(db):
        if system.tools_available and not system.human_oversight:
            findings.append(
                AIInventoryFinding(
                    ai_system_name=system.name,
                    finding_type="excessive_agency_risk",
                    severity="critical",
                    detail=(
                        f"'{system.name}' has tool access ({', '.join(system.tools_available)}) with "
                        "no documented human oversight - a malfunction or manipulation could take "
                        "action, not just produce bad text."
                    ),
                )
            )

        if system.influences_decisions and not system.human_oversight:
            findings.append(
                AIInventoryFinding(
                    ai_system_name=system.name,
                    finding_type="unreviewed_decision_influence",
                    severity="critical",
                    detail=(
                        f"'{system.name}' influences decisions about people with no documented human "
                        "review before that influence takes effect."
                    ),
                )
            )

        if not system.monitoring_enabled:
            findings.append(
                AIInventoryFinding(
                    ai_system_name=system.name,
                    finding_type="no_monitoring",
                    severity="medium",
                    detail=f"'{system.name}' has no monitoring enabled for its usage or output.",
                )
            )

        if "third-party" in system.model_provider.lower() or "external" in system.model_provider.lower():
            if system.regulatory_risk_tier.value == "high" and not system.human_oversight:
                findings.append(
                    AIInventoryFinding(
                        ai_system_name=system.name,
                        finding_type="high_tier_third_party_no_oversight",
                        severity="high",
                        detail=(
                            f"'{system.name}' resembles an EU AI Act high-risk category and relies on a "
                            "third-party model provider, with no documented human oversight."
                        ),
                    )
                )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_rank.get(f.severity, 4))
    return findings
