import os
import psycopg
from psycopg.rows import dict_row

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

async def get_db_connection():
    """Establish and return an asynchronous connection to the PostgreSQL database."""
    try:
        conn = await psycopg.AsyncConnection.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            row_factory=dict_row
        )
        return conn
    except psycopg.OperationalError as e:
        print(f"Error connecting to database: {e}")
        raise

async def init_db():
    """Initialize the database tables if they do not exist."""
    conn = None
    try:
        conn = await get_db_connection()
        async with conn:
            async with conn.cursor() as cur:
                # Create Users Table
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        role VARCHAR(20) DEFAULT 'user',
                        disabled BOOLEAN DEFAULT FALSE,
                        hashed_password VARCHAR NOT NULL
                    );
                """)
                
                # Create Tasks Table
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(100) NOT NULL,
                        description VARCHAR(300),
                        priority VARCHAR(10) DEFAULT 'medium',
                        status VARCHAR(20) DEFAULT 'pending',
                        assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL
                    );
                """)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
    finally:
        if conn:
            await conn.close()
