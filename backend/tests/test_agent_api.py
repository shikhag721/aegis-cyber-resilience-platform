from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

AGENT_PAYLOAD = {
    "name": "Test Agent",
    "purpose": "p",
    "tools_available": ["lookup"],
    "autonomy_level": "human_approval_required",
    "requires_human_approval": True,
    "guardrails_description": "Restricted to read-only tools.",
}


def test_viewer_cannot_create_agent(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post("/api/v1/agent-security/agents", json=AGENT_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_create_agent_and_run_assessment(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    agent = client.post("/api/v1/agent-security/agents", json=AGENT_PAYLOAD, headers=headers).json()

    assessment = client.post(f"/api/v1/agent-security/agents/{agent['id']}/assessments", headers=headers)
    assert assessment.status_code == 201
    assert assessment.json()["rating"] in ("Low", "Moderate", "High", "Critical")

    latest = client.get(f"/api/v1/agent-security/agents/{agent['id']}/assessments/latest", headers=headers)
    assert latest.status_code == 200
    assert latest.json()["id"] == assessment.json()["id"]


def test_get_latest_assessment_404_when_none_exists(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    agent = client.post("/api/v1/agent-security/agents", json=AGENT_PAYLOAD, headers=headers).json()
    response = client.get(f"/api/v1/agent-security/agents/{agent['id']}/assessments/latest", headers=headers)
    assert response.status_code == 404


def test_get_nonexistent_agent_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/agent-security/agents/999999", headers=headers)
    assert response.status_code == 404


def test_create_assessment_for_nonexistent_agent_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post("/api/v1/agent-security/agents/999999/assessments", headers=headers)
    assert response.status_code == 404
