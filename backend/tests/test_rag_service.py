import pytest

from app.db.session import SessionLocal
from app.services import rag as rag_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _pipeline(**overrides) -> dict:
    defaults = dict(
        name="Test RAG Pipeline",
        data_sources=["Internal documents"],
        document_level_access_control=True,
        retrieved_content_sanitized=True,
        allows_untrusted_data_sources=False,
        source_content_validated=True,
        output_validated_before_use=True,
        notes="",
    )
    defaults.update(overrides)
    return defaults


def test_well_configured_pipeline_produces_no_findings(db_session):
    pipeline = rag_service.create_rag_pipeline(db_session, _pipeline())
    findings = rag_service.analyze_rag_pipeline(pipeline)
    assert findings == []


def test_missing_document_level_access_control_flagged_broken_authorization(db_session):
    pipeline = rag_service.create_rag_pipeline(
        db_session, _pipeline(document_level_access_control=False)
    )
    findings = rag_service.analyze_rag_pipeline(pipeline)
    assert any(f.root_cause == "broken_authorization" for f in findings)


def test_unsanitized_retrieved_content_flagged_prompt_injection(db_session):
    pipeline = rag_service.create_rag_pipeline(
        db_session, _pipeline(retrieved_content_sanitized=False)
    )
    findings = rag_service.analyze_rag_pipeline(pipeline)
    assert any(f.root_cause == "prompt_injection" for f in findings)


def test_untrusted_unvalidated_sources_flagged_data_poisoning(db_session):
    pipeline = rag_service.create_rag_pipeline(
        db_session,
        _pipeline(allows_untrusted_data_sources=True, source_content_validated=False),
    )
    findings = rag_service.analyze_rag_pipeline(pipeline)
    assert any(f.root_cause == "data_poisoning" for f in findings)


def test_untrusted_but_validated_sources_not_flagged_data_poisoning(db_session):
    pipeline = rag_service.create_rag_pipeline(
        db_session,
        _pipeline(allows_untrusted_data_sources=True, source_content_validated=True),
    )
    findings = rag_service.analyze_rag_pipeline(pipeline)
    assert not any(f.root_cause == "data_poisoning" for f in findings)


def test_unvalidated_output_flagged_insecure_output_handling(db_session):
    pipeline = rag_service.create_rag_pipeline(
        db_session, _pipeline(output_validated_before_use=False)
    )
    findings = rag_service.analyze_rag_pipeline(pipeline)
    assert any(f.root_cause == "insecure_output_handling" for f in findings)


def test_same_symptom_different_root_causes_are_distinguishable(db_session):
    """Two pipelines can both leak sensitive info, but for different reasons -
    the root-cause classification, not just severity, must differ."""
    authz_gap = rag_service.create_rag_pipeline(
        db_session,
        _pipeline(name="authz-gap", document_level_access_control=False),
    )
    injection_gap = rag_service.create_rag_pipeline(
        db_session,
        _pipeline(name="injection-gap", retrieved_content_sanitized=False),
    )
    authz_findings = {f.root_cause for f in rag_service.analyze_rag_pipeline(authz_gap)}
    injection_findings = {f.root_cause for f in rag_service.analyze_rag_pipeline(injection_gap)}
    assert "broken_authorization" in authz_findings
    assert "broken_authorization" not in injection_findings
    assert "prompt_injection" in injection_findings
    assert "prompt_injection" not in authz_findings


def test_analyze_all_pipelines_aggregates_across_pipelines(db_session):
    rag_service.create_rag_pipeline(db_session, _pipeline(name="clean"))
    rag_service.create_rag_pipeline(
        db_session, _pipeline(name="leaky", document_level_access_control=False)
    )
    findings = rag_service.analyze_all_rag_pipelines(db_session)
    assert any(f.pipeline_name == "leaky" for f in findings)
    assert not any(f.pipeline_name == "clean" for f in findings)
