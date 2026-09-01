"""Cloud security posture findings - CRUD plus severity-ordered listing."""
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.cloud import CloudFinding, CloudFindingSeverity, CloudFindingStatus

_SEVERITY_RANK = case(
    (CloudFinding.severity == CloudFindingSeverity.CRITICAL, 4),
    (CloudFinding.severity == CloudFindingSeverity.HIGH, 3),
    (CloudFinding.severity == CloudFindingSeverity.MEDIUM, 2),
    (CloudFinding.severity == CloudFindingSeverity.LOW, 1),
    else_=0,
)


def create_finding(db: Session, data: dict) -> CloudFinding:
    finding = CloudFinding(**data)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


def list_findings(db: Session, status: CloudFindingStatus | None = None) -> list[CloudFinding]:
    query = db.query(CloudFinding)
    if status is not None:
        query = query.filter(CloudFinding.status == status)
    return query.order_by(_SEVERITY_RANK.desc()).all()


def get_finding(db: Session, finding_id: int) -> CloudFinding | None:
    return db.get(CloudFinding, finding_id)


def update_finding_status(db: Session, finding: CloudFinding, status: CloudFindingStatus) -> CloudFinding:
    finding.status = status
    db.commit()
    db.refresh(finding)
    return finding
