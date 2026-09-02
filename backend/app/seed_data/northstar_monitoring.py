"""Synthetic security events and a seeded incident for Northstar Financial
Services. The event sequence for 'a.singh' (already flagged in Phase 5 for
missing MFA on a privileged account - see northstar_iam_cloud.py) is the
Section 15 worked example, encoded as data: failed login(s), then a
successful login from an unusual location, then privilege escalation,
then database access - a plausible compromise chain given that account's
already-known weak posture.
"""
from datetime import datetime, timedelta, timezone

BASE_EVENT_TIME = datetime.now(timezone.utc) - timedelta(hours=6)


# Fields: event_type, username, source_ip, source_location, details, offset_minutes
NORTHSTAR_SECURITY_EVENTS = [
    ("failed_login", "a.singh", "203.0.113.44", "Unknown (VPN exit node)", "Incorrect password", 0),
    ("failed_login", "a.singh", "203.0.113.44", "Unknown (VPN exit node)", "Incorrect password", 3),
    (
        "successful_login",
        "a.singh",
        "203.0.113.44",
        "Unknown (VPN exit node)",
        "Login succeeded on 3rd attempt",
        7,
    ),
    (
        "unusual_location",
        "a.singh",
        "203.0.113.44",
        "Unknown (VPN exit node)",
        "Login location inconsistent with employee's usual working location",
        7,
    ),
    (
        "privilege_escalation",
        "a.singh",
        "203.0.113.44",
        "Unknown (VPN exit node)",
        "Session used to access a production database administration console",
        12,
    ),
    (
        "database_access",
        "a.singh",
        "203.0.113.44",
        "Unknown (VPN exit node)",
        "Queried the Customer Database directly outside normal working hours",
        18,
    ),
    # Unrelated, benign event for a different account - should NOT correlate into a finding.
    ("successful_login", "s.nakamura", "198.51.100.7", "Northstar HQ office network", "Routine login", 30),
]

NORTHSTAR_INCIDENT = {
    "title": "Suspected compromised privileged account - a.singh",
    "description": (
        "Correlated security events show a.singh's account (already flagged in IAM Risk for missing "
        "MFA on a privileged account) authenticated after multiple failed attempts from an unrecognized "
        "VPN exit node, then accessed a production database administration console outside normal hours."
    ),
    "severity": "critical",
    "indicators": [
        "failed_login x2 from 203.0.113.44",
        "successful_login from unrecognized location",
        "privilege_escalation to database administration console",
        "database_access outside normal working hours",
    ],
    "recommended_containment": (
        "Disable the account pending investigation, force a password reset, revoke active sessions, "
        "and require MFA enrollment before re-enabling."
    ),
}

# (stage, description, minutes_after_detection) - applied via advance_stage
# to build a realistic timeline beyond the automatic "detection" entry.
NORTHSTAR_INCIDENT_PROGRESS = [
    ("triage", "Triaged as Critical given privileged access and after-hours database activity."),
    (
        "investigation",
        "Confirmed the login originated from a VPN exit node never previously associated with this "
        "account; correlated with the missing-MFA finding already on record for this account.",
    ),
    ("containment", "Account disabled and active sessions revoked pending password reset."),
]
