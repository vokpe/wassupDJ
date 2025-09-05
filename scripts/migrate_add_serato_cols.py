import sqlite3, json

DB = "data/tracks.db"

def add_column_if_missing(cur, table, coldef):
    col = coldef.split()[0]
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    if col not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {coldef}")

def ensure_index(cur, name, sql):
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    have = {r[0] for r in cur.fetchall()}
    if name not in have:
        cur.execute(sql)

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Add new columns to tracks (no data loss)
    add_column_if_missing(cur, "tracks", "file_path TEXT")
    add_column_if_missing(cur, "tracks", "bpm_serato REAL")
    add_column_if_missing(cur, "tracks", "key_serato TEXT")
    add_column_if_missing(cur, "tracks", "bpm_tag REAL")
    add_column_if_missing(cur, "tracks", "key_tag TEXT")
    add_column_if_missing(cur, "tracks", "crate_names TEXT")

    # Helpful indexes
    ensure_index(cur, "idx_tracks_ta", "CREATE UNIQUE INDEX IF NOT EXISTS idx_tracks_ta ON tracks(title, artist)")
    ensure_index(cur, "idx_tracks_file_path", "CREATE INDEX IF NOT EXISTS idx_tracks_file_path ON tracks(file_path)")

    conn.commit()
    conn.close()
    print("✅ Migration complete: tracks table ready for Serato + tags")
    
if __name__ == "__main__":
    main()
