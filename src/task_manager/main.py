from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from routers import users, tasks

app = FastAPI()

static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(users.user_routes, prefix="/users", tags=["users"])
app.include_router(tasks.task_routes, prefix="/tasks", tags=["tasks"])


@app.get("/")
def read_root():
    return FileResponse(static_path / "index.html")
