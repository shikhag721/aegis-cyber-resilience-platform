from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER


def test_viewer_cannot_create_appsec_finding(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/app-security/findings",
        json={
            "resource_name": "x",
            "finding_type": "injection",
            "severity": "high",
            "description": "d",
            "recommendation": "r",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_and_list_appsec_finding(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post(
        "/api/v1/app-security/findings",
        json={
            "resource_name": "GET /api/v1/search",
            "finding_type": "injection",
            "severity": "critical",
            "description": "Unsanitized query parameter passed to a raw SQL query.",
            "owasp_reference": "OWASP API8:2023",
            "recommendation": "Use parameterized queries.",
        },
        headers=headers,
    )
    assert created.status_code == 201
    findings = client.get("/api/v1/app-security/findings", headers=headers).json()
    assert len(findings) == 1


def test_viewer_cannot_scan_for_secrets(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/app-security/secrets/scan",
        json={"text": "password = \"x\"", "location": "test.py"},
        headers=headers,
    )
    assert response.status_code == 403


def test_scan_for_secrets_finds_and_persists(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post(
        "/api/v1/app-security/secrets/scan",
        json={
            "text": "aws_key = 'AKIAIOSFODNN7EXAMPLE'",
            "location": "legacy/config.py",
            "exposure": "Internal repository",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body) == 1
    assert "AKIAIOSFODNN7EXAMPLE" not in body[0]["redacted_snippet"]

    listed = client.get("/api/v1/app-security/secrets", headers=headers).json()
    assert len(listed) == 1


def test_scan_clean_text_returns_empty(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post(
        "/api/v1/app-security/secrets/scan",
        json={"text": "def add(a, b):\n    return a + b", "location": "math.py"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json() == []


def test_update_appsec_finding_status(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post(
        "/api/v1/app-security/findings",
        json={
            "resource_name": "x",
            "finding_type": "missing_rate_limiting",
            "severity": "medium",
            "description": "d",
            "recommendation": "r",
        },
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/app-security/findings/{created['id']}/status?status=remediated", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "remediated"
