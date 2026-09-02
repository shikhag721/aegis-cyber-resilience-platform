"""RAG pipeline CRUD and deterministic root-cause gap analysis (Section 26).
See app/models/rag.py for why root cause, not just symptom, is classified.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.rag import RAGPipeline, RAGRootCause

_SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass
class RAGFinding:
    pipeline_name: str
    root_cause: str
    severity: str
    detail: str


def analyze_rag_pipeline(pipeline: RAGPipeline) -> list[RAGFinding]:
    findings: list[RAGFinding] = []

    if not pipeline.document_level_access_control:
        findings.append(
            RAGFinding(
                pipeline_name=pipeline.name,
                root_cause=RAGRootCause.BROKEN_AUTHORIZATION.value,
                severity="high",
                detail=(
                    f"'{pipeline.name}' controls access at the source-repository level only - "
                    "retrieval does not check per-document sensitivity, so any user authorized to "
                    "query the assistant can retrieve documents they would not be authorized to "
                    "open directly. This is an access-control gap, not a model-behavior problem."
                ),
            )
        )

    if not pipeline.retrieved_content_sanitized:
        findings.append(
            RAGFinding(
                pipeline_name=pipeline.name,
                root_cause=RAGRootCause.PROMPT_INJECTION.value,
                severity="high",
                detail=(
                    f"'{pipeline.name}' inserts retrieved content directly into the model context "
                    "without treating it as untrusted input - a document containing hidden "
                    "instructions could hijack the model's behavior for that query."
                ),
            )
        )

    if pipeline.allows_untrusted_data_sources and not pipeline.source_content_validated:
        findings.append(
            RAGFinding(
                pipeline_name=pipeline.name,
                root_cause=RAGRootCause.DATA_POISONING.value,
                severity="high",
                detail=(
                    f"'{pipeline.name}' ingests content from untrusted sources with no validation "
                    "before indexing - an attacker who can place content in those sources could "
                    "poison what the assistant treats as ground truth."
                ),
            )
        )

    if not pipeline.output_validated_before_use:
        findings.append(
            RAGFinding(
                pipeline_name=pipeline.name,
                root_cause=RAGRootCause.INSECURE_OUTPUT_HANDLING.value,
                severity="medium",
                detail=(
                    f"'{pipeline.name}' output is displayed or acted on downstream without "
                    "validation - unvalidated model output reaching a user or another system "
                    "carries injection/rendering risk of its own."
                ),
            )
        )

    findings.sort(key=lambda f: _SEVERITY_RANK.get(f.severity, 99))
    return findings


def analyze_all_rag_pipelines(db: Session) -> list[RAGFinding]:
    findings: list[RAGFinding] = []
    for pipeline in list_rag_pipelines(db):
        findings.extend(analyze_rag_pipeline(pipeline))
    findings.sort(key=lambda f: _SEVERITY_RANK.get(f.severity, 99))
    return findings


def create_rag_pipeline(db: Session, data: dict) -> RAGPipeline:
    pipeline = RAGPipeline(**data)
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline


def list_rag_pipelines(db: Session) -> list[RAGPipeline]:
    return db.query(RAGPipeline).order_by(RAGPipeline.name).all()


def get_rag_pipeline(db: Session, pipeline_id: int) -> RAGPipeline | None:
    return db.get(RAGPipeline, pipeline_id)
