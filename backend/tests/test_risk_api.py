from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

ASSET_PAYLOAD = {
    "asset_tag": "AST-RISK-API",
    "name": "Test Core Database",
    "asset_type": "database",
    "owner": "Owner",
    "business_unit": "BU",
    "environment": "production",
    "criticality": "critical",
    "data_classification": "restricted",
    "internet_exposed": False,
}


def _create_asset(client, headers):
    return client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()


def test_viewer_cannot_create_risk_record(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/risk-register",
        json={"title": "x", "description": "d", "asset_id": 1, "threat_severity": "low"},
        headers=headers,
    )
    assert response.status_code == 403


def test_create_risk_record_end_to_end(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)

    response = client.post(
        "/api/v1/risk-register",
        json={
            "title": "Unpatched TLS library",
            "description": "A known-exploited vulnerability in the TLS library.",
            "asset_id": asset["id"],
            "threat_severity": "high",
            "known_exploited": True,
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["inherent_score"] == body["likelihood"] * body["impact"]
    assert body["asset_criticality"] == "critical"
    assert len(body["contributing_factors"]) > 0
    assert body["treatment_decision"] is None


def test_create_risk_record_rejects_invalid_severity(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    response = client.post(
        "/api/v1/risk-register",
        json={
            "title": "x",
            "description": "d",
            "asset_id": asset["id"],
            "threat_severity": "super-critical",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_create_risk_record_unknown_asset_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post(
        "/api/v1/risk-register",
        json={"title": "x", "description": "d", "asset_id": 999999, "threat_severity": "low"},
        headers=headers,
    )
    assert response.status_code == 404


def test_update_treatment_requires_reason(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    created = client.post(
        "/api/v1/risk-register",
        json={"title": "x", "description": "d", "asset_id": asset["id"], "threat_severity": "medium"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/risk-register/{created['id']}/treatment",
        json={"treatment_decision": "mitigate", "treatment_reason": "short", "owner": "Team"},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_treatment_succeeds_with_valid_payload(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    created = client.post(
        "/api/v1/risk-register",
        json={"title": "x", "description": "d", "asset_id": asset["id"], "threat_severity": "medium"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/risk-register/{created['id']}/treatment",
        json={
            "treatment_decision": "accept",
            "treatment_reason": "Within organizational risk appetite for this asset class.",
            "owner": "Risk Committee",
            "status": "closed",
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["treatment_decision"] == "accept"
    assert response.json()["status"] == "closed"


def test_list_risk_records_filters_by_asset(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset_a = _create_asset(client, headers)
    asset_b_payload = dict(ASSET_PAYLOAD, asset_tag="AST-RISK-API-2")
    asset_b = client.post("/api/v1/assets", json=asset_b_payload, headers=headers).json()

    client.post(
        "/api/v1/risk-register",
        json={"title": "x", "description": "d", "asset_id": asset_a["id"], "threat_severity": "low"},
        headers=headers,
    )
    client.post(
        "/api/v1/risk-register",
        json={"title": "y", "description": "d", "asset_id": asset_b["id"], "threat_severity": "low"},
        headers=headers,
    )

    response = client.get(f"/api/v1/risk-register?asset_id={asset_a['id']}", headers=headers)
    assert len(response.json()) == 1
    assert response.json()[0]["asset_id"] == asset_a["id"]
