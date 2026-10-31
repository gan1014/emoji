
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_update_existing_task():
    """Create a task and update its category."""

    # Create a temporary task
    create_response = client.post(
        "/tasks",
        json={
            "task": "PYTEST - Update test",
            "priority": "high",
            "category": "education"
        }
    )

    assert create_response.status_code in (200, 201)

    task_id = create_response.json()["task"]["id"]

    # Update its category
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "category": "testing"
        }
    )

    assert response.status_code == 200

    # Verify the update
    updated_response = client.get(f"/tasks/{task_id}")

    assert updated_response.status_code == 200

    updated_task = updated_response.json()["task"]

    assert updated_task["category"] == "testing"

    print("Updated task:", updated_task)


def test_update_nonexistent_task():
    """Updating an unknown task should return 404."""

    response = client.patch(
        "/tasks/999999",
        json={
            "category": "testing"
        }
    )

    assert response.status_code == 404
