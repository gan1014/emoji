
from fastapi.testclient import TestClient

from app.main import app


# Create a test client for FastAPI
client = TestClient(app)


def test_home_endpoint():
    """Test whether the home API is working."""

    response = client.get("/")

    assert response.status_code == 200


def test_health_endpoint():
    """Test whether the health API is working."""

    response = client.get("/health")

    assert response.status_code == 200
