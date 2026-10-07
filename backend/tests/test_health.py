from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    """Verify the basic health endpoint."""

    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


def test_database_health_check():
    """Verify the database health endpoint."""

    response = client.get("/health/database")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["database"] == "connected"
