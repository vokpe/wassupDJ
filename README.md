# wassupDJ (MVP Skeleton)

Goal: Session-aware DJ next-track suggester (harmonic + tempo + vibe) using Serato history + Spotify audio features.

## Day 1 Status
- ✅ FastAPI backend skeleton (`/health`, `/suggest`)
- ✅ Streamlit UI skeleton calling backend
- ✅ Virtualenv + requirements
- ✅ Repo structure in place

## Run Locally
```bash
# Terminal 1
uvicorn backend.main:app --reload

# Terminal 2
streamlit run ui/app.py

