
import os, sqlite3
from contextlib import closing

def mask_text(text: str, keep: int = 400) -> str:
    if len(text) <= keep:
        return text
    return text[:keep] + "… (truncated)"

def ensure_db(db_path: str):
    with closing(sqlite3.connect(db_path)) as conn, closing(conn.cursor()) as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, symptoms TEXT, response_json TEXT)"
        )
        conn.commit()
