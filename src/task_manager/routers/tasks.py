from fastapi import APIRouter
from schemas import models

task_routes = APIRouter()
Task = models.Task
User = models.User
MockDB = models.DB


@task_routes.get("/{task_id}", response_model=Task)
async def read_task(task_id: int):
    task_key = f"task_{task_id}"
    if task_key in MockDB:
        task_data = MockDB[task_key]
        return Task(**task_data)
    return {"error": "Task not found"}


@task_routes.post("/")
async def create_task(task: Task):
    new_id = models.NEXT_TASK_ID
    task_data = task.model_dump()
    task_data["id"] = new_id
    MockDB[f"task_{new_id}"] = task_data
    return Task(**task_data)


@task_routes.put("/{task_id}")
async def update_task(task_id: int, task: Task):
    if f"task_{task_id}" not in MockDB:
        return {"error": "Task not found"}
    task_data = task.model_dump()
    task_data["id"] = task_id
    MockDB[f"task_{task_id}"] = task_data
    return Task(**task_data)


@task_routes.delete("/{task_id}")
async def delete_task(task_id: int):
    if f"task_{task_id}" not in MockDB:
        return {"error": "Task not found"}
    del MockDB[f"task_{task_id}"]
    return {"message": "Task deleted successfully"}
