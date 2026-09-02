from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

VENDOR_PAYLOAD = {
    "name": "Test SaaS Vendor",
    "service_description": "d",
    "business_criticality": "medium",
    "data_classification_handled": "internal",
    "certifications": "SOC 2 Type II",
    "contractual_security_clause": True,
    "exit_strategy_defined": True,
}

ASSET_PAYLOAD = {
    "asset_tag": "AST-P9-API",
    "name": "Test Asset",
    "asset_type": "database",
    "owner": "o",
    "business_unit": "bu",
    "environment": "production",
    "criticality": "high",
    "data_classification": "restricted",
}


def test_viewer_cannot_create_vendor(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post("/api/v1/vendors", json=VENDOR_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_create_vendor_and_run_assessment(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    vendor = client.post("/api/v1/vendors", json=VENDOR_PAYLOAD, headers=headers).json()

    assessment = client.post(f"/api/v1/vendors/{vendor['id']}/assessments", headers=headers)
    assert assessment.status_code == 201
    assert assessment.json()["rating"] in ("Low", "Moderate", "High", "Critical")

    latest = client.get(f"/api/v1/vendors/{vendor['id']}/assessments/latest", headers=headers)
    assert latest.status_code == 200
    assert latest.json()["id"] == assessment.json()["id"]


def test_get_latest_assessment_404_when_none_exists(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    vendor = client.post("/api/v1/vendors", json=VENDOR_PAYLOAD, headers=headers).json()
    response = client.get(f"/api/v1/vendors/{vendor['id']}/assessments/latest", headers=headers)
    assert response.status_code == 404


def test_create_data_asset_and_findings(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()

    created = client.post(
        "/api/v1/data-security/data-assets",
        json={
            "name": "Customer PII",
            "category": "pii",
            "classification": "restricted",
            "asset_id": asset["id"],
            "encrypted": False,
        },
        headers=headers,
    )
    assert created.status_code == 201

    findings = client.get("/api/v1/data-security/findings", headers=headers).json()
    assert any(f["finding_type"] == "unencrypted_sensitive_data" for f in findings)


def test_create_continuity_plan_and_findings(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = client.post("/api/v1/assets", json=ASSET_PAYLOAD, headers=headers).json()

    created = client.post(
        "/api/v1/business-continuity/plans",
        json={"asset_id": asset["id"]},
        headers=headers,
    )
    assert created.status_code == 201

    findings = client.get("/api/v1/business-continuity/findings", headers=headers).json()
    assert any(f["finding_type"] == "missing_rto_rpo" for f in findings)


def test_viewer_cannot_create_data_asset(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/data-security/data-assets",
        json={"name": "x", "category": "pii", "classification": "restricted", "asset_id": 1},
        headers=headers,
    )
    assert response.status_code == 403
