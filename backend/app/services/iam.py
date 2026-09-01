"""IAM risk detection (Section 11).

Deterministic, explainable findings over IdentityAccount records - each
finding names the specific accounts and explains the business risk in
plain language, not just a rule ID.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.identity import AccountType, EmploymentStatus, IdentityAccount

INACTIVE_THRESHOLD_DAYS = 90

# Segregation-of-duties conflicts: pairs of permissions that should never
# both be held by one account (classic SoD example: the same person/service
# should not be able to both initiate AND approve a payment).
TOXIC_PERMISSION_PAIRS = [
    ({"initiate_payment", "approve_payment"}, "can both initiate and approve payments"),
    ({"create_vendor", "approve_vendor_payment"}, "can both create a vendor and approve payment to it"),
]

PRODUCTION_ELIGIBLE_DEPARTMENTS = {
    "Platform Engineering",
    "Core Banking Team",
    "Data Platform Team",
    "Payments Engineering",
    "IT Security",
    "Network Engineering",
}


@dataclass
class IAMFinding:
    account_username: str
    finding_type: str
    severity: str
    detail: str


def _as_aware_utc(dt: datetime | None) -> datetime | None:
    """SQLite drops timezone info on round-trip even for DateTime(timezone=True)
    columns (it always returns naive datetimes), while Postgres preserves it -
    normalize here so `analyze()` never crashes comparing naive vs. aware
    datetimes regardless of which database is in use.
    """
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def create_identity_account(db: Session, data: dict) -> IdentityAccount:
    account = IdentityAccount(**data)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def list_identity_accounts(db: Session) -> list[IdentityAccount]:
    return db.query(IdentityAccount).order_by(IdentityAccount.username).all()


def get_identity_account(db: Session, account_id: int) -> IdentityAccount | None:
    return db.get(IdentityAccount, account_id)


def analyze(db: Session) -> list[IAMFinding]:
    findings: list[IAMFinding] = []
    now = datetime.now(timezone.utc)

    for account in list_identity_accounts(db):
        if account.employment_status == EmploymentStatus.TERMINATED and account.is_enabled:
            findings.append(
                IAMFinding(
                    account_username=account.username,
                    finding_type="orphan_account",
                    severity="high",
                    detail=(
                        f"'{account.username}' ({account.display_name}) is marked terminated but the "
                        "account is still enabled - a departed employee retains system access."
                    ),
                )
            )

        if account.is_privileged and not account.mfa_enabled:
            findings.append(
                IAMFinding(
                    account_username=account.username,
                    finding_type="missing_mfa",
                    severity="critical",
                    detail=(
                        f"'{account.username}' holds privileged access but does not have MFA enabled - "
                        "a single compromised password would be sufficient for privileged access."
                    ),
                )
            )

        last_login = _as_aware_utc(account.last_login_at)
        if (
            account.account_type == AccountType.HUMAN
            and account.employment_status == EmploymentStatus.ACTIVE
            and account.is_enabled
            and (last_login is None or last_login < now - timedelta(days=INACTIVE_THRESHOLD_DAYS))
        ):
            findings.append(
                IAMFinding(
                    account_username=account.username,
                    finding_type="inactive_account",
                    severity="medium",
                    detail=(
                        f"'{account.username}' has not logged in within {INACTIVE_THRESHOLD_DAYS} days "
                        "but remains active and enabled - an unused account is unnecessary attack surface."
                    ),
                )
            )

        if (
            account.production_access
            and account.department not in PRODUCTION_ELIGIBLE_DEPARTMENTS
            and not account.is_privileged
        ):
            findings.append(
                IAMFinding(
                    account_username=account.username,
                    finding_type="inappropriate_production_access",
                    severity="high",
                    detail=(
                        f"'{account.username}' in '{account.department}' has production access, which "
                        "is not a typical requirement for that department - access should be reviewed "
                        "against actual job function."
                    ),
                )
            )

        if (
            account.account_type == AccountType.SERVICE
            and account.is_privileged
            and account.production_access
            and not account.mfa_enabled
        ):
            findings.append(
                IAMFinding(
                    account_username=account.username,
                    finding_type="privilege_escalation_path",
                    severity="critical",
                    detail=(
                        f"'{account.username}' is a privileged service account with production access "
                        "and no MFA - if its credentials are exposed (e.g. in a config file or log), an "
                        "attacker gains privileged production access with no second factor to stop them."
                    ),
                )
            )

        permission_set = set(account.permissions or [])
        for toxic_pair, description in TOXIC_PERMISSION_PAIRS:
            if toxic_pair.issubset(permission_set):
                findings.append(
                    IAMFinding(
                        account_username=account.username,
                        finding_type="conflicting_privileges",
                        severity="high",
                        detail=f"'{account.username}' {description} - a segregation-of-duties conflict.",
                    )
                )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_rank.get(f.severity, 4))
    return findings
