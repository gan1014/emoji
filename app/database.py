
import sqlite3
from pathlib import Path


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database file
DB_PATH = DATA_DIR / "tasks.db"


def get_connection():
    """Create and return a SQLite database connection."""

    connection = sqlite3.connect(DB_PATH)

    # Return database rows as dictionary-like objects
    connection.row_factory = sqlite3.Row

    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create database tables and update the schema when required."""

    connection = get_connection()

    try:
        # Create tasks table
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

        # Check existing task table columns
        columns = connection.execute(
            "PRAGMA table_info(tasks)"
        ).fetchall()

        column_names = [
            column["name"] for column in columns
        ]

        # Add due_date if it does not already exist
        if "due_date" not in column_names:
            connection.execute(
                "ALTER TABLE tasks ADD COLUMN due_date TEXT"
            )

        # Create reminder_logs table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reminder_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                reminder_date TEXT NOT NULL,
                reminder_type TEXT NOT NULL,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(task_id, reminder_date, reminder_type),

                FOREIGN KEY(task_id)
                    REFERENCES tasks(id)
                    ON DELETE CASCADE
            )
        """)

        connection.commit()

        print("SQLite database initialized successfully!")
        print("Tasks table is ready!")
        print("Reminder logs table is ready!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
