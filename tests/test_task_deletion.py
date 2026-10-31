
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_delete_existing_task():
    """Create a test task, delete it, and verify deletion."""

    # Create a temporary test task
    create_response = client.post(
        "/tasks",
        json={
            "task": "PYTEST - Delete test",
            "priority": "low",
            "category": "testing"
        }
    )

    assert create_response.status_code in (200, 201)

    task_id = create_response.json()["task"]["id"]

    # Delete the task
    delete_response = client.delete(f"/tasks/{task_id}")

    assert delete_response.status_code == 200

    # Verify that the task no longer exists
    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 404

    print(f"Task {task_id} deleted successfully!")


def test_delete_nonexistent_task():
    """Deleting an unknown task should return 404."""

    response = client.delete("/tasks/999999")

    assert response.status_code == 404
