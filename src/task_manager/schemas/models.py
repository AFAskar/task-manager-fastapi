from typing import Annotated, Literal
from pydantic import BaseModel, Field

DB = {}
NEXT_USER_ID = 1
STATUSES = Literal["pending", "in progress", "completed"]
ROLES = Literal["admin", "manager", "team member", "user"]


class User(BaseModel):
    id: int | None = None
    username: str
    role: ROLES = Field(default="user")
    full_name: str | None = None
    disabled: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserInDB(User):
    id: int
    hashed_password: str


class Task(BaseModel):
    id: int
    title: str = Field(
        title="Title of Task",
        min_length=3,
        max_length=100,
        regex="^[A-Z][a-zA-Z0-9 ]+$",
        description="Title must start with an uppercase letter and contain only alphanumeric characters and spaces.",
    )
    description: str | None = Field(
        default=None, title="Description of the task", max_length=300
    )
    priority: Literal["low", "medium", "high"] = "medium"
    status: STATUSES = Field(default="pending")
    assigned_to: str = "UnAssigned"
