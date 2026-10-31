
import pytest

from app import database


@pytest.fixture(autouse=True)
def isolate_test_database(tmp_path, monkeypatch):
    """Give every test its own temporary SQLite database."""

    test_database_path = tmp_path / "test_tasks.db"

    # Replace the real database path during this test
    monkeypatch.setattr(
        database,
        "DB_PATH",
        test_database_path
    )

    # Create tables in the temporary database
    database.initialize_database()

    yield
