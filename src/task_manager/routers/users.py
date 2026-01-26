from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas import models
import database

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


user_routes = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
User = models.User
UserCreate = models.UserCreate
UserInDB = models.UserInDB
TokenData = models.TokenData
Token = models.Token
Task = models.Task
password_hash = PasswordHash.recommended()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(mock_db, user_id: int | str | None):
    if user_id is None:
        return None
    key = f"user_{user_id}"
    if key in mock_db:
        user_dict = mock_db[key]
        return UserInDB(**user_dict)
    return None


def get_user_by_username(mock_db, username: str):
    for entry in mock_db.values():
        # Check if entry is a user (has username field)
        if entry.get("username") == username:
            return UserInDB(**entry)
    return None


def authenticate_user(mock_db, username: str, password: str):
    user = get_user_by_username(mock_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(username=user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(database.DB, user_id=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@user_routes.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(database.DB, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@user_routes.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@user_routes.post("/", response_model=User)
async def create_user(user: UserCreate):
    # ensure username is unique across DB entries
    for v in database.DB.values():
        if v.get("username", "").lower() == user.username.lower():
            raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_id = database.NEXT_USER_ID
    database.NEXT_USER_ID += 1
    
    user_data = user.model_dump()
    if "password" in user_data:
        del user_data["password"]
    
    user_data["id"] = new_id
    user_in_db = UserInDB(**user_data, hashed_password=hashed_password)
    database.DB[f"user_{new_id}"] = user_in_db.model_dump()
    database.save()
    return User(**user_in_db.model_dump())


@user_routes.get("/{user_id}/tasks", response_model=list[Task])
async def read_user_tasks(user_id: int):
    user_tasks = []
    for task_key, task_data in database.DB.items():
        if task_data.get("assigned_to") == f"user_{user_id}":
            user_tasks.append(Task(**task_data))
    return user_tasks
