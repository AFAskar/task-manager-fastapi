import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from task_manager.routers import users, tasks
from task_manager import database

reqs = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "DB_HOST", "DB_PORT"]

if os.environ.get("ENV") == "production":
    if os.environ.get("constring"):
        pass
    missing = [r for r in reqs if r not in os.environ]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables for production: {', '.join(missing)}"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(users.user_routes, prefix="/users", tags=["users"])
app.include_router(tasks.task_routes, prefix="/tasks", tags=["tasks"])


@app.get("/")
def read_root():
    return FileResponse(static_path / "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}
