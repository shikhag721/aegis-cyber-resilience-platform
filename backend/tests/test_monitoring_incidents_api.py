from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER


def test_viewer_cannot_create_security_event(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/security-events",
        json={"event_type": "failed_login", "username": "x"},
        headers=headers,
    )
    assert response.status_code == 403


def test_create_event_and_correlate(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    for event_type in ["failed_login", "successful_login", "unusual_location", "database_access"]:
        client.post(
            "/api/v1/security-events",
            json={"event_type": event_type, "username": "compromised_user"},
            headers=headers,
        )
    findings = client.get("/api/v1/security-events/correlate", headers=headers).json()
    assert any(f["username"] == "compromised_user" and f["severity"] == "critical" for f in findings)


def test_viewer_cannot_create_incident(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/incidents",
        json={"title": "x", "description": "d", "severity": "high"},
        headers=headers,
    )
    assert response.status_code == 403


def test_create_and_advance_incident(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "Compromised privileged account",
            "description": "d",
            "severity": "critical",
            "indicators": ["failed_login", "successful_login"],
        },
        headers=headers,
    ).json()
    assert created["stage"] == "detection"
    assert len(created["timeline"]) == 1

    advanced = client.post(
        f"/api/v1/incidents/{created['id']}/advance",
        json={"description": "Triaged as critical priority given privileged account impact."},
        headers=headers,
    )
    assert advanced.status_code == 200
    assert advanced.json()["stage"] == "triage"
    assert len(advanced.json()["timeline"]) == 2


def test_advance_incident_rejects_vague_description(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post(
        "/api/v1/incidents",
        json={"title": "x", "description": "d", "severity": "medium"},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/v1/incidents/{created['id']}/advance", json={"description": "ok"}, headers=headers
    )
    assert response.status_code == 422


def test_get_nonexistent_incident_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/incidents/999999", headers=headers)
    assert response.status_code == 404


def test_update_incident_remediation(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post(
        "/api/v1/incidents",
        json={"title": "x", "description": "d", "severity": "low"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/incidents/{created['id']}",
        json={"remediation": "Rotated credentials."},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["remediation"] == "Rotated credentials."
