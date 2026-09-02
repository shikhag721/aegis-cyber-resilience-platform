"""RAG (retrieval-augmented generation) pipeline security (Section 26).

The key insight this module encodes: the SAME visible symptom - a RAG
assistant surfacing information a user should not have seen - can have two
entirely different root causes that call for different fixes: retrieval
was never access-controlled per document (broken authorization), or the
model was manipulated via instructions hidden in retrieved content (prompt
injection). analyze_rag_pipeline() classifies findings by root cause, not
just symptom - see docs/ai-security/README.md.
"""
from enum import StrEnum

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RAGRootCause(StrEnum):
    BROKEN_AUTHORIZATION = "broken_authorization"
    PROMPT_INJECTION = "prompt_injection"
    DATA_POISONING = "data_poisoning"
    INSECURE_OUTPUT_HANDLING = "insecure_output_handling"


class RAGPipeline(Base):
    __tablename__ = "rag_pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    ai_system_id: Mapped[int | None] = mapped_column(ForeignKey("ai_systems.id"), nullable=True)
    data_sources: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["Internal policy documents"]

    # Per-document access control at the retrieval layer, not just at the
    # source repository - missing this is a broken-authorization root cause.
    document_level_access_control: Mapped[bool] = mapped_column(Boolean, default=False)

    # Whether retrieved content is treated as untrusted input (stripped of
    # embedded instructions) before being placed in the model context -
    # missing this is a prompt-injection amplification root cause.
    retrieved_content_sanitized: Mapped[bool] = mapped_column(Boolean, default=False)

    # Whether the pipeline ingests content from sources it does not control
    # (public web, user uploads, third-party feeds).
    allows_untrusted_data_sources: Mapped[bool] = mapped_column(Boolean, default=False)

    # Whether ingested source content is validated/reviewed before indexing -
    # missing this alongside untrusted sources is a data-poisoning root cause.
    source_content_validated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Whether model output is validated before being displayed or acted on
    # downstream - missing this is an insecure-output-handling root cause.
    output_validated_before_use: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str] = mapped_column(Text, default="")

    ai_system: Mapped["AISystem | None"] = relationship()  # noqa: F821
