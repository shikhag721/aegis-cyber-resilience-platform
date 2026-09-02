"""Security event correlation (Section 15).

The point of this module is the CORRELATION, not the storage: a single
failed login or a single database access event is noise. A specific
*sequence* of events for the same account within a time window is a
signal worth an analyst's attention - this mirrors real detection-
engineering practice (why a SIEM correlation rule exists at all) at a
scale appropriate for a portfolio project.
"""
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.monitoring import SecurityEvent, SecurityEventType

CORRELATION_WINDOW = timedelta(hours=24)

# The specific event-type sequence that, together, indicates a plausible
# account-compromise chain (Section 15's own example, encoded as data):
# failed_login -> successful_login -> unusual_location/privilege_escalation
# -> database_access/unusual_data_transfer.
SUSPICIOUS_FOLLOW_ONS = {SecurityEventType.UNUSUAL_LOCATION, SecurityEventType.PRIVILEGE_ESCALATION}
SUSPICIOUS_DATA_ACTIONS = {SecurityEventType.DATABASE_ACCESS, SecurityEventType.UNUSUAL_DATA_TRANSFER}


@dataclass
class CorrelationFinding:
    username: str
    severity: str
    matched_event_types: list[str]
    narrative: str


def create_event(db: Session, data: dict) -> SecurityEvent:
    event = SecurityEvent(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, username: str | None = None) -> list[SecurityEvent]:
    query = db.query(SecurityEvent)
    if username is not None:
        query = query.filter(SecurityEvent.username == username)
    return query.order_by(SecurityEvent.occurred_at).all()


def _events_by_account(db: Session) -> dict[str, list[SecurityEvent]]:
    grouped: dict[str, list[SecurityEvent]] = {}
    for event in list_events(db):
        grouped.setdefault(event.username, []).append(event)
    return grouped


def correlate(db: Session) -> list[CorrelationFinding]:
    findings: list[CorrelationFinding] = []

    for username, events in _events_by_account(db).items():
        events = sorted(events, key=lambda e: e.occurred_at)
        types_present = [e.event_type for e in events]

        has_failed_then_success = _has_ordered_pair(
            events, SecurityEventType.FAILED_LOGIN, SecurityEventType.SUCCESSFUL_LOGIN
        )
        has_suspicious_follow_on = any(t in SUSPICIOUS_FOLLOW_ONS for t in types_present)
        has_data_action = any(t in SUSPICIOUS_DATA_ACTIONS for t in types_present)

        if has_failed_then_success and has_suspicious_follow_on and has_data_action:
            findings.append(
                CorrelationFinding(
                    username=username,
                    severity="critical",
                    matched_event_types=[t.value for t in types_present],
                    narrative=(
                        f"'{username}': failed login attempt(s) followed by a successful login, then "
                        "a suspicious follow-on (unusual location or privilege escalation), then access "
                        "to sensitive data - a plausible account-compromise chain, not an isolated event."
                    ),
                )
            )
        elif has_failed_then_success and has_suspicious_follow_on:
            findings.append(
                CorrelationFinding(
                    username=username,
                    severity="high",
                    matched_event_types=[t.value for t in types_present],
                    narrative=(
                        f"'{username}': failed login attempt(s) followed by a successful login from an "
                        "unusual context - worth investigation even without confirmed data access yet."
                    ),
                )
            )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_rank.get(f.severity, 4))
    return findings


def _has_ordered_pair(
    events: list[SecurityEvent], first_type: SecurityEventType, second_type: SecurityEventType
) -> bool:
    """True if `first_type` is followed (not necessarily immediately) by
    `second_type` within CORRELATION_WINDOW, in chronological order.
    """
    first_seen_at = None
    for event in events:
        if event.event_type == first_type and first_seen_at is None:
            first_seen_at = event.occurred_at
        elif (
            event.event_type == second_type
            and first_seen_at is not None
            and event.occurred_at - first_seen_at <= CORRELATION_WINDOW
        ):
            return True
    return False
