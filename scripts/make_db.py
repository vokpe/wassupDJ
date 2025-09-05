import sqlite3

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tracks (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  artist TEXT NOT NULL,
  file_path TEXT,
  bpm REAL,
  key_text TEXT,
  serato_key TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crates (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS track_crates (
  track_id INTEGER,
  crate_id INTEGER,
  PRIMARY KEY (track_id, crate_id),
  FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
  FOREIGN KEY (crate_id) REFERENCES crates(id) ON DELETE CASCADE
);

-- historical transitions derived from history: prev -> next within same set/time
CREATE TABLE IF NOT EXISTS transitions (
  id INTEGER PRIMARY KEY,
  prev_track_id INTEGER NOT NULL,
  next_track_id INTEGER NOT NULL,
  played_at TEXT, -- timestamp if available
  FOREIGN KEY (prev_track_id) REFERENCES tracks(id) ON DELETE CASCADE,
  FOREIGN KEY (next_track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

-- spotify enrichment
CREATE TABLE IF NOT EXISTS track_features (
  track_id INTEGER PRIMARY KEY,
  spotify_id TEXT,
  spotify_match_conf REAL,
  bpm REAL, key_num INTEGER, mode INTEGER,
  energy REAL, danceability REAL, valence REAL, loudness REAL,
  acousticness REAL, instrumentalness REAL, liveness REAL, speechiness REAL,
  tempo REAL,
  FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

-- suggestion logs / feedback
CREATE TABLE IF NOT EXISTS suggestion_log (
  id INTEGER PRIMARY KEY,
  now_track_id INTEGER,
  candidate_track_id INTEGER,
  score REAL,
  reason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY,
  now_track_id INTEGER,
  chosen_track_id INTEGER,
  accepted INTEGER,  -- 1 accept, 0 skip
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def main():
  conn = sqlite3.connect("data/tracks.db")
  conn.executescript(SCHEMA)
  conn.commit()
  conn.close()
  print("✅ created data/tracks.db with schema")

if __name__ == "__main__":
  main()
