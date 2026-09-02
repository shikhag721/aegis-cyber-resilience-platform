from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

AI_SYSTEM_PAYLOAD = {
    "name": "Test AI Customer Assistant",
    "business_owner": "o",
    "technical_owner": "t",
    "purpose": "p",
    "model_provider": "Third-party LLM API",
    "data_processed": "Customer chat messages",
    "user_base": "Customers",
    "deployment_environment": "production",
}


def test_viewer_cannot_create_ai_system(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post("/api/v1/ai-inventory", json=AI_SYSTEM_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_create_and_get_ai_system(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post("/api/v1/ai-inventory", json=AI_SYSTEM_PAYLOAD, headers=headers)
    assert created.status_code == 201
    ai_system_id = created.json()["id"]

    fetched = client.get(f"/api/v1/ai-inventory/{ai_system_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["findings"] == []


def test_get_nonexistent_ai_system_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/ai-inventory/999999", headers=headers)
    assert response.status_code == 404


def test_create_security_finding_and_list(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    ai_system = client.post("/api/v1/ai-inventory", json=AI_SYSTEM_PAYLOAD, headers=headers).json()

    created = client.post(
        f"/api/v1/ai-security/ai-systems/{ai_system['id']}/findings",
        json={
            "risk_lens": "application",
            "finding_type": "prompt_injection",
            "severity": "high",
            "description": "Customer input is passed directly into the model context with no filtering.",
            "recommendation": "Add input sanitization and an instruction-hierarchy safeguard.",
        },
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["risk_lens"] == "application"

    findings = client.get("/api/v1/ai-security/findings", headers=headers).json()
    assert len(findings) == 1


def test_create_finding_for_nonexistent_ai_system_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post(
        "/api/v1/ai-security/ai-systems/999999/findings",
        json={
            "risk_lens": "model",
            "finding_type": "model_manipulation",
            "severity": "high",
            "description": "d",
            "recommendation": "r",
        },
        headers=headers,
    )
    assert response.status_code == 404


def test_gap_analysis_endpoint_flags_excessive_agency(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    payload = dict(AI_SYSTEM_PAYLOAD, tools_available=["database_query"], human_oversight=False)
    client.post("/api/v1/ai-inventory", json=payload, headers=headers)

    response = client.get("/api/v1/ai-security/gap-analysis", headers=headers)
    assert response.status_code == 200
    assert any(f["finding_type"] == "excessive_agency_risk" for f in response.json())
