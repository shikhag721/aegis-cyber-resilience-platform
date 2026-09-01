from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

ASSET_PAYLOAD = {
    "asset_tag": "AST-VULN-API",
    "name": "Test Server",
    "asset_type": "server",
    "owner": "Owner",
    "business_unit": "BU",
    "environment": "production",
    "criticality": "high",
    "data_classification": "confidential",
}


def _create_asset(client, headers):
    return client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()


def test_viewer_cannot_create_vulnerability(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/vulnerabilities",
        json={"title": "x", "description": "d", "asset_id": 1, "cvss_score": 5.0},
        headers=headers,
    )
    assert response.status_code == 403


def test_create_vulnerability_rejects_invalid_cvss(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    response = client.post(
        "/api/v1/vulnerabilities",
        json={"title": "x", "description": "d", "asset_id": asset["id"], "cvss_score": 11.0},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_and_get_vulnerability(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    response = client.post(
        "/api/v1/vulnerabilities",
        json={
            "cve_id": "CVE-2024-1234",
            "title": "Remote code execution",
            "description": "d",
            "asset_id": asset["id"],
            "cvss_score": 9.8,
            "known_exploited": True,
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["cvss_severity_band"] == "critical"
    assert body["remediation_status"] == "open"

    get_response = client.get(f"/api/v1/vulnerabilities/{body['id']}", headers=headers)
    assert get_response.status_code == 200


def test_assess_vulnerability_creates_linked_risk_record(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    vuln = client.post(
        "/api/v1/vulnerabilities",
        json={"title": "x", "description": "d", "asset_id": asset["id"], "cvss_score": 7.5},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/v1/vulnerabilities/{vuln['id']}/assess",
        json={"control_effectiveness": 0.3},
        headers=headers,
    )
    assert response.status_code == 201
    risk_record = response.json()
    assert risk_record["threat_severity"] == "high"

    updated_vuln = client.get(f"/api/v1/vulnerabilities/{vuln['id']}", headers=headers).json()
    assert updated_vuln["risk_record_id"] == risk_record["id"]


def test_update_remediation_status(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    vuln = client.post(
        "/api/v1/vulnerabilities",
        json={"title": "x", "description": "d", "asset_id": asset["id"], "cvss_score": 5.0},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/vulnerabilities/{vuln['id']}",
        json={"remediation_status": "remediated"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["remediation_status"] == "remediated"


def test_get_nonexistent_vulnerability_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/vulnerabilities/999999", headers=headers)
    assert response.status_code == 404


def test_filter_vulnerabilities_by_remediation_status(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = _create_asset(client, headers)
    v1 = client.post(
        "/api/v1/vulnerabilities",
        json={"title": "a", "description": "d", "asset_id": asset["id"], "cvss_score": 5.0},
        headers=headers,
    ).json()
    client.post(
        "/api/v1/vulnerabilities",
        json={"title": "b", "description": "d", "asset_id": asset["id"], "cvss_score": 6.0},
        headers=headers,
    )
    client.patch(
        f"/api/v1/vulnerabilities/{v1['id']}", json={"remediation_status": "remediated"}, headers=headers
    )

    response = client.get("/api/v1/vulnerabilities?remediation_status=remediated", headers=headers)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "a"
