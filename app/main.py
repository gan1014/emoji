
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import logging
from datetime import date

from app.database import get_connection, initialize_database
from app.ollama_service import extract_task_details


# -----------------------------
# LOGGING
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------
# FASTAPI APPLICATION
# -----------------------------

app = FastAPI(
    title="AI TaskOps",
    description="AI-Powered Task Automation Platform",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    initialize_database()


# -----------------------------
# PYDANTIC MODELS
# -----------------------------

class TaskInput(BaseModel):
    task: str = Field(min_length=3, max_length=200)
    priority: Literal["low", "medium", "high"] = "medium"
    category: str = Field(default="general", min_length=2, max_length=50)
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    task: Optional[str] = Field(default=None, min_length=3, max_length=200)
    priority: Optional[Literal["low", "medium", "high"]] = None
    category: Optional[str] = Field(default=None, min_length=2, max_length=50)
    due_date: Optional[str] = None
    completed: Optional[bool] = None


class AIMessage(BaseModel):
    message: str = Field(min_length=5, max_length=1000)


# -----------------------------
# HELPER FUNCTION
# -----------------------------

def validate_due_date(due_date):
    if due_date is None:
        return None

    try:
        return date.fromisoformat(due_date).isoformat()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="Invalid due date. Use YYYY-MM-DD format."
        )


# -----------------------------
# HOME AND HEALTH
# -----------------------------

@app.get("/")
def home():
    return {"message": "Welcome to AI TaskOps!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# -----------------------------
# CREATE NORMAL TASK
# -----------------------------

@app.post("/tasks", status_code=201)
def create_task(task_data: TaskInput):

    connection = get_connection()

    try:
        due_date = validate_due_date(task_data.due_date)

        cursor = connection.execute(
            """
            INSERT INTO tasks (task, priority, category, due_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                task_data.task,
                task_data.priority,
                task_data.category,
                due_date
            )
        )

        connection.commit()

        task_id = cursor.lastrowid

        logger.info("Task created: ID %s", task_id)

        saved_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        return {"task": dict(saved_task)}

    except HTTPException:
        raise

    except Exception:
        logger.exception("Task creation failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to create task"
        )

    finally:
        connection.close()


# -----------------------------
# GET ALL TASKS
# -----------------------------

@app.get("/tasks")
def get_tasks():

    connection = get_connection()

    try:
        tasks = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

        return {
            "total": len(tasks),
            "tasks": [dict(task) for task in tasks]
        }

    except Exception:
        logger.exception("Unable to retrieve tasks")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve tasks"
        )

    finally:
        connection.close()


# -----------------------------
# GET TASK BY ID
# -----------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    connection = get_connection()

    try:
        task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return {"task": dict(task)}

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unable to retrieve task")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve task"
        )

    finally:
        connection.close()


# -----------------------------
# UPDATE TASK
# -----------------------------

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):

    connection = get_connection()

    try:
        update_data = task_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        if "due_date" in update_data:
            update_data["due_date"] = validate_due_date(
                update_data["due_date"]
            )

        if "completed" in update_data:
            update_data["completed"] = int(update_data["completed"])

        existing_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if existing_task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        allowed_fields = {
            "task",
            "priority",
            "category",
            "due_date",
            "completed"
        }

        fields = [
            field for field in update_data
            if field in allowed_fields
        ]

        set_clause = ", ".join(
            f"{field} = ?" for field in fields
        )

        values = [update_data[field] for field in fields]
        values.append(task_id)

        connection.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            values
        )

        connection.commit()

        updated_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        logger.info("Task updated: ID %s", task_id)

        return {"task": dict(updated_task)}

    except HTTPException:
        raise

    except Exception:
        logger.exception("Task update failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to update task"
        )

    finally:
        connection.close()


# -----------------------------
# DELETE TASK
# -----------------------------

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    connection = get_connection()

    try:
        existing_task = connection.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if existing_task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        connection.commit()

        logger.info("Task deleted: ID %s", task_id)

        return {
            "message": "Task deleted successfully",
            "task_id": task_id
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Task deletion failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to delete task"
        )

    finally:
        connection.close()


# -----------------------------
# AI TASK CREATION
# -----------------------------

@app.post("/tasks/ai", status_code=201)
def create_ai_task(ai_data: AIMessage):

    connection = None

    try:
        # Step 1: Extract task information using Ollama
        extracted_data = extract_task_details(ai_data.message)

        # Step 2: Validate extracted information
        validated_task = TaskInput(**extracted_data)

        due_date = validate_due_date(validated_task.due_date)

        # Step 3: Connect to SQLite
        connection = get_connection()

        # Step 4: Check for duplicate tasks
        duplicate = connection.execute(
            """
            SELECT id FROM tasks
            WHERE LOWER(TRIM(task)) = LOWER(TRIM(?))
            AND completed = 0
            AND created_at >= datetime('now', '-10 minutes')
            """,
            (validated_task.task,)
        ).fetchone()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=f"Duplicate task detected. Existing task ID: {duplicate['id']}"
            )

        # Step 5: Save task INCLUDING due_date
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                task,
                priority,
                category,
                due_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                validated_task.task,
                validated_task.priority,
                validated_task.category,
                due_date
            )
        )

        connection.commit()

        task_id = cursor.lastrowid

        logger.info("AI task created: ID %s", task_id)

        # Step 6: Return saved task
        saved_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        return {
            "message": "AI task created successfully!",
            "task_id": task_id,
            "extracted_data": dict(saved_task)
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("AI task creation failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to process AI task"
        )

    finally:
        if connection is not None:
            connection.close()
