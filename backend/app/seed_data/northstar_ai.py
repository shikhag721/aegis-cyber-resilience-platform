"""AI inventory and AI security seed data for Northstar Financial Services.
Reuses the two AI systems already referenced narratively in the asset
inventory (AST-009 AI Customer Support Assistant, AST-010 Internal RAG
Knowledge Assistant) and adds a third, deliberately under-governed example
(an experimental AI trading-signal tool) so the deterministic gap analysis
has something real to flag on a fresh clone.
"""

# Fields: name, asset_tag, business_owner, technical_owner, purpose,
# model_provider, data_processed, user_base, integrations, tools_available,
# permissions_summary, deployment_environment, human_oversight,
# monitoring_enabled, influences_decisions, regulatory_risk_tier
NORTHSTAR_AI_SYSTEMS = [
    {
        "name": "AI Customer Support Assistant",
        "asset_tag": "AST-009",
        "business_owner": "Head of Customer Support",
        "technical_owner": "Support Systems Analyst",
        "purpose": "Drafts suggested responses to customer support chat inquiries for agent review.",
        "model_provider": "Third-party LLM API",
        "data_processed": "Customer chat messages, including names and order details.",
        "user_base": "Customer support agents (draft review), customers (chat interface)",
        "integrations": ["Customer Database", "Ticketing System"],
        "tools_available": [],
        "permissions_summary": "Read-only access to customer order history for context.",
        "deployment_environment": "production",
        "human_oversight": True,
        "monitoring_enabled": True,
        "influences_decisions": False,
        "regulatory_risk_tier": "limited",
    },
    {
        "name": "Internal RAG Knowledge Assistant",
        "asset_tag": "AST-010",
        "business_owner": "Enterprise Architecture",
        "technical_owner": "Enterprise Architecture",
        "purpose": "Answers employee questions against internal policy and knowledge documents.",
        "model_provider": "Internal model (self-hosted, RAG over internal documents)",
        "data_processed": "Internal policy documents and employee questions.",
        "user_base": "All Northstar employees",
        "integrations": ["Customer Document Storage (KYC documents)"],
        "tools_available": ["document_retrieval"],
        "permissions_summary": "Read-only access to the internal document knowledge base.",
        "deployment_environment": "production",
        "human_oversight": True,
        "monitoring_enabled": True,
        "influences_decisions": False,
        "regulatory_risk_tier": "minimal",
    },
    {
        "name": "Experimental AI Trading Signal Assistant",
        "asset_tag": None,
        "business_owner": "Quantitative Strategy (informal pilot - no assigned business owner)",
        "technical_owner": "None assigned",
        "purpose": (
            "Generates suggested trade signals for a pilot desk, with output sometimes acted on directly."
        ),
        "model_provider": "Third-party LLM API",
        "data_processed": "Market data feeds and internal position data.",
        "user_base": "A small pilot group of traders",
        "integrations": ["Trading Execution System (pilot)"],
        "tools_available": ["execute_trade_suggestion"],
        "permissions_summary": "Can submit trade suggestions directly into the execution queue.",
        "deployment_environment": "production",
        "human_oversight": False,
        "monitoring_enabled": False,
        "influences_decisions": True,
        "regulatory_risk_tier": "high",
    },
]

# (ai_system_name, risk_lens, finding_type, severity, description, recommendation)
NORTHSTAR_AI_SECURITY_FINDINGS = [
    (
        "AI Customer Support Assistant",
        "application",
        "prompt_injection",
        "medium",
        "Customer chat input is passed into the model context with only basic filtering.",
        "Add an instruction-hierarchy safeguard and output validation before agents see drafted replies.",
    ),
    (
        "Internal RAG Knowledge Assistant",
        "data",
        "sensitive_info_disclosure",
        "high",
        (
            "The RAG index includes KYC document content, which may surface customer PII in answers "
            "to employee questions that were not access-controlled per document sensitivity."
        ),
        "Apply document-level access control in retrieval, not just at the source repository.",
    ),
    (
        "Experimental AI Trading Signal Assistant",
        "governance",
        "improper_authorization",
        "critical",
        "The pilot was deployed to production without a formal AI use-case approval or risk assessment.",
        "Halt production use until the use case completes the AI governance intake and approval process.",
    ),
]
