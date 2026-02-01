from fastapi import APIRouter, HTTPException
from task_manager.schemas import models
from task_manager import database


task_routes = APIRouter()
Task = models.Task


@task_routes.get("/{task_id}", response_model=Task)
async def read_task(task_id: int):
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task_data = await cur.fetchone()
            if task_data:
                return Task(**task_data)
    raise HTTPException(status_code=404, detail="Task not found")


@task_routes.get("/", response_model=list[Task])
async def read_tasks():
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM tasks")
            rows = await cur.fetchall()
            return [Task(**row) for row in rows]


@task_routes.post("/")
async def create_task(task: Task) -> Task:
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO tasks (title, description, priority, status, assigned_to)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, title, description, priority, status, assigned_to
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.status,
                    task.assigned_to,
                ),
            )
            new_task_data = await cur.fetchone()
            await conn.commit()
            return Task(**new_task_data)


@task_routes.put("/{task_id}")
async def update_task(task_id: int, task: Task) -> Task:
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            # Check if task exists first (optional, but good for returning 404 vs 500)
            # Actually UPDATE RETURNING works too
            await cur.execute(
                """
                UPDATE tasks
                SET title = %s, description = %s, priority = %s, status = %s, assigned_to = %s
                WHERE id = %s
                RETURNING id, title, description, priority, status, assigned_to
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.status,
                    task.assigned_to,
                    task_id,
                ),
            )
            updated_task_data = await cur.fetchone()
            await conn.commit()

            if updated_task_data:
                return Task(**updated_task_data)
    raise HTTPException(status_code=404, detail="Task not found")


@task_routes.delete("/{task_id}")
async def delete_task(task_id: int) -> dict[str, str]:
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,)
            )
            deleted = await cur.fetchone()
            await conn.commit()

            if deleted:
                return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")
