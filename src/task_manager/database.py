
"""
This module holds the in-memory database and global counters, persisted to a JSON file.
"""
import json
from pathlib import Path

# Path to the JSON database file
DB_FILE = Path(__file__).parent / "db.json"

# In-memory database with valid tables
DB = {
    "users": {},
    "tasks": {}
}

# Global counters for IDs
NEXT_USER_ID = 1
NEXT_TASK_ID = 1


def save():
    """Save the current state of DB and counters to the JSON file."""
    data = {
        "DB": DB,
        "NEXT_USER_ID": NEXT_USER_ID,
        "NEXT_TASK_ID": NEXT_TASK_ID
    }
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving database: {e}")


def load():
    """Load the state from the JSON file into memory."""
    global DB, NEXT_USER_ID, NEXT_TASK_ID
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                DB = data.get("DB", {"users": {}, "tasks": {}})
                NEXT_USER_ID = data.get("NEXT_USER_ID", 1)
                NEXT_TASK_ID = data.get("NEXT_TASK_ID", 1)

        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading database: {e}")

# Load data immediately upon module import
load()
