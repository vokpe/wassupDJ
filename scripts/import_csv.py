import csv, sqlite3, pathlib, io

DB = "data/tracks.db"

def sniff_delimiter(sample_bytes: bytes, default=","):
    try:
        sample = sample_bytes.decode("utf-8", errors="ignore")
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample, delimiters=[",",";","\t","|"])
        return dialect.delimiter
    except Exception:
        return default

def open_dict_reader(path):
    # read a small sample to sniff delimiter
    with open(path, "rb") as fb:
        sample = fb.read(4096)
    delim = sniff_delimiter(sample)
    # reopen text mode with utf-8 & ignore bad bytes
    f = open(path, newline="", encoding="utf-8", errors="ignore")
    return csv.DictReader(f, delimiter=delim), f, delim

def normalize_row(r):
    # lowercased keys → values stripped
    rl = { (k or "").strip().lower(): (v or "").strip() for k,v in r.items() }

    def pick(*keys):
        for k in keys:
            if k.lower() in rl and rl[k.lower()]:
                return rl[k.lower()]
        return ""

    title = pick("title","name","track","song")
    artist = pick("artist","artists")
    bpm = pick("bpm","tempo")
    key_text = pick("key","serato key","musical key")
    played_at = pick("played","date","start time","time","played at","start time/date")

    try:
        bpm_val = float(bpm) if bpm else None
    except ValueError:
        bpm_val = None

    return {
        "title": title,
        "artist": artist,
        "bpm": bpm_val,
        "key_text": key_text or None,
        "played_at": played_at or None,
    }

def ensure_unique_index(cur):
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tracks_ta ON tracks(title, artist)")

def upsert_track(cur, title, artist, bpm=None, key_text=None):
    # requires unique index on (title, artist)
    cur.execute("""
      INSERT INTO tracks (title, artist, bpm, key_text)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(title, artist) DO UPDATE SET
        bpm=COALESCE(excluded.bpm, bpm),
        key_text=COALESCE(excluded.key_text, key_text)
    """, (title, artist, bpm, key_text))
    cur.execute("SELECT id FROM tracks WHERE title=? AND artist=?", (title, artist))
    row = cur.fetchone()
    return row[0] if row else None

def import_library(csv_path):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    ensure_unique_index(cur)
    conn.commit()

    reader, fh, delim = open_dict_reader(csv_path)
    print(f"→ importing library {csv_path} (delimiter='{delim}', cols={reader.fieldnames})")

    added = 0
    for raw in reader:
        row = normalize_row(raw)
        if not row["title"] or not row["artist"]:
            continue
        tid = upsert_track(cur, row["title"], row["artist"], row["bpm"], row["key_text"])
        if tid:
            added += 1

    conn.commit()
    conn.close()
    fh.close()
    print(f"✅ library import done: {csv_path} (tracks upserted: {added})")

def import_history(csv_path):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    ensure_unique_index(cur)
    conn.commit()

    reader, fh, delim = open_dict_reader(csv_path)
    print(f"→ importing history {csv_path} (delimiter='{delim}', cols={reader.fieldnames})")

    processed = 0
    transitions = 0
    prev_id = None

    for raw in reader:
        row = normalize_row(raw)
        if not row["title"] or not row["artist"]:
            continue
        tid = upsert_track(cur, row["title"], row["artist"], row["bpm"], row["key_text"])
        if tid is None:
            continue
        if prev_id is not None and prev_id != tid:
            cur.execute("""
              INSERT INTO transitions (prev_track_id, next_track_id, played_at)
              VALUES (?, ?, ?)
            """, (prev_id, tid, row["played_at"]))
            transitions += 1
        prev_id = tid
        processed += 1

    conn.commit()
    conn.close()
    fh.close()
    print(f"✅ history import done: {csv_path} (rows: {processed}, transitions: {transitions})")

if __name__ == "__main__":
    import argparse, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", type=pathlib.Path)
    ap.add_argument("--history", type=pathlib.Path)
    args = ap.parse_args()
    if args.library:
        import_library(str(args.library))
    if args.history:
        import_history(str(args.history))