"""Vendor, data security, and business continuity seed data for Northstar
Financial Services. Reuses the vendor names already referenced narratively
in the asset inventory (AST-008 Salesforce CRM) and threat model
(Compromised Third-Party Vendor threat actor) so the story is consistent
across modules.
"""

NORTHSTAR_VENDORS = [
    {
        "name": "Salesforce CRM",
        "service_description": "Customer relationship management for commercial banking clients.",
        "business_criticality": "high",
        "data_access": True,
        "data_classification_handled": "confidential",
        "security_controls_summary": "Vendor publishes a documented security program and SOC 2 report.",
        "certifications": "SOC 2 Type II, ISO/IEC 27001",
        "has_incident_history": False,
        "subprocessors": "AWS (infrastructure hosting)",
        "availability_sla_percent": 99.9,
        "contractual_security_clause": True,
        "data_retention_policy": "Data retained for the duration of the contract plus 90 days.",
        "exit_strategy_defined": True,
    },
    {
        "name": "Legacy Payroll Processor",
        "service_description": "Third-party payroll processing for all Northstar employees.",
        "business_criticality": "high",
        "data_access": True,
        "data_classification_handled": "restricted",
        "security_controls_summary": "Limited documentation provided; no independent audit report available.",
        "certifications": "",
        "has_incident_history": True,
        "incident_history_notes": (
            "Vendor disclosed a data exposure incident in 2023 affecting a subset of client employee "
            "records at another customer; Northstar's own data was not confirmed affected."
        ),
        "subprocessors": "Undisclosed sub-processor for tax filing services",
        "availability_sla_percent": None,
        "contractual_security_clause": False,
        "data_retention_policy": "Not clearly documented in the current contract.",
        "exit_strategy_defined": False,
    },
    {
        "name": "Cloud Email & Productivity Suite",
        "service_description": "Corporate email, calendar, and document collaboration for all employees.",
        "business_criticality": "high",
        "data_access": True,
        "data_classification_handled": "confidential",
        "security_controls_summary": "Well-documented enterprise security program with regular audits.",
        "certifications": "SOC 2 Type II, ISO/IEC 27001, ISO/IEC 27018",
        "has_incident_history": False,
        "subprocessors": "",
        "availability_sla_percent": 99.9,
        "contractual_security_clause": True,
        "data_retention_policy": "Configurable retention policy managed by Northstar IT.",
        "exit_strategy_defined": True,
    },
]

# Fields: asset_tag, name, category, classification, encrypted,
# access_controlled, retention_defined, retention_period_days, exposure_notes
NORTHSTAR_DATA_ASSETS = [
    (
        "AST-004",
        "Customer PII in Customer Database",
        "pii",
        "restricted",
        True,
        True,
        True,
        2555,
        "",
    ),
    (
        "AST-004",
        "Payment/Transaction Records",
        "financial_data",
        "restricted",
        True,
        True,
        True,
        2555,
        "",
    ),
    (
        "AST-006",
        "Scanned KYC Documents",
        "pii",
        "confidential",
        True,
        True,
        False,
        None,
        "Access logging not yet enabled - see Cloud Security findings for AST-006.",
    ),
    (
        "AST-012",
        "Core Banking Ledger Data",
        "financial_data",
        "restricted",
        True,
        True,
        True,
        3650,
        "",
    ),
    (
        "AST-010",
        "Internal Policy Documents (RAG source)",
        "business_data",
        "internal",
        True,
        True,
        False,
        None,
        "No formal retention policy defined for the RAG knowledge source documents.",
    ),
]

# Fields: asset_tag, rto_hours, rpo_hours, backup_frequency,
# last_backup_tested_days_ago, last_dr_test_days_ago, dr_test_result
NORTHSTAR_CONTINUITY_PLANS = [
    (
        "AST-004",
        4,
        1,
        "continuous replication + daily snapshot",
        30,
        90,
        "Successful full restore to isolated environment.",
    ),
    (
        "AST-003",
        2,
        1,
        "continuous replication",
        20,
        400,
        "Not yet re-tested since last year's DR exercise.",
    ),
    ("AST-012", 8, 4, "nightly", 200, None, ""),
    ("AST-001", None, None, "N/A - stateless application tier", None, None, ""),
]
