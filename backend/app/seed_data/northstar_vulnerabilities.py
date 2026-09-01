"""Synthetic vulnerability findings for Northstar Financial Services.

CVE identifiers referenced are real, publicly known vulnerabilities (used
here purely as realistic examples of vulnerability class/severity) applied
to fictional Northstar assets - no claim is made about Northstar's actual
(fictional) software versions matching these CVEs precisely.

CVE-2021-44228 (Log4Shell) on the isolated legacy test server (AST-014) is
the deliberate, canonical CVSS-vs-business-risk pairing: CVSS 10.0,
known-exploited, on a low-criticality, non-internet-facing, decommission-
scheduled asset - the same pairing already used for the Risk Register
example, now traced through the full Vulnerability -> assess -> RiskRecord
workflow.
"""

# Fields: cve_id, title, description, asset_tag, cvss_score,
# known_exploited, compensating_controls, assess (bool - whether to run
# the risk assessment at seed time)
NORTHSTAR_VULNERABILITIES = [
    {
        "cve_id": "CVE-2021-44228",
        "title": "Remote code execution in logging library (Log4Shell-class)",
        "description": (
            "Unauthenticated remote code execution via crafted log input in a bundled logging "
            "dependency."
        ),
        "asset_tag": "AST-014",
        "cvss_score": 10.0,
        "known_exploited": True,
        "compensating_controls": "Isolated network segment; scheduled for decommission within 90 days.",
        "assess": True,
    },
    {
        "cve_id": "CVE-2024-3094",
        "title": "Supply-chain backdoor in compression library (xz-class)",
        "description": "A backdoored compression library dependency could allow SSH authentication bypass.",
        "asset_tag": "AST-015",
        "cvss_score": 10.0,
        "known_exploited": True,
        "compensating_controls": "",
        "assess": True,
    },
    {
        "cve_id": "CVE-2023-4863",
        "title": "Heap buffer overflow in image processing library",
        "description": "Maliciously crafted image content could trigger a heap overflow in image handling.",
        "asset_tag": "AST-001",
        "cvss_score": 8.8,
        "known_exploited": True,
        "compensating_controls": "WAF rule deployed to block known exploit patterns.",
        "assess": True,
    },
    {
        "cve_id": None,
        "title": "Outdated TLS cipher suite support on edge load balancer",
        "description": "Load balancer still accepts several deprecated TLS 1.1 cipher suites.",
        "asset_tag": "AST-013",
        "cvss_score": 5.3,
        "known_exploited": False,
        "compensating_controls": "",
        "assess": False,
    },
    {
        "cve_id": None,
        "title": "Missing OS security patch (local privilege escalation)",
        "description": "Core banking server is two patch cycles behind on OS security updates.",
        "asset_tag": "AST-012",
        "cvss_score": 7.8,
        "known_exploited": False,
        "compensating_controls": "Restricted administrative access; MFA required for privileged sessions.",
        "assess": False,
    },
]
