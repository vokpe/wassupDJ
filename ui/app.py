import requests, streamlit as st

st.set_page_config(page_title="wassupDJ", layout="centered")
st.title("wassupDJ - MVP")

now = st.text_input("Now Playing (type a track name for demo)", "Test Track")

with st.expander("Recent transitions"):
    try:
        r = requests.get("http://127.0.0.1:8000/recent", timeout=5).json()
        for row in r.get("recent", []):
            st.write(f"{row['prev']} → {row['nxt']}  {('('+row['played_at']+')') if row.get('played_at') else ''}")
    except Exception as e:
        st.warning(f"Could not load recent transitions: {e}")

if st.button("Get Suggestions"):
    try:
        resp = requests.get("http://127.0.0.1:8000/suggest", params={"now_playing": now}, timeout=5)
        data = resp.json()
        st.subheader(f"Now Playing: {data.get('now_playing')}")
        for i, s in enumerate(data.get("suggestions", []), 1):
            st.write(f"**{i}. {s['title']}** — {s['reason']}")
    except Exception as e:
        st.error(f"Backend not running? {e}")
else:
    st.caption("Start the backend (uvicorn) first, then click the button.")


