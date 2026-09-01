"""Synthetic Risk Register entries for Northstar Financial Services.

Includes AST-014 (the deliberately low-value legacy test server) scored
against a Critical-severity, known-exploited finding specifically to
demonstrate the CVSS-vs-business-risk principle (Section 9) live in the
seeded data, not just in a unit test.
"""

# Fields: title, description, asset_tag, threat_severity, known_exploited,
# control_effectiveness, threat_name (or None), treatment (or None)
NORTHSTAR_RISKS = [
    {
        "title": "Credential stuffing exposure on Customer Web Portal",
        "description": (
            "No documented rate-limiting or anomaly-based account lockout on customer login attempts."
        ),
        "asset_tag": "AST-001",
        "threat_severity": "high",
        "known_exploited": False,
        "control_effectiveness": 0.2,
        "threat_name": "Credential stuffing against customer login",
        "treatment": None,
    },
    {
        "title": "Over-privileged service account on Payment Processing Service",
        "description": (
            "IAM role scope for the payment service workload has not been reviewed against least privilege."
        ),
        "asset_tag": "AST-003",
        "threat_severity": "medium",
        "known_exploited": False,
        "control_effectiveness": 0.3,
        "threat_name": "Valid account abuse via over-privileged service account",
        "treatment": None,
    },
    {
        "title": "Bulk export monitoring gap on Customer Database",
        "description": "No volume-based alerting confirmed for large data exports by authorized users.",
        "asset_tag": "AST-004",
        "threat_severity": "high",
        "known_exploited": False,
        "control_effectiveness": 0.1,
        "threat_name": "Insider exfiltration of customer records",
        "treatment": {
            "treatment_decision": "mitigate",
            "treatment_reason": "Data Platform Team implementing export-volume alerting next quarter.",
            "owner": "Data Platform Team",
            "status": "treatment_in_progress",
        },
    },
    {
        "title": "Known-exploited OS vulnerability on legacy QA test server",
        "description": (
            "Ubuntu 18.04 (end of life) with a Critical-severity, known-exploited kernel vulnerability. "
            "Illustrates that technical severity alone is not business risk - see notes."
        ),
        "asset_tag": "AST-014",
        "threat_severity": "critical",
        "known_exploited": True,
        "control_effectiveness": 0.5,
        "threat_name": None,
        "treatment": {
            "treatment_decision": "accept",
            "treatment_reason": (
                "Isolated network segment, synthetic data only, scheduled for decommission within 90 days - "
                "residual risk accepted rather than investing in patching a system being retired."
            ),
            "owner": "QA Team",
            "status": "closed",
        },
    },
    {
        "title": "Missing access logging on customer document storage",
        "description": "S3 bucket access logging not enabled for the KYC document store.",
        "asset_tag": "AST-006",
        "threat_severity": "medium",
        "known_exploited": False,
        "control_effectiveness": 0.1,
        "threat_name": None,
        "treatment": None,
    },
]
