# 🎧 wassupDJ (MVP Skeleton)

Goal: **Session-aware DJ next-track suggester**  
(Harmonic + tempo + vibe) using **Serato history** + **Spotify audio features**

---

## ✅ Day 1 Status
- FastAPI backend skeleton (`/health`, `/suggest`)
- Streamlit UI skeleton calling backend
- Virtualenv + requirements
- Repo structure in place

---

## ✅ Day 2 Status
- **SQLite ingestion pipeline**
  - `scan_library.py` → scans music library/flash drive, extracts tags (title, artist, BPM/key if present)  
  - Skips junk files (AppleDouble `._*`) + logs unreadables  
  - Successfully ingested sample tracks into `data/tracks.db`
- **Schema migration ready for Serato integration**
  - Added `file_path`, `bpm_serato`, `key_serato`, `bpm_tag`, `key_tag`, `crate_names` columns
- **Verification**
  - `queries/verify_flashdrive.sql` for quick DB checks (counts, samples, transitions)
- **Backend API**
  - `/health` → DB status + track/transition counts
  - `/counts` → totals
  - `/recent` → last N transitions from Serato history
- **UI**
  - Streamlit panel shows recent transitions (live data from backend)

---

## 📂 Project Structure

```text
wassupDJ/
├── backend/                        # Backend API (FastAPI)
│   ├── __init__.py
│   ├── main.py                     # FastAPI app + routes (/health, /counts, /recent)
│   └── db.py                       # SQLite helpers (connect, queries)
│
├── data/                           # Local data storage
│   └── tracks.db                   # SQLite database (autocreated/updated)
│
├── queries/                        # SQL utilities for debugging
│   └── verify_flashdrive.sql
│
├── scripts/                        # Ingestion + migration scripts
│   ├── scan_library.py             # Scan flash drive / music folder → insert into DB
│   ├── migrate_add_serato_cols.py  # Adds Serato-ready columns (bpm_serato, key_serato, crates, etc.)
│   └── import_csv.py               # Import Serato history CSVs
│
├── ui/                             # Streamlit frontend
│   └── app.py                      # Streamlit UI (shows transitions, future suggester UI)
│
└── README.md                       # Project docs
```
---
## 📊 Database
- `data/tracks.db` is created locally by running:
  ```bash
  python scripts/scan_library.py --root "/path/to/music"
  python scripts/import_csv.py --file path/to/history.csv
---
## ▶ Run Locally

#### Terminal 1: Backend

source .venv/bin/activate
uvicorn backend.main:app --reload
Runs on http://127.0.0.1:8000

### Terminal 2: UI
bash
Copy code
source .venv/bin/activate
streamlit run ui/app.py
Runs on http://localhost:8501

---
## 🔍 Verify DB
open verify_flashdrive.sql in VS Code and run with the SQLite extension.

---

## 🚀 Roadmap

Day 3: Spotify enrichment (track_features table, fetch tempo/energy/danceability/valence/key via Spotipy)

Day 4: First suggest() (harmonic mixing, tempo matching, novelty scoring)

Day 5+: Crate-aware suggestions, advanced scoring, optional Serato parser integration
