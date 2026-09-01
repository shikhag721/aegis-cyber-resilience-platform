"""Synthetic IAM accounts and cloud findings for Northstar Financial
Services, deliberately including one example of each IAM finding type
(Section 11) so the detection engine has something real to surface.
"""
from datetime import datetime, timedelta, timezone

_NOW = datetime.now(timezone.utc)

NORTHSTAR_IDENTITY_ACCOUNTS = [
    {
        "username": "j.martinez",
        "display_name": "Jamie Martinez",
        "account_type": "human",
        "department": "Platform Engineering",
        "employment_status": "active",
        "is_enabled": True,
        "is_privileged": True,
        "mfa_enabled": True,
        "production_access": True,
        "permissions": ["deploy_production"],
        "last_login_at": _NOW - timedelta(days=1),
    },
    {
        # Orphan account: terminated employee, account never disabled.
        "username": "r.chen",
        "display_name": "Riley Chen (former employee)",
        "account_type": "human",
        "department": "Payments Engineering",
        "employment_status": "terminated",
        "is_enabled": True,
        "is_privileged": True,
        "mfa_enabled": True,
        "production_access": True,
        "permissions": [],
        "last_login_at": _NOW - timedelta(days=45),
    },
    {
        # Missing MFA on a privileged account.
        "username": "a.singh",
        "display_name": "Amara Singh",
        "account_type": "human",
        "department": "Core Banking Team",
        "employment_status": "active",
        "is_enabled": True,
        "is_privileged": True,
        "mfa_enabled": False,
        "production_access": True,
        "permissions": [],
        "last_login_at": _NOW - timedelta(days=2),
    },
    {
        # Inactive account: active/enabled but no login in a long time.
        "username": "t.oconnor",
        "display_name": "Taylor O'Connor",
        "account_type": "human",
        "department": "Human Resources",
        "employment_status": "active",
        "is_enabled": True,
        "is_privileged": False,
        "mfa_enabled": True,
        "production_access": False,
        "permissions": [],
        "last_login_at": _NOW - timedelta(days=210),
    },
    {
        # Inappropriate production access for a non-technical department.
        "username": "m.patel",
        "display_name": "Meera Patel",
        "account_type": "human",
        "department": "Marketing",
        "employment_status": "active",
        "is_enabled": True,
        "is_privileged": False,
        "mfa_enabled": True,
        "production_access": True,
        "permissions": [],
        "last_login_at": _NOW - timedelta(days=3),
    },
    {
        # Segregation-of-duties conflict.
        "username": "d.oyelaran",
        "display_name": "Dara Oyelaran",
        "account_type": "human",
        "department": "Finance",
        "employment_status": "active",
        "is_enabled": True,
        "is_privileged": False,
        "mfa_enabled": True,
        "production_access": False,
        "permissions": ["initiate_payment", "approve_payment"],
        "last_login_at": _NOW - timedelta(days=1),
    },
    {
        # Privilege escalation path: privileged service account, prod access, no MFA.
        "username": "svc-payment-processor",
        "display_name": "Payment Processor Service Account",
        "account_type": "service",
        "department": "Payments Engineering",
        "employment_status": "n_a",
        "is_enabled": True,
        "is_privileged": True,
        "mfa_enabled": False,
        "production_access": True,
        "permissions": ["deploy_production", "database_write"],
        "last_login_at": _NOW - timedelta(hours=6),
        "asset_tag": "AST-003",
    },
    {
        # A clean, well-managed account for contrast.
        "username": "s.nakamura",
        "display_name": "Sora Nakamura",
        "account_type": "human",
        "department": "IT Security",
        "employment_status": "active",
        "is_enabled": True,
        "is_privileged": True,
        "mfa_enabled": True,
        "production_access": True,
        "permissions": [],
        "last_login_at": _NOW - timedelta(hours=3),
    },
]

NORTHSTAR_CLOUD_FINDINGS = [
    {
        "resource_name": "s3://northstar-kyc-documents",
        "asset_tag": "AST-006",
        "finding_type": "missing_logging",
        "severity": "medium",
        "description": "Access logging is not enabled on the customer document storage bucket.",
        "recommendation": "Enable S3 server access logging and forward logs to the central log pipeline.",
    },
    {
        "resource_name": "iam-role: payment-service-execution-role",
        "asset_tag": "AST-003",
        "finding_type": "overly_permissive_iam",
        "severity": "high",
        "description": (
            "The Payment Processing Service's execution role grants write access to all S3 buckets "
            "in the account, not just the buckets it actually uses."
        ),
        "recommendation": "Scope the IAM policy to the specific bucket ARNs the service requires.",
    },
    {
        "resource_name": "security-group: sg-edge-lb",
        "asset_tag": "AST-013",
        "finding_type": "open_security_group",
        "severity": "high",
        "description": "Security group allows inbound traffic on port 22 (SSH) from 0.0.0.0/0.",
        "recommendation": "Restrict SSH access to a bastion host or VPN CIDR range only.",
    },
    {
        "resource_name": "container-platform: eks-node-group-config",
        "asset_tag": "AST-015",
        "finding_type": "configuration_drift",
        "severity": "medium",
        "description": "Node group configuration has drifted from the last approved Terraform state.",
        "recommendation": "Reconcile drift and re-apply infrastructure-as-code as the source of truth.",
    },
    {
        "resource_name": "secrets-manager: legacy-db-credentials",
        "asset_tag": "AST-012",
        "finding_type": "exposed_secret",
        "severity": "critical",
        "description": "A database credential was found committed in a configuration file in a private repo.",
        "recommendation": "Rotate the credential immediately and move it to the secrets manager.",
    },
]
