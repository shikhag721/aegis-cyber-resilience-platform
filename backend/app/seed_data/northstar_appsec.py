"""Synthetic application/API security findings for Northstar Financial
Services, plus one secrets-scan example run through the real scanner at
seed time (not a hand-written record) so the detection pipeline itself is
exercised on startup, not just described.
"""

NORTHSTAR_APPSEC_FINDINGS = [
    {
        "resource_name": "POST /api/v1/accounts/{id}/transfer",
        "asset_tag": "AST-002",
        "finding_type": "broken_authorization",
        "severity": "critical",
        "description": (
            "The transfer endpoint checks that the caller is authenticated but does not verify the "
            "caller owns the source account - Broken Object Level Authorization."
        ),
        "owasp_reference": "OWASP API Security Top 10 - API1:2023 Broken Object Level Authorization",
        "recommendation": (
            "Verify the authenticated user owns (or is authorized for) the source account on every "
            "request."
        ),
    },
    {
        "resource_name": "GET /api/v1/search",
        "asset_tag": "AST-002",
        "finding_type": "injection",
        "severity": "high",
        "description": "The search query parameter is concatenated directly into a backend query string.",
        "owasp_reference": "OWASP Top 10 - A03:2021 Injection",
        "recommendation": (
            "Use parameterized queries / an ORM query builder; never concatenate user input into a query."
        ),
    },
    {
        "resource_name": "POST /api/v1/auth/login",
        "asset_tag": "AST-001",
        "finding_type": "missing_rate_limiting",
        "severity": "high",
        "description": (
            "No rate limiting is enforced on login attempts, enabling credential-stuffing at scale."
        ),
        "owasp_reference": "OWASP API Security Top 10 - API4:2023 Unrestricted Resource Consumption",
        "recommendation": (
            "Add per-account and per-IP rate limiting with exponential backoff on repeated failures."
        ),
    },
    {
        "resource_name": "GET /api/v1/support/tickets/{id}",
        "asset_tag": "AST-009",
        "finding_type": "sensitive_data_exposure",
        "severity": "medium",
        "description": (
            "Support ticket responses include the customer's full account number, not a masked version."
        ),
        "owasp_reference": "OWASP Top 10 - A02:2021 Cryptographic Failures (sensitive data exposure)",
        "recommendation": "Mask all but the last 4 digits of account numbers in any API response.",
    },
    {
        "resource_name": "Session cookie configuration",
        "asset_tag": "AST-001",
        "finding_type": "session_security",
        "severity": "medium",
        "description": "Session cookies are not marked with the Secure or SameSite attributes.",
        "owasp_reference": "OWASP Top 10 - A05:2021 Security Misconfiguration",
        "recommendation": "Set Secure, HttpOnly, and SameSite=Strict on all session cookies.",
    },
]

# Text run through the real scanner (app/services/secrets_scanner.py) at
# seed time - deliberately fake/synthetic values only. Values are shaped to
# avoid closely resembling any real provider's actual token format (beyond
# AWS's own well-known public documentation-example key) since GitHub's own
# push protection flags realistic-looking tokens even inside test/seed data.
SAMPLE_LEAKED_CONFIG_TEXT = """
# legacy deployment config - found in an internal wiki page export
DATABASE_URL = "postgres://svc_user:REDACTED@db.internal:5432/northstar"
aws_access_key = "AKIAIOSFODNN7EXAMPLE"
SLACK_WEBHOOK_TOKEN = "xoxb-NOT-A-REAL-TOKEN-PLACEHOLDER-VALUE"
api_key = "example-placeholder-value-not-real-1234567890"
""".strip()

SAMPLE_LEAKED_CONFIG_LOCATION = "internal wiki export: 'Legacy Deployment Notes'"
SAMPLE_LEAKED_CONFIG_EXPOSURE = "Internal wiki page (still indexed, not access-restricted)"
