from typing import Annotated, Literal
from pydantic import BaseModel, Field, field_validator

DB = {}
NEXT_USER_ID = 1
NEXT_TASK_ID = 1
STATUSES = Literal["pending", "in progress", "completed"]
ROLES = Literal["admin", "manager", "team member", "user"]
PRIORITIES = Literal["low", "medium", "high"]

class User(BaseModel):
    id: Annotated[int | None, Field(default=None)]
    username: Annotated[str, Field(
        title="Username",
        min_length=3,
        max_length=100,
    )]
    role:Annotated[ROLES, Field(default="user")]
    disabled: Annotated[bool | None, Field(default=None)]


class Token(BaseModel):
    access_token: Annotated[str, Field(title="Access Token")]
    token_type: Annotated[str, Field(title="Token Type")]


class TokenData(BaseModel):
    username: Annotated[str | None, Field(default=None)]


class UserInDB(User):
    id: Annotated[int | None, Field(default=None)]
    hashed_password: Annotated[str | None, Field(default=None)]


class Task(BaseModel):
    id: Annotated[int | None, Field(default=None)]
    title: Annotated[str, Field(
        title="Title of Task",
        min_length=3,
        max_length=100,
        description="Title must start with an uppercase letter and contain only alphanumeric characters and spaces.",
    )]
    description: Annotated[str | None, Field(
        default=None, title="Description of the task", max_length=300
    )]
    priority: Annotated[PRIORITIES, Field(default="medium")]
    status:Annotated[STATUSES, Field(default="pending")]
    assigned_to: Annotated[str | None, Field(default="UnAssigned")]

    @field_validator("title")
    def title_must_be_capitalized(cls, v: str) -> str:
        if not v[0].isupper():
            raise ValueError("Title must start with an uppercase letter")
        return v
