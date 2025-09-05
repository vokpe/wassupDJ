from fastapi import FastAPI

app = FastAPI(title="wassupDJ")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/suggest")
def suggest(now_playing: str = "UNKNOWN"):
    # Day 4+ will return real suggestions. For now, a stub.
    return {
        "now_playing": now_playing,
        "suggestions": [
            {"title": "Stub Track 1", "reason": "baseline demo"},
            {"title": "Stub Track 2", "reason": "baseline demo"},
            {"title": "Stub Track 3", "reason": "baseline demo"},
        ],
    }
