from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

PIPELINE_PAYLOAD = {
    "name": "Test RAG Pipeline",
    "data_sources": ["Internal documents"],
    "document_level_access_control": True,
    "retrieved_content_sanitized": True,
    "source_content_validated": True,
    "output_validated_before_use": True,
}


def test_viewer_cannot_create_pipeline(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post("/api/v1/rag-security/pipelines", json=PIPELINE_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_create_and_get_pipeline(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post("/api/v1/rag-security/pipelines", json=PIPELINE_PAYLOAD, headers=headers)
    assert created.status_code == 201
    pipeline_id = created.json()["id"]

    fetched = client.get(f"/api/v1/rag-security/pipelines/{pipeline_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Test RAG Pipeline"


def test_get_nonexistent_pipeline_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/rag-security/pipelines/999999", headers=headers)
    assert response.status_code == 404


def test_gap_analysis_endpoint_flags_broken_authorization(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    payload = dict(PIPELINE_PAYLOAD, name="Leaky Pipeline", document_level_access_control=False)
    client.post("/api/v1/rag-security/pipelines", json=payload, headers=headers)

    response = client.get("/api/v1/rag-security/gap-analysis", headers=headers)
    assert response.status_code == 200
    assert any(f["root_cause"] == "broken_authorization" for f in response.json())
