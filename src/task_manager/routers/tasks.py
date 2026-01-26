from fastapi import APIRouter
from schemas import models
import database

task_routes = APIRouter()
Task = models.Task


@task_routes.get("/{task_id}", response_model=Task)
async def read_task(task_id: int):
    task_key = f"task_{task_id}"
    if task_key in database.DB:
        task_data = database.DB[task_key]
        return Task(**task_data)
    return {"error": "Task not found"}


@task_routes.post("/")
async def create_task(task: Task):
    new_id = database.NEXT_TASK_ID
    database.NEXT_TASK_ID += 1
    task_data = task.model_dump()
    task_data["id"] = new_id
    database.DB[f"task_{new_id}"] = task_data
    database.save()
    return Task(**task_data)


@task_routes.put("/{task_id}")
async def update_task(task_id: int, task: Task):
    if f"task_{task_id}" not in database.DB:
        return {"error": "Task not found"}
    task_data = task.model_dump()
    task_data["id"] = task_id
    database.DB[f"task_{task_id}"] = task_data
    database.save()
    return Task(**task_data)


@task_routes.delete("/{task_id}")
async def delete_task(task_id: int):
    if f"task_{task_id}" not in database.DB:
        return {"error": "Task not found"}
    del database.DB[f"task_{task_id}"]
    database.save()
    return {"message": "Task deleted successfully"}
