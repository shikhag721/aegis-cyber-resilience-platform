"""Application/API security and secrets finding management."""
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.appsec import AppSecFinding, FindingSeverity, FindingStatus, SecretFinding
from app.services.secrets_scanner import SecretMatch, scan_text

_SEVERITY_RANK = case(
    (AppSecFinding.severity == FindingSeverity.CRITICAL, 4),
    (AppSecFinding.severity == FindingSeverity.HIGH, 3),
    (AppSecFinding.severity == FindingSeverity.MEDIUM, 2),
    (AppSecFinding.severity == FindingSeverity.LOW, 1),
    else_=0,
)

_SECRET_SEVERITY_RANK = case(
    (SecretFinding.severity == FindingSeverity.CRITICAL, 4),
    (SecretFinding.severity == FindingSeverity.HIGH, 3),
    (SecretFinding.severity == FindingSeverity.MEDIUM, 2),
    (SecretFinding.severity == FindingSeverity.LOW, 1),
    else_=0,
)


def create_appsec_finding(db: Session, data: dict) -> AppSecFinding:
    finding = AppSecFinding(**data)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


def list_appsec_findings(db: Session, status: FindingStatus | None = None) -> list[AppSecFinding]:
    query = db.query(AppSecFinding)
    if status is not None:
        query = query.filter(AppSecFinding.status == status)
    return query.order_by(_SEVERITY_RANK.desc()).all()


def get_appsec_finding(db: Session, finding_id: int) -> AppSecFinding | None:
    return db.get(AppSecFinding, finding_id)


def update_appsec_status(db: Session, finding: AppSecFinding, status: FindingStatus) -> AppSecFinding:
    finding.status = status
    db.commit()
    db.refresh(finding)
    return finding


def create_secret_finding(db: Session, data: dict) -> SecretFinding:
    finding = SecretFinding(**data)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


def list_secret_findings(db: Session) -> list[SecretFinding]:
    return db.query(SecretFinding).order_by(_SECRET_SEVERITY_RANK.desc()).all()


def scan_and_record(db: Session, text: str, location: str, exposure: str) -> list[SecretFinding]:
    """Runs the detector over `text` and persists a SecretFinding for each
    match - this is the bridge between the stateless scanner
    (app/services/secrets_scanner.py) and the tracked findings register.
    """
    matches: list[SecretMatch] = scan_text(text)
    created = []
    for match in matches:
        finding = create_secret_finding(
            db,
            dict(
                secret_type=match.secret_type,
                location=f"{location} (line {match.line_number})",
                severity=match.severity,
                exposure=exposure,
                redacted_snippet=match.redacted_snippet,
                rotation_recommendation=_rotation_recommendation(match.secret_type),
            ),
        )
        created.append(finding)
    return created


def _rotation_recommendation(secret_type) -> str:
    return {
        "aws_access_key": "Rotate the AWS access key immediately via IAM and invalidate the old key.",
        "slack_token": "Revoke the Slack token in the Slack app admin console and issue a new one.",
        "private_key": "Revoke and reissue the private key/certificate; investigate what it authenticated.",
        "generic_api_key": "Rotate the API key with the issuing provider and update all consumers.",
        "password_assignment": "Rotate the password and move it to a secrets manager, not source code.",
    }.get(str(secret_type), "Rotate the credential and move it to a secrets manager.")
