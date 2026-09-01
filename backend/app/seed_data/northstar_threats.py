"""Synthetic threat model for Northstar Financial Services.

Every `why_relevant` field ties the (real) MITRE ATT&CK technique to a
specific Northstar asset or control gap, per the project brief's explicit
requirement to explain relevance rather than just list technique IDs.
"""

NORTHSTAR_THREAT_ACTORS = [
    {
        "name": "Organized Cybercrime Group",
        "category": "external_cybercriminal",
        "motivation": "Direct financial theft via fraudulent payment transactions and resale of customer PII",
        "sophistication": "High",
        "description": (
            "Financially motivated external actors targeting retail banking customers and payment "
            "infrastructure. Typically use commodity malware, phishing kits, and credential-stuffing "
            "toolchains rather than custom exploits."
        ),
    },
    {
        "name": "Malicious Insider",
        "category": "insider_malicious",
        "motivation": "Financial gain, retaliation, or coercion",
        "sophistication": "Medium",
        "description": (
            "An employee or contractor with legitimate access who intentionally misuses that access, "
            "e.g. a Core Banking Team member with standing production access."
        ),
    },
    {
        "name": "Compromised Third-Party Vendor",
        "category": "third_party",
        "motivation": "N/A - vector, not motivated actor",
        "sophistication": "Variable",
        "description": (
            "A vendor with legitimate integration access (e.g. Salesforce CRM) is itself compromised, "
            "and that trusted access is used to reach Northstar systems or data."
        ),
    },
]

# Tuple fields: threat_name, description, mitre_technique_id,
# mitre_technique_name, why_relevant, threat_actor_name_or_None
NORTHSTAR_THREATS = [
    (
        "Credential stuffing against customer login",
        "Automated login attempts using breached username/password lists from unrelated prior breaches.",
        "T1110.004",
        "Brute Force: Credential Stuffing",
        (
            "The Customer Web Portal (AST-001) authenticates directly against the customer identity "
            "store with no documented rate-limiting or anomaly-based lockout, and retail banking "
            "customers have historically high password-reuse rates - this is the most common real-world "
            "initial-access path into online banking platforms, not a theoretical concern."
        ),
        "Organized Cybercrime Group",
    ),
    (
        "Valid account abuse via over-privileged service account",
        "Use of a legitimate but overly permissive service account to access systems beyond its "
        "intended scope.",
        "T1078.004",
        "Valid Accounts: Cloud Accounts",
        (
            "The Payment Processing Service (AST-003) and Container Platform (AST-015) both use "
            "IAM-role-based authentication; if a workload's IAM role is broader than that workload "
            "needs (not yet verified - see Phase 5 IAM Risk), a compromised container gains lateral "
            "reach across the payment path rather than being contained to its own function."
        ),
        None,
    ),
    (
        "Public API Gateway rate-limit bypass leading to data scraping",
        "Automated enumeration/scraping of an API endpoint that lacks effective rate limiting.",
        "T1213",
        "Data from Information Repositories",
        (
            "The Public API Gateway (AST-002) is the single entry point for all customer-facing API "
            "traffic; if per-client rate limiting is not enforced at the gateway (to be verified in "
            "Phase 6, Application/API Security), an attacker can enumerate account or transaction data "
            "at scale rather than one record at a time."
        ),
        "Organized Cybercrime Group",
    ),
    (
        "Insider exfiltration of customer records",
        "An employee with standing database access exports customer records for unauthorized use.",
        "T1005",
        "Data from Local System",
        (
            "The Customer Database (AST-004) is accessed by multiple internal teams; without "
            "query-level audit logging and anomaly detection on bulk exports (status: logging_enabled=true "
            "but export-volume alerting not yet confirmed), a single legitimate credential can quietly "
            "exfiltrate the full customer PII dataset."
        ),
        "Malicious Insider",
    ),
    (
        "Compromised SaaS vendor session used to pivot",
        "A trusted third-party SaaS integration is compromised and its session/API access is reused.",
        "T1199",
        "Trusted Relationship",
        (
            "Salesforce CRM (AST-008) holds commercial banking client data and has an authenticated "
            "integration back into Northstar systems; a compromise at the vendor (outside Northstar's "
            "direct control - see Phase 9 Vendor Risk) would arrive as 'trusted' traffic that internal "
            "monitoring is less likely to flag."
        ),
        "Compromised Third-Party Vendor",
    ),
    (
        "Prompt injection against the AI customer support assistant",
        "Crafted customer input manipulates the AI assistant into taking or suggesting unintended actions.",
        "T1566",
        "Phishing (adapted: malicious input as the delivery mechanism)",
        (
            "The AI Customer Support Assistant (AST-009) reads customer chat input directly into its "
            "context window; without input/output filtering (see Phase 10 AI Security), a crafted "
            "message could manipulate its drafted response or attempted actions rather than exploiting "
            "a traditional software vulnerability."
        ),
        None,
    ),
]

# Attack paths reference asset tags and threat names, resolved to IDs at seed time.
NORTHSTAR_ATTACK_PATHS = [
    {
        "name": "Compromised customer credential to payment data exfiltration",
        "description": (
            "The canonical path from the project brief (Section 8): a stolen customer credential is "
            "used to reach authenticated APIs, abuse legitimate access, and reach payment/customer data."
        ),
        "entry_point": "Internet",
        "target_asset_tag": "AST-004",
        "likelihood": 3,
        "impact": 5,
        "notes": (
            "Highest-impact path in the current model: reaches restricted customer PII and payment data."
        ),
        "steps": [
            {
                "sequence": 1,
                "description": "Attacker obtains a valid customer credential via credential stuffing",
                "asset_tag": "AST-001",
                "threat_name": "Credential stuffing against customer login",
            },
            {
                "sequence": 2,
                "description": "Authenticated session reaches the Public API Gateway",
                "asset_tag": "AST-002",
                "threat_name": None,
            },
            {
                "sequence": 3,
                "description": "Gateway forwards authenticated request to the Payment Processing Service",
                "asset_tag": "AST-003",
                "threat_name": "Valid account abuse via over-privileged service account",
            },
            {
                "sequence": 4,
                "description": "Payment service query reaches the Customer Database; data exfiltrated",
                "asset_tag": "AST-004",
                "threat_name": None,
            },
        ],
    },
    {
        "name": "Malicious insider bulk export of customer records",
        "description": "A Core Banking Team member with standing database access exports records directly.",
        "entry_point": "Internal network (authenticated employee)",
        "target_asset_tag": "AST-004",
        "likelihood": 2,
        "impact": 5,
        "notes": (
            "Lower likelihood than external paths, but comparable impact - insider risk should "
            "not be deprioritized purely on likelihood."
        ),
        "steps": [
            {
                "sequence": 1,
                "description": (
                    "Employee with standing production access queries the Customer Database directly"
                ),
                "asset_tag": "AST-004",
                "threat_name": "Insider exfiltration of customer records",
            },
            {
                "sequence": 2,
                "description": (
                    "Bulk export is not flagged by volume-based alerting (not yet confirmed to exist)"
                ),
                "asset_tag": "AST-004",
                "threat_name": None,
            },
        ],
    },
    {
        "name": "Compromised vendor session reaches commercial client data",
        "description": "Salesforce CRM compromise is used to pivot into Northstar's integrated systems.",
        "entry_point": "Trusted third-party integration",
        "target_asset_tag": "AST-008",
        "likelihood": 2,
        "impact": 4,
        "notes": "Depends on Salesforce's own security posture - outside Northstar's direct control.",
        "steps": [
            {
                "sequence": 1,
                "description": "Vendor-side compromise of a Salesforce integration account",
                "asset_tag": "AST-008",
                "threat_name": "Compromised SaaS vendor session used to pivot",
            },
            {
                "sequence": 2,
                "description": "Trusted integration traffic used to access commercial client records",
                "asset_tag": "AST-008",
                "threat_name": None,
            },
        ],
    },
]
