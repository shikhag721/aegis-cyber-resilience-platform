def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "aegis-backend"}


def test_health_db(client):
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_security_headers_present(client):
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
