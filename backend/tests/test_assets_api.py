from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER

ASSET_PAYLOAD = {
    "asset_tag": "AST-100",
    "name": "Core Banking Database",
    "asset_type": "database",
    "owner": "Data Platform Team",
    "business_unit": "Retail Banking",
    "environment": "production",
    "criticality": "critical",
    "data_classification": "restricted",
    "internet_exposed": False,
}


def test_list_assets_requires_authentication(client):
    response = client.get("/api/v1/assets")
    assert response.status_code == 401


def test_viewer_can_list_assets(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/assets", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_viewer_cannot_create_asset(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_risk_analyst_can_create_asset(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["asset_tag"] == "AST-100"
    assert body["criticality"] == "critical"


def test_risk_analyst_cannot_delete_asset(client, make_auth_headers):
    write_headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=write_headers).json()

    response = client.delete(f"/api/v1/assets/{created['id']}", headers=write_headers)
    assert response.status_code == 403


def test_admin_can_delete_asset(client, make_auth_headers):
    admin_headers = make_auth_headers(ROLE_ADMIN)
    created = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=admin_headers).json()

    response = client.delete(f"/api/v1/assets/{created['id']}", headers=admin_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/assets/{created['id']}", headers=admin_headers)
    assert get_response.status_code == 404


def test_get_nonexistent_asset_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_ADMIN)
    response = client.get("/api/v1/assets/999999", headers=headers)
    assert response.status_code == 404


def test_create_asset_rejects_invalid_enum_value(client, make_auth_headers):
    headers = make_auth_headers(ROLE_ADMIN)
    bad_payload = dict(ASSET_PAYLOAD, criticality="super-critical")
    response = client.post("/api/v1/assets", json=bad_payload, headers=headers)
    assert response.status_code == 422


def test_update_asset_partial_fields(client, make_auth_headers):
    headers = make_auth_headers(ROLE_ADMIN)
    created = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()

    response = client.patch(
        f"/api/v1/assets/{created['id']}", json={"criticality": "high"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["criticality"] == "high"
    assert response.json()["name"] == ASSET_PAYLOAD["name"]  # unchanged


def test_add_dependency_between_assets(client, make_auth_headers):
    headers = make_auth_headers(ROLE_ADMIN)
    api_asset = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()
    db_payload = dict(ASSET_PAYLOAD, asset_tag="AST-101", asset_type="server")
    db_asset = client.post("/api/v1/assets", json=db_payload, headers=headers).json()

    response = client.post(
        f"/api/v1/assets/{api_asset['id']}/dependencies",
        json={"depends_on_asset_id": db_asset["id"], "description": "stores customer records"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["depends_on_asset_id"] == db_asset["id"]


def test_add_dependency_to_nonexistent_asset_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_ADMIN)
    api_asset = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()

    response = client.post(
        f"/api/v1/assets/{api_asset['id']}/dependencies",
        json={"depends_on_asset_id": 999999, "description": "bad ref"},
        headers=headers,
    )
    assert response.status_code == 404


def test_filter_assets_by_internet_exposed(client, make_auth_headers):
    headers = make_auth_headers(ROLE_ADMIN)
    exposed = dict(ASSET_PAYLOAD, asset_tag="AST-EXPOSED", internet_exposed=True)
    internal = dict(ASSET_PAYLOAD, asset_tag="AST-INTERNAL", internet_exposed=False)
    client.post("/api/v1/assets", json=exposed, headers=headers)
    client.post("/api/v1/assets", json=internal, headers=headers)

    response = client.get("/api/v1/assets?internet_exposed=true", headers=headers)
    tags = [a["asset_tag"] for a in response.json()]
    assert tags == ["AST-EXPOSED"]
