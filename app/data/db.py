import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    from pathlib import Path

    db_path = Path(db_path)
    # Ensure parent directory exists
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    # Ensure foreign key constraints are enforced
    conn.execute("PRAGMA foreign_keys = ON;")
    return sqlite3.connect(str(db_path))