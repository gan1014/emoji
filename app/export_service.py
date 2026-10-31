
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.database import get_connection


# Project and export directories
BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


def get_all_tasks():
    """Fetch all tasks from SQLite."""

    connection = get_connection()

    try:
        tasks = connection.execute(
            """
            SELECT *
            FROM tasks
            ORDER BY created_at DESC
            """
        ).fetchall()

        return [dict(task) for task in tasks]

    finally:
        connection.close()


def export_tasks_to_excel():
    """Generate a formatted Excel report of all tasks."""

    tasks = get_all_tasks()

    workbook = Workbook()

    # -------------------------------
    # Tasks worksheet
    # -------------------------------

    worksheet = workbook.active
    worksheet.title = "Tasks"

    headers = [
        "ID",
        "Task",
        "Priority",
        "Category",
        "Due Date",
        "Status",
        "Created At"
    ]

    worksheet.append(headers)

    # Header styling
    header_fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78"
    )

    header_font = Font(
        bold=True,
        color="FFFFFF",
        size=11
    )

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # Add task records
    for task in tasks:

        status = (
            "Completed"
            if task["completed"]
            else "Pending"
        )

        worksheet.append([
            task["id"],
            task["task"],
            task["priority"].upper(),
            task["category"],
            task["due_date"] or "Not assigned",
            status,
            task["created_at"]
        ])

    # Column widths
    column_widths = {
        "A": 10,
        "B": 42,
        "C": 15,
        "D": 18,
        "E": 18,
        "F": 15,
        "G": 23
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    # Make task text easier to read
    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True
            )

    # Table usability
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    worksheet.row_dimensions[1].height = 25

    # -------------------------------
    # Summary worksheet
    # -------------------------------

    summary = workbook.create_sheet("Summary")

    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks if task["completed"]
    )

    pending_tasks = total_tasks - completed_tasks

    today = date.today().isoformat()

    overdue_tasks = sum(
        1
        for task in tasks
        if (
            task["due_date"]
            and task["due_date"] < today
            and not task["completed"]
        )
    )

    summary.append(["AI TaskOps - Task Summary"])
    summary.append([])
    summary.append(["Metric", "Count"])

    summary_data = [
        ["Total Tasks", total_tasks],
        ["Completed Tasks", completed_tasks],
        ["Pending Tasks", pending_tasks],
        ["Overdue Tasks", overdue_tasks]
    ]

    for item in summary_data:
        summary.append(item)

    # Summary styling
    summary["A1"].font = Font(
        bold=True,
        size=16,
        color="1F4E78"
    )

    for cell in summary[3]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center"
        )

    for row in summary.iter_rows(min_row=4):
        for cell in row:
            cell.font = Font(size=11)

    summary.column_dimensions["A"].width = 25
    summary.column_dimensions["B"].width = 18

    summary.append([])
    summary.append([
        "Report Generated",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    # -------------------------------
    # Save Excel report
    # -------------------------------

    filename = (
        "tasks_export_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".xlsx"
    )

    file_path = EXPORT_DIR / filename

    workbook.save(file_path)

    print("Excel report generated successfully!")
    print(f"Total tasks exported: {total_tasks}")
    print(f"File location: {file_path}")

    return str(file_path)
