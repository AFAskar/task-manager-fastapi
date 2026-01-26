from fastapi import APIRouter
from schemas import models

task_routes = APIRouter()
Task = models.Task
User = models.User
MockDB = models.DB


@task_routes.get("/{task_id}", response_model=Task)
async def read_task():
    pass


@task_routes.post("/")
async def create_task(task: Task):
    pass


@task_routes.put("/{task_id}")
async def update_task(task_id: int, task: Task):
    pass


@task_routes.delete("/{task_id}")
async def delete_task(task_id: int):
    pass


async def get_tasks_for_user(username: str):
    pass
