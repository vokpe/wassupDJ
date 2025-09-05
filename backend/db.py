import sqlite3
from typing import List, Dict, Any

DB_PATH = "data/tracks.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def track_count() -> int:
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    conn.close()
    return n

def transition_count() -> int:
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]
    conn.close()
    return n

def recent_transitions(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            t1.title  AS prev,
            t2.title  AS nxt,
            tr.played_at
        FROM transitions tr
        JOIN tracks t1 ON tr.prev_track_id = t1.id
        JOIN tracks t2 ON tr.next_track_id = t2.id
        ORDER BY tr.id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
