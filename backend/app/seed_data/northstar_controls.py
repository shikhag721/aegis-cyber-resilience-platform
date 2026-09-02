"""Control library and assessments for Northstar Financial Services.
Deliberately includes a mix of Effective, Partially Effective, Ineffective,
and Not Assessed controls, plus one with expired evidence and one overdue
for review - so the gap-analysis endpoint has real variety to demonstrate
on a fresh clone, not just a wall of green.
"""
from datetime import date, timedelta

NORTHSTAR_CONTROLS = [
    {
        "control_id": "CTRL-01",
        "title": "MFA Enforcement for Privileged Accounts",
        "description": "All privileged (admin) accounts require multi-factor authentication.",
        "control_objective": (
            "Prevent unauthorized access to privileged accounts via credential compromise alone."
        ),
        "framework_reference": "NIST CSF 2.0 PR.AA-03; CIS Control 6.5",
        "test_procedure": (
            "Sample privileged accounts in the identity provider and confirm MFA is enrolled and enforced."
        ),
        "owner": "IT Security",
        "review_frequency_days": 90,
    },
    {
        "control_id": "CTRL-02",
        "title": "Least-Privilege IAM Role Scoping",
        "description": "Service and application IAM roles are scoped to only the permissions they require.",
        "control_objective": "Limit blast radius if a service account or workload identity is compromised.",
        "framework_reference": "NIST CSF 2.0 PR.AA-05; CIS Control 6.8",
        "test_procedure": (
            "Review IAM policy documents for a sample of production service roles against actual usage."
        ),
        "owner": "Platform Engineering",
        "review_frequency_days": 180,
    },
    {
        "control_id": "CTRL-03",
        "title": "Vulnerability Remediation SLA",
        "description": "Critical and High vulnerabilities are remediated within defined SLA windows.",
        "control_objective": "Limit the exposure window for known exploitable weaknesses.",
        "framework_reference": "NIST CSF 2.0 ID.RA-01; CIS Control 7.4",
        "test_procedure": (
            "Sample open vulnerabilities and confirm remediation timing against the SLA policy."
        ),
        "owner": "Platform Engineering",
        "review_frequency_days": 90,
    },
    {
        "control_id": "CTRL-04",
        "title": "Security Event Logging on Customer-Facing Systems",
        "description": (
            "All customer-facing applications and APIs log authentication and access events centrally."
        ),
        "control_objective": (
            "Enable detection of anomalous access patterns and support incident investigation."
        ),
        "framework_reference": "NIST CSF 2.0 DE.CM-01; CIS Control 8.2",
        "test_procedure": "Confirm logging configuration and sample recent log output for completeness.",
        "owner": "Platform Engineering",
        "review_frequency_days": 180,
    },
    {
        "control_id": "CTRL-05",
        "title": "Third-Party Vendor Security Review",
        "description": (
            "New vendors with access to Northstar systems or data undergo a security review before "
            "onboarding."
        ),
        "control_objective": (
            "Identify and manage third-party/supply-chain risk before granting access."
        ),
        "framework_reference": "NIST CSF 2.0 GV.SC-06; CIS Control 15.1",
        "test_procedure": (
            "Sample recently onboarded vendors and confirm a completed security review exists."
        ),
        "owner": "Procurement / IT Security",
        "review_frequency_days": 365,
    },
]

# Each entry: control_id, design effectiveness, operating effectiveness,
# notes, evidence (list of dicts or None), days since last reviewed (or None).
NORTHSTAR_CONTROL_ASSESSMENTS = [
    (
        "CTRL-01",
        "effective",
        "effective",
        "MFA enforced for all IT Security and Payments Engineering privileged accounts.",
        [
            {
                "evidence_type": "MFA enrollment export",
                "source": "Okta admin console",
                "days_ago": 20,
                "valid_days": 90,
            }
        ],
        20,
    ),
    (
        "CTRL-02",
        "effective",
        "partially_effective",
        "Policy is well-designed but the last review found one over-broad service role (see IAM Risk).",
        [
            {
                "evidence_type": "IAM policy review",
                "source": "AWS IAM Access Analyzer export",
                "days_ago": 200,
                "valid_days": 180,
            }
        ],
        200,
    ),
    (
        "CTRL-03",
        "effective",
        "ineffective",
        (
            "SLA policy exists and is well-designed, but the Log4Shell-class finding on AST-014 "
            "remained open well past its due date before being risk-accepted rather than remediated."
        ),
        [
            {
                "evidence_type": "Remediation SLA report",
                "source": "Vulnerability management export",
                "days_ago": 10,
                "valid_days": 90,
            }
        ],
        10,
    ),
    (
        "CTRL-04",
        "not_assessed",
        "not_assessed",
        "Scheduled for assessment next quarter.",
        None,
        None,
    ),
    (
        "CTRL-05",
        "effective",
        "effective",
        "Salesforce CRM onboarding review is on file.",
        [
            {
                "evidence_type": "Vendor security review",
                "source": "Procurement records",
                "days_ago": 400,
                "valid_days": 365,
            }
        ],
        400,
    ),
]


def build_evidence_data(entry: dict) -> dict:
    collected_at = date.today() - timedelta(days=entry["days_ago"])
    valid_until = collected_at + timedelta(days=entry["valid_days"])
    status = "valid" if valid_until >= date.today() else "expired"
    return {
        "evidence_type": entry["evidence_type"],
        "source": entry["source"],
        "owner": "",
        "collected_at": collected_at,
        "valid_until": valid_until,
        "status": status,
    }
