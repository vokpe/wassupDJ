from fastapi import FastAPI, Query
from . import db

app = FastAPI(title="wassupDJ API")

@app.get("/health")
def health():
    # also return simple DB stats so we know DB is reachable
    try:
        return {"status": "ok", "tracks": db.track_count(), "transitions": db.transition_count()}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

@app.get("/recent")
def recent(limit: int = Query(10, ge=1, le=100)):
    return {"recent": db.recent_transitions(limit)}

@app.get("/counts")
def counts():
    return {"tracks": db.track_count(), "transitions": db.transition_count()}
