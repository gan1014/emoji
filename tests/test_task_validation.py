
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rejects_short_task_name():
    """A task name shorter than 3 characters should be rejected."""

    response = client.post(
        "/tasks",
        json={
            "task": "ab"
        }
    )

    assert response.status_code == 422

def test_rejects_invalid_priority():
    """Only low, medium and high priorities are allowed."""

    response = client.post(
        "/tasks",
        json={
            "task": "Prepare project report",
            "priority": "urgent"
        }
    )

    assert response.status_code == 422