from app.models.user import ROLE_VIEWER


def test_viewer_can_read_dashboard_summary(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "assets_total" in body
    assert "risks_by_residual_rating" in body


def test_viewer_can_read_executive_report(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/reports/executive-summary", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "generated_at" in body
    assert "summary" in body
    assert "recommended_actions" in body
    assert isinstance(body["recommended_actions"], list)
    assert len(body["recommended_actions"]) >= 1


def test_unauthenticated_dashboard_request_rejected(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401
