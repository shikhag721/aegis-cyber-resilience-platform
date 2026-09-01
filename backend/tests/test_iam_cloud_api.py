from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER


def test_viewer_cannot_create_identity_account(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/iam/accounts",
        json={
            "username": "x",
            "display_name": "X",
            "account_type": "human",
            "department": "Engineering",
            "employment_status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_account_and_see_finding(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    client.post(
        "/api/v1/iam/accounts",
        json={
            "username": "priv_test",
            "display_name": "Priv Test",
            "account_type": "human",
            "department": "IT Security",
            "employment_status": "active",
            "is_privileged": True,
            "mfa_enabled": False,
        },
        headers=headers,
    )
    findings = client.get("/api/v1/iam/findings", headers=headers).json()
    assert any(f["account_username"] == "priv_test" and f["finding_type"] == "missing_mfa" for f in findings)


def test_list_identity_accounts(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.get("/api/v1/iam/accounts", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_viewer_cannot_create_cloud_finding(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/cloud/findings",
        json={
            "resource_name": "test",
            "finding_type": "public_exposure",
            "severity": "high",
            "description": "d",
            "recommendation": "r",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_and_update_cloud_finding(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    created = client.post(
        "/api/v1/cloud/findings",
        json={
            "resource_name": "s3-kyc-docs",
            "finding_type": "missing_logging",
            "severity": "medium",
            "description": "Access logging not enabled",
            "recommendation": "Enable S3 access logging",
        },
        headers=headers,
    ).json()
    assert created["status"] == "open"

    updated = client.patch(
        f"/api/v1/cloud/findings/{created['id']}/status?status=remediated", headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "remediated"


def test_update_nonexistent_cloud_finding_returns_404(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    response = client.patch("/api/v1/cloud/findings/999999/status?status=remediated", headers=headers)
    assert response.status_code == 404
