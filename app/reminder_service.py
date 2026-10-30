from app.database import get_connection
from datetime import date


def get_tasks_due_tomorrow():

    from datetime import timedelta

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    connection = get_connection()

    try:
        tasks = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE due_date = ?
            AND completed = 0
            """,
            (tomorrow,)
        ).fetchall()

        return [dict(task) for task in tasks]

    finally:
        connection.close()