from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

ASSET_PAYLOAD = {
    "asset_tag": "AST-TM-1",
    "name": "Test API Gateway",
    "asset_type": "api",
    "owner": "Owner",
    "business_unit": "BU",
    "environment": "production",
    "criticality": "critical",
    "data_classification": "confidential",
}


def _create_asset(client, headers):
    return client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()


def test_viewer_cannot_create_threat(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/threats",
        json={
            "name": "Test threat",
            "description": "desc",
            "why_relevant": "This is a sufficiently long explanation for the test.",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_threat_rejects_vague_why_relevant(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post(
        "/api/v1/threats",
        json={"name": "Test threat", "description": "desc", "why_relevant": "too short"},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_threat_with_specific_justification_succeeds(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post(
        "/api/v1/threats",
        json={
            "name": "Test threat",
            "description": "desc",
            "mitre_technique_id": "T1078",
            "mitre_technique_name": "Valid Accounts",
            "why_relevant": "This specific environment has no MFA enforcement on service accounts.",
        },
        headers=headers,
    )
    assert response.status_code == 201


def test_create_attack_path_and_retrieve_with_steps(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)

    create_response = client.post(
        "/api/v1/attack-paths",
        json={
            "name": "Credential to exfiltration",
            "description": "Test attack path",
            "entry_point": "Internet",
            "target_asset_id": asset["id"],
            "likelihood": 3,
            "impact": 4,
            "steps": [
                {"sequence": 1, "description": "Step one", "asset_id": asset["id"]},
                {"sequence": 2, "description": "Step two"},
            ],
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["score"] == 12
    assert len(body["steps"]) == 2

    get_response = client.get(f"/api/v1/attack-paths/{body['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["steps"][0]["sequence"] == 1


def test_attack_path_rejects_out_of_range_likelihood(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    response = client.post(
        "/api/v1/attack-paths",
        json={
            "name": "Invalid path",
            "description": "d",
            "entry_point": "Internet",
            "target_asset_id": asset["id"],
            "likelihood": 9,
            "impact": 3,
            "steps": [],
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_get_nonexistent_attack_path_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/attack-paths/999999", headers=headers)
    assert response.status_code == 404
