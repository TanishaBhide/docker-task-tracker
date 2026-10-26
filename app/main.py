
import os
import time

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task Tracker API")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "tasksdb"),
    "user": os.getenv("DB_USER", "taskuser"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


@app.on_event("startup")
def initialize_database():
    # Retry briefly while PostgreSQL finishes starting.
    for attempt in range(15):
        try:
            with get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        completed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                """)
            return
        except psycopg.OperationalError:
            if attempt == 14:
                raise
            time.sleep(2)


class TaskCreate(BaseModel):
    title: str


@app.get("/")
def home():
    return {"message": "Task Tracker API is running!"}


@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/tasks")
def list_tasks():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id"
        ).fetchall()

    return [
        {"id": row[0], "title": row[1], "completed": row[2]}
        for row in rows
    ]


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) "
            "RETURNING id, title, completed",
            (task.title,),
        ).fetchone()

    return {"id": row[0], "title": row[1], "completed": row[2]}


@app.patch("/tasks/{task_id}")
def complete_task(task_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "UPDATE tasks SET completed = TRUE WHERE id = %s "
            "RETURNING id, title, completed",
            (task_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"id": row[0], "title": row[1], "completed": row[2]}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = %s", (task_id,)
        )

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted"}
