import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "tasks.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                category TEXT NOT NULL DEFAULT 'general',
                due_date TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = connection.execute(
            "PRAGMA table_info(tasks)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "due_date" not in column_names:
            connection.execute(
                "ALTER TABLE tasks ADD COLUMN due_date TEXT"
            )

        connection.commit()
        print("SQLite database initialized successfully!")

    finally:
        connection.close()