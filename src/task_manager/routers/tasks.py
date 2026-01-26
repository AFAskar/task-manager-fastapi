from fastapi import APIRouter
from schemas import models

task_routes = APIRouter()
Task = models.Task
User = models.User
MockDB = models.DB

@task_routes.get("/{task_id}", response_model=Task)
async def read_task():