# AI Security

Covers AI inventory (Phase 10), AI-specific security findings across the
eight risk lenses (Model/Application/Data/Identity/Infrastructure/Tool/
Third-Party/Governance), and RAG + AI-agent security (Phase 11).

## AI Inventory & AI Security (Phase 10)
`app/services/ai.py::analyze_ai_inventory` computes governance gap findings
directly from the AI system inventory - excessive agency (tool access
without human oversight), unreviewed decision influence, missing
monitoring, and high-tier third-party models without oversight - the same
computed-not-stored pattern used by IAM, controls, data security, and
continuity.

## RAG Security (Phase 11)
The same visible symptom - a RAG assistant surfacing information a user
shouldn't see - can have two different root causes that need different
fixes:
- **Broken authorization**: retrieval respects source-repository access,
  not per-document sensitivity, so an authorized user of the tool can
  retrieve documents they'd not be authorized to open directly.
- **Prompt injection**: retrieved content is inserted into the model
  context without being treated as untrusted input, so a document with
  hidden instructions can hijack the model's behavior.

`app/services/rag.py::analyze_rag_pipeline` classifies findings by root
cause (also covering data poisoning and insecure output handling), not
just by symptom or severity - see `app/models/rag.py` for the reasoning
behind each of the four flags it checks.

## AI Agent Security (Phase 11)
Agents that can take action (not just produce text) are assessed for
blast radius: how likely a bad instruction is to be acted on (autonomy
level, human-approval requirement, documented guardrails) times how bad
it would be if it were (irreversibility, financial-transaction
capability, breadth of tool access). `app/services/agent.py::assess_agent`
is its own explainable scorer following the same pattern as vendor risk -
see `docs/decisions/0009-agent-blast-radius-not-reusing-risk-engine.md`.

## AI Governance Lifecycle (illustrative)
Inventory → Classification → Risk → Control → Evidence → Approval →
Monitoring → Reassessment. AEGIS implements the inventory, classification,
and risk stages concretely; the remaining stages are represented through
the existing GRC controls/evidence/audit-log modules (Phase 8) rather than
a separate AI-specific workflow, since the same control-assessment and
evidence machinery applies regardless of what the control is protecting.
