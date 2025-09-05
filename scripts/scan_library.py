import argparse
import os
import sqlite3
from pathlib import Path
from typing import Optional

from mutagen import File as MutagenFile

DB = "data/tracks.db"
AUDIO_EXTS = {".mp3", ".m4a", ".aac", ".wav", ".aiff", ".aif", ".flac", ".ogg", ".oga", ".m4b", ".alac"}


def ensure_unique_index(cur):
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tracks_ta ON tracks(title, artist)")


def get_tag(tags, *keys, default=None) -> Optional[str]:
    """Try multiple keys across formats, return first non-empty string."""
    for k in keys:
        if k in tags and tags[k]:
            v = tags[k]
            # Mutagen sometimes returns lists
            if isinstance(v, (list, tuple)):
                v = v[0] if v else ""
            v = str(v).strip()
            if v:
                return v
    return default


def read_audio_tags(path: Path):
    # Skip tiny or hidden/system files fast
    try:
        if path.name.startswith(".") or path.stat().st_size < 1024:  # <1KB
            return None
    except Exception:
        return None

    try:
        audio = MutagenFile(path, easy=True)
    except Exception:
        # unreadable / wrong container / corrupt
        return None

    if audio is None:
        return None

    tags = getattr(audio, "tags", {}) or {}

    def first(tags, *keys):
        for k in keys:
            if k in tags and tags[k]:
                v = tags[k]
                if isinstance(v, (list, tuple)):
                    v = v[0] if v else ""
                v = str(v).strip()
                if v:
                    return v
        return ""

    title  = first(tags, "title", "©nam")
    artist = first(tags, "artist", "©ART", "albumartist", "performer")
    bpm_str = first(tags, "bpm", "TBPM")
    key     = first(tags, "initialkey", "TKEY", "key")

    bpm = None
    if bpm_str:
        try:
            bpm = float(bpm_str)
        except ValueError:
            digits = "".join(ch for ch in bpm_str if (ch.isdigit() or ch == "."))
            try:
                bpm = float(digits) if digits else None
            except Exception:
                bpm = None

    if not title or not artist:
        return None

    return {"title": title, "artist": artist, "bpm": bpm, "key_text": key or None}



def upsert_track(cur, title, artist, file_path=None, bpm=None, key_text=None):
    cur.execute("""
      INSERT INTO tracks (title, artist, file_path, bpm, key_text)
      VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(title, artist) DO UPDATE SET
        file_path=COALESCE(excluded.file_path, file_path),
        bpm=COALESCE(excluded.bpm, bpm),
        key_text=COALESCE(excluded.key_text, key_text)
    """, (title, artist, str(file_path) if file_path else None, bpm, key_text))
    cur.execute("SELECT id FROM tracks WHERE title=? AND artist=?", (title, artist))
    row = cur.fetchone()
    return row[0] if row else None


def scan(root: Path, dry_run=False, limit=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # Add columns if your current schema doesn't yet have file_path
    cur.execute("PRAGMA table_info(tracks)")
    cols = {row[1] for row in cur.fetchall()}
    if "file_path" not in cols:
        cur.execute("ALTER TABLE tracks ADD COLUMN file_path TEXT")
    ensure_unique_index(cur)
    conn.commit()

    count_seen = 0
    count_added = 0
    bad = 0
    bad_samples = []

    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            if limit and count_seen >= limit:
                break
            p = Path(dirpath) / name
            if p.suffix.lower() not in AUDIO_EXTS:
                continue
            
            if name.startswith("._"):
                continue

            count_seen += 1
            meta = read_audio_tags(p)
            if not meta:
                bad += 1
                if len(bad_samples) < 5:
                    bad_samples.append(str(p))
                continue

            title = meta["title"]
            artist = meta["artist"]
            if not dry_run:
                tid = upsert_track(cur, title, artist, file_path=p, bpm=meta["bpm"], key_text=meta["key_text"])
                if tid:
                    count_added += 1

    if not dry_run:
        conn.commit()
    conn.close()

    print(f"✅ scanned {count_seen} files, upserted {count_added} tracks")
    if bad > 0:
        print(f"Skipped unreadable/unsupported files: {bad}")
        if bad_samples:
            print("Examples:")
            for s in bad_samples:
                print("  -", s)

    return count_seen, count_added



def main():
    ap = argparse.ArgumentParser(description="Scan a folder for audio files and import tags into SQLite.")
    ap.add_argument("--root", type=str, required=True, help="Root folder to scan (e.g., /Users/you/Music)")
    ap.add_argument("--limit", type=int, default=None, help="Optional max files to process (for testing)")
    ap.add_argument("--dry-run", action="store_true", help="Parse and report only; do not write to DB")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Root folder not found: {root}")
        return

    seen, added = scan(root, dry_run=args.dry_run, limit=args.limit)
    mode = "(dry run)" if args.dry_run else ""
    print(f"✅ scanned {seen} files, upserted {added} tracks {mode}")

if __name__ == "__main__":
    main()
