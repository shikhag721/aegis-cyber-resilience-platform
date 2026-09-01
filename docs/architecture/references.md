# References

External frameworks referenced by AEGIS, with how each is used. AEGIS does
not claim certification against, or endorsement by, any of the bodies
below — see `SECURITY.md` and `README.md` disclaimers.

| Framework | Publisher | Used for |
|---|---|---|
| NIST Cybersecurity Framework 2.0 | NIST | Govern/Identify/Protect/Detect/Respond/Recover structure for general control mapping |
| NIST AI Risk Management Framework | NIST | AI governance workflow structure (Phase 10) |
| NIST Generative AI Profile (AI 600-1) | NIST | GenAI-specific risk categories for AI/RAG/agent security (Phase 10-11) |
| CIS Controls v8.1 | Center for Internet Security | Control-library reference points for asset/IAM/vulnerability controls |
| MITRE ATT&CK | MITRE | Technique references in threat modeling / attack paths (Phase 2), each explained in scenario context, not just an ID lookup |
| OWASP Application Security guidance | OWASP Foundation | Application/API security scenarios (Phase 6) |
| OWASP GenAI/LLM security guidance | OWASP GenAI Security Project | AI/RAG/agent security risk categories (Phase 10-11) |
| ISO/IEC 27001 concepts | ISO/IEC | Control-assessment structure inspiration (design vs. operating effectiveness) |

Each phase's own documentation (`docs/threat-models/`, `docs/risk-methodology/`,
`docs/ai-security/`, etc.) links back to the specific concept used and
explains, in that context: what the control means, why it matters, what
risk it addresses, what evidence would demonstrate effectiveness, and what
limitations exist — per the brief's "Industry-Alignment Principle."
