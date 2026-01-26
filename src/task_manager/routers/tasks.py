from fastapi import APIRouter
from schemas import models
import database

task_routes = APIRouter()
Task = models.Task


@task_routes.get("/{task_id}", response_model=Task)
async def read_task(task_id: int):
    task_key = str(task_id)
    if task_key in database.DB["tasks"]:
        task_data = database.DB["tasks"][task_key]
        return Task(**task_data)
    return {"error": "Task not found"}


@task_routes.get("/", response_model=list[Task])
async def read_tasks():
    all_tasks = []
    for task_data in database.DB["tasks"].values():
        all_tasks.append(Task(**task_data))
    return all_tasks


@task_routes.post("/")
async def create_task(task: Task)->Task:
    new_id = database.NEXT_TASK_ID
    database.NEXT_TASK_ID += 1
    task_data = task.model_dump()
    task_data["id"] = new_id
    database.DB["tasks"][str(new_id)] = task_data
    database.save()
    return Task(**task_data)


@task_routes.put("/{task_id}")
async def update_task(task_id: int, task: Task)->Task:
    task_key = str(task_id)
    if task_key not in database.DB["tasks"]:
        return {"error": "Task not found"}
    task_data = task.model_dump()
    task_data["id"] = task_id
    database.DB["tasks"][task_key] = task_data
    database.save()
    return Task(**task_data)


@task_routes.delete("/{task_id}")
async def delete_task(task_id: int)->dict[str,str]:
    task_key = str(task_id)
    if task_key not in database.DB["tasks"]:
        return {"error": "Task not found"}
    del database.DB["tasks"][task_key]
    database.save()
    return {"message": "Task deleted successfully"}
