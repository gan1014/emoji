
from datetime import date, timedelta
import logging

from app.database import get_connection
from app.telegram_service import send_telegram_message

logger = logging.getLogger(__name__)


def get_tasks_due_today():
    """Fetch incomplete tasks due today."""

    today = date.today().isoformat()

    connection = get_connection()

    try:
        tasks = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE due_date = ?
            AND completed = 0
            ORDER BY priority DESC
            """,
            (today,)
        ).fetchall()

        return [dict(task) for task in tasks]

    finally:
        connection.close()


def get_tasks_due_tomorrow():
    """Fetch incomplete tasks due tomorrow."""

    tomorrow = (
        date.today() + timedelta(days=1)
    ).isoformat()

    connection = get_connection()

    try:
        tasks = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE due_date = ?
            AND completed = 0
            ORDER BY priority DESC
            """,
            (tomorrow,)
        ).fetchall()

        return [dict(task) for task in tasks]

    finally:
        connection.close()


def reminder_already_sent(task_id, reminder_date, reminder_type):
    """Check whether this reminder was already sent."""

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT id
            FROM reminder_logs
            WHERE task_id = ?
            AND reminder_date = ?
            AND reminder_type = ?
            """,
            (task_id, reminder_date, reminder_type)
        ).fetchone()

        return result is not None

    finally:
        connection.close()


def record_reminder_sent(task_id, reminder_date, reminder_type):
    """Save a successfully sent reminder in SQLite."""

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO reminder_logs
            (task_id, reminder_date, reminder_type)
            VALUES (?, ?, ?)
            """,
            (task_id, reminder_date, reminder_type)
        )

        connection.commit()

    finally:
        connection.close()


def format_reminder(task):
    """Create a readable Telegram reminder."""

    message = (
        "🔔 AI TaskOps Reminder\n\n"
        f"Task: {task['task']}\n"
        f"Priority: {task['priority'].upper()}\n"
        f"Category: {task['category']}\n"
        f"Due date: {task['due_date']}\n\n"
        "Don't forget to complete your task!"
    )

    return message


async def send_task_reminders(tasks, reminder_type):
    """Send reminders without repeating previously logged reminders."""

    if not tasks:
        print("No pending reminders found!")
        return 0

    sent_count = 0
    skipped_count = 0

    for task in tasks:

        task_id = task["id"]
        reminder_date = task["due_date"]

        # Check whether reminder was already sent
        if reminder_already_sent(
            task_id,
            reminder_date,
            reminder_type
        ):
            print(
                f"Reminder already sent for task ID: {task_id}. Skipping."
            )
            skipped_count += 1
            continue

        try:
            message = format_reminder(task)

            # Send Telegram message
            await send_telegram_message(message)

            # Record only after successful delivery
            record_reminder_sent(
                task_id,
                reminder_date,
                reminder_type
            )

            sent_count += 1

            print(
                f"Reminder sent successfully for task ID: {task_id}"
            )

        except Exception:
            logger.exception(
                "Failed to send reminder for task ID: %s",
                task_id
            )

    print(f"Total reminders sent: {sent_count}")
    print(f"Total reminders skipped: {skipped_count}")

    return sent_count


async def send_due_today_reminders():
    """Send reminders for tasks due today."""

    tasks = get_tasks_due_today()

    return await send_task_reminders(
        tasks,
        "due_today"
    )


async def send_due_tomorrow_reminders():
    """Send reminders for tasks due tomorrow."""

    tasks = get_tasks_due_tomorrow()

    return await send_task_reminders(
        tasks,
        "due_tomorrow"
    )
