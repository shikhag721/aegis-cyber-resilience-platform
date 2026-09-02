from app.models.user import ROLE_RISK_ANALYST, ROLE_VIEWER

CONTROL_PAYLOAD = {
    "control_id": "CTRL-API-1",
    "title": "MFA Enforcement",
    "description": "d",
    "control_objective": "o",
    "framework_reference": "NIST CSF PR.AC-7",
    "test_procedure": "Sample privileged accounts and confirm MFA enrollment.",
}


def test_viewer_cannot_create_control(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post("/api/v1/controls", json=CONTROL_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_create_control_and_assessment(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    control = client.post("/api/v1/controls", json=CONTROL_PAYLOAD, headers=headers).json()

    created = client.post(
        "/api/v1/controls/assessments",
        json={"control_id": control["id"]},
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["overall_status"] == "Not Assessed"


def test_update_assessment_changes_status_and_writes_audit_entry(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    control = client.post("/api/v1/controls", json=CONTROL_PAYLOAD, headers=headers).json()
    assessment = client.post(
        "/api/v1/controls/assessments", json={"control_id": control["id"]}, headers=headers
    ).json()

    updated = client.patch(
        f"/api/v1/controls/assessments/{assessment['id']}",
        json={
            "design_effectiveness": "effective",
            "operating_effectiveness": "effective",
            "reason": "Verified via access review sample.",
        },
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["overall_status"] == "Effective"

    audit_entries = client.get(
        "/api/v1/audit-log?object_type=ControlAssessment", headers=headers
    ).json()
    assert any(e["object_id"] == assessment["id"] for e in audit_entries)


def test_gap_analysis_endpoint(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    control = client.post("/api/v1/controls", json=CONTROL_PAYLOAD, headers=headers).json()
    client.post("/api/v1/controls/assessments", json={"control_id": control["id"]}, headers=headers)

    response = client.get("/api/v1/controls/gap-analysis", headers=headers)
    assert response.status_code == 200
    assert any(f["finding_type"] == "not_assessed" for f in response.json())


def test_create_and_list_evidence(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    control = client.post("/api/v1/controls", json=CONTROL_PAYLOAD, headers=headers).json()
    assessment = client.post(
        "/api/v1/controls/assessments", json={"control_id": control["id"]}, headers=headers
    ).json()

    created = client.post(
        "/api/v1/evidence",
        json={
            "control_assessment_id": assessment["id"],
            "evidence_type": "Access review export",
            "source": "Okta admin console",
            "collected_at": "2026-01-01",
        },
        headers=headers,
    )
    assert created.status_code == 201

    listed = client.get(f"/api/v1/evidence?control_assessment_id={assessment['id']}", headers=headers)
    assert len(listed.json()) == 1


def test_viewer_cannot_create_evidence(client, make_auth_headers):
    headers = make_auth_headers(ROLE_VIEWER)
    response = client.post(
        "/api/v1/evidence",
        json={
            "control_assessment_id": 1,
            "evidence_type": "x",
            "source": "x",
            "collected_at": "2026-01-01",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_audit_log_has_no_write_endpoints():
    """No POST/PATCH/DELETE route exists on /audit-log - entries can only be
    created as a side effect of another service's state change.
    """
    from app.api.v1.audit import router

    all_methods = {method for route in router.routes for method in route.methods}
    assert "GET" in all_methods
    assert not {"POST", "PATCH", "DELETE", "PUT"} & all_methods


def test_advancing_incident_writes_audit_entry(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    incident = client.post(
        "/api/v1/incidents",
        json={"title": "x", "description": "d", "severity": "high"},
        headers=headers,
    ).json()
    client.post(
        f"/api/v1/incidents/{incident['id']}/advance",
        json={"description": "Triaged as high priority given scope."},
        headers=headers,
    )
    entries = client.get(
        f"/api/v1/audit-log?object_type=Incident&object_id={incident['id']}", headers=headers
    ).json()
    assert len(entries) == 1
    assert entries[0]["new_value"]["stage"] == "triage"


def test_updating_risk_treatment_writes_audit_entry(client, make_auth_headers):
    headers = make_auth_headers(ROLE_RISK_ANALYST)
    asset = client.post(
        "/api/v1/assets",
        json={
            "asset_tag": "AST-AUDIT-1",
            "name": "x",
            "asset_type": "server",
            "owner": "o",
            "business_unit": "bu",
            "environment": "production",
            "criticality": "high",
            "data_classification": "confidential",
        },
        headers=headers,
    ).json()
    risk = client.post(
        "/api/v1/risk-register",
        json={"title": "x", "description": "d", "asset_id": asset["id"], "threat_severity": "high"},
        headers=headers,
    ).json()

    client.patch(
        f"/api/v1/risk-register/{risk['id']}/treatment",
        json={
            "treatment_decision": "mitigate",
            "treatment_reason": "Scheduling remediation next sprint.",
            "owner": "Platform Team",
            "status": "treatment_in_progress",
        },
        headers=headers,
    )
    entries = client.get(
        f"/api/v1/audit-log?object_type=RiskRecord&object_id={risk['id']}", headers=headers
    ).json()
    assert len(entries) == 1
    assert entries[0]["new_value"]["status"] == "treatment_in_progress"
