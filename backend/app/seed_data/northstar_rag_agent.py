"""RAG pipeline and AI agent seed data for Northstar Financial Services
(Phase 11). Continues the Phase 10 AI inventory narrative: the "Internal
RAG Knowledge Assistant" pipeline reproduces the exact access-control gap
already flagged as a Phase 10 AI security finding (now classified by root
cause), and the "Trading Signal Execution Agent" is the execution-layer
counterpart of the already deliberately under-governed "Experimental AI
Trading Signal Assistant."
"""

# Fields: name, ai_system_name (resolved to ai_system_id, or None), data_sources,
# document_level_access_control, retrieved_content_sanitized,
# allows_untrusted_data_sources, source_content_validated,
# output_validated_before_use, notes
NORTHSTAR_RAG_PIPELINES = [
    {
        "name": "Internal RAG Knowledge Assistant Pipeline",
        "ai_system_name": "Internal RAG Knowledge Assistant",
        "data_sources": ["Internal policy documents", "Customer Document Storage (KYC documents)"],
        "document_level_access_control": False,
        "retrieved_content_sanitized": True,
        "allows_untrusted_data_sources": False,
        "source_content_validated": True,
        "output_validated_before_use": True,
        "notes": (
            "Retrieval indexes KYC documents alongside general policy content without "
            "per-document access control - same underlying gap as the Phase 10 "
            "sensitive_info_disclosure finding, now classified by root cause."
        ),
    },
    {
        "name": "Public FAQ RAG Assistant",
        "ai_system_name": None,
        "data_sources": ["Public company website", "Community forum posts"],
        "document_level_access_control": True,
        "retrieved_content_sanitized": False,
        "allows_untrusted_data_sources": True,
        "source_content_validated": False,
        "output_validated_before_use": False,
        "notes": (
            "Pilot assistant answering public FAQ questions by pulling from public web "
            "content and an unmoderated community forum."
        ),
    },
]

# Fields: name, ai_system_name (resolved to ai_system_id, or None), purpose,
# tools_available, autonomy_level, can_take_irreversible_actions,
# can_initiate_financial_transactions, requires_human_approval,
# data_access_scope, guardrails_description
NORTHSTAR_AI_AGENTS = [
    {
        "name": "Customer Support Draft Agent",
        "ai_system_name": "AI Customer Support Assistant",
        "purpose": "Looks up order/ticket details to draft a suggested reply for a human agent to review.",
        "tools_available": ["ticket_lookup"],
        "autonomy_level": "human_approval_required",
        "can_take_irreversible_actions": False,
        "can_initiate_financial_transactions": False,
        "requires_human_approval": True,
        "data_access_scope": "Read-only customer ticket and order data.",
        "guardrails_description": "All replies are queued for human agent review before being sent.",
    },
    {
        "name": "Trading Signal Execution Agent",
        "ai_system_name": "Experimental AI Trading Signal Assistant",
        "purpose": "Submits trade suggestions directly into the execution queue for the pilot desk.",
        "tools_available": ["execute_trade_suggestion"],
        "autonomy_level": "autonomous_within_guardrails",
        "can_take_irreversible_actions": True,
        "can_initiate_financial_transactions": True,
        "requires_human_approval": False,
        "data_access_scope": (
            "Market data feeds and internal position data; can submit into the trade "
            "execution queue."
        ),
        "guardrails_description": "",
    },
]
