
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_successfully():
    """Test whether a valid task can be created."""

    response = client.post(
        "/tasks",
        json={
            "task": "PYTEST - API creation test",
            "priority": "high",
            "category": "education",
            "due_date": None
        }
    )

    assert response.status_code in (200, 201)
    assert response.json()

    print("Created task response:", response.json())
