"""Business Continuity & Disaster Recovery (Section 22)."""
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models.continuity import ContinuityPlan

BACKUP_TEST_STALE_DAYS = 180
DR_TEST_STALE_DAYS = 365


def create_plan(db: Session, data: dict) -> ContinuityPlan:
    plan = ContinuityPlan(**data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db: Session) -> list[ContinuityPlan]:
    return db.query(ContinuityPlan).options(joinedload(ContinuityPlan.asset)).all()


def get_plan_for_asset(db: Session, asset_id: int) -> ContinuityPlan | None:
    return db.query(ContinuityPlan).filter(ContinuityPlan.asset_id == asset_id).first()


@dataclass
class ContinuityFinding:
    asset_name: str
    finding_type: str
    severity: str
    detail: str


def analyze_continuity(db: Session) -> list[ContinuityFinding]:
    findings: list[ContinuityFinding] = []
    today = date.today()

    for plan in list_plans(db):
        asset_name = plan.asset.name if plan.asset else f"Asset #{plan.asset_id}"
        asset_criticality = plan.asset.criticality.value if plan.asset else "unknown"

        if plan.rto_hours is None or plan.rpo_hours is None:
            findings.append(
                ContinuityFinding(
                    asset_name=asset_name,
                    finding_type="missing_rto_rpo",
                    severity="high" if asset_criticality in ("high", "critical") else "medium",
                    detail=f"'{asset_name}' has no defined RTO/RPO.",
                )
            )

        if plan.last_backup_tested_at is None or (
            today - plan.last_backup_tested_at > timedelta(days=BACKUP_TEST_STALE_DAYS)
        ):
            findings.append(
                ContinuityFinding(
                    asset_name=asset_name,
                    finding_type="stale_backup_test",
                    severity="high" if asset_criticality in ("high", "critical") else "medium",
                    detail=(
                        f"'{asset_name}' backup restoration has not been tested within the last "
                        f"{BACKUP_TEST_STALE_DAYS} days (or ever)."
                    ),
                )
            )

        if plan.last_dr_test_at is None or (
            today - plan.last_dr_test_at > timedelta(days=DR_TEST_STALE_DAYS)
        ):
            findings.append(
                ContinuityFinding(
                    asset_name=asset_name,
                    finding_type="stale_dr_test",
                    severity="critical" if asset_criticality == "critical" else "medium",
                    detail=(
                        f"'{asset_name}' has not had a full disaster-recovery test within the last "
                        f"{DR_TEST_STALE_DAYS} days (or ever)."
                    ),
                )
            )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_rank.get(f.severity, 4))
    return findings
