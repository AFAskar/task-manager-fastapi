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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token") # Updated tokenUrl to match full path if needed, or keeping it relative
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


async def get_user(user_id: int | str | None):
    if user_id is None:
        return None
    try:
        conn = await database.get_db_connection()
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users WHERE id = %s", (int(user_id),))
                row = await cur.fetchone()
                if row:
                    return UserInDB(**row)
    except Exception as e:
        print(f"Error getting user: {e}")
    return None


async def get_user_by_username(username: str) -> UserInDB | None:
    try:
        conn = await database.get_db_connection()
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = await cur.fetchone()
                if row:
                    return UserInDB(**row)
    except Exception as e:
        print(f"Error getting user by username: {e}")
    return None


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
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
    
    # user_id in token 'sub' is actually the ID as string in previous code, 
    # but let's check login_for_access_token used user.id.
    user = await get_user(user_id=token_data.username) 
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
    user = await authenticate_user(form_data.username, form_data.password)
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
async def create_user(user: UserCreate) -> User:
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            # Check if username exists
            await cur.execute("SELECT 1 FROM users WHERE username = %s", (user.username,))
            if await cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already registered")
            
            hashed_password = get_password_hash(user.password)
            
            # Insert new user
            await cur.execute(
                """
                INSERT INTO users (username, role, disabled, hashed_password)
                VALUES (%s, %s, %s, %s)
                RETURNING id, username, role, disabled, hashed_password
                """,
                (user.username, user.role, user.disabled, hashed_password)
            )
            new_user_data = await cur.fetchone()
            await conn.commit()
            
            return UserInDB(**new_user_data)


@user_routes.get("/", response_model=list[User])
async def read_users() -> list[User]:
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users")
            rows = await cur.fetchall()
            return [UserInDB(**row) for row in rows]


@user_routes.get("/{user_id}/tasks", response_model=list[Task])
async def read_user_tasks(user_id: int) -> list[Task]:
    conn = await database.get_db_connection()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM tasks WHERE assigned_to = %s", (user_id,))
            rows = await cur.fetchall()
            return [Task(**row) for row in rows]
