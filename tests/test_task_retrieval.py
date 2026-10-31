
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_existing_task():
    """Create a task and retrieve it from the test database."""

    create_response = client.post(
        "/tasks",
        json={
            "task": "PYTEST - Retrieval test",
            "priority": "high",
            "category": "testing"
        }
    )

    assert create_response.status_code in (200, 201)

    task_id = create_response.json()["task"]["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200

    task_data = response.json()["task"]

    assert task_data["id"] == task_id
    assert task_data["task"] == "PYTEST - Retrieval test"

    print("Retrieved task:", task_data)


def test_get_nonexistent_task():
    """An unknown task ID should return 404."""

    response = client.get("/tasks/999999")

    assert response.status_code == 404
