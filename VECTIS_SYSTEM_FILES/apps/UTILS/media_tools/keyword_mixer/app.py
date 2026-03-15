import streamlit as st
import random
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="Keyword Mixer", page_icon="🧬")
st.title("🧬 Keyword Mixer [Rank 23]")

KW_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../AUTO_YOUTUBE/MY_KEYWORDS.txt"))
keywords = []
if os.path.exists(KW_FILE):
    with open(KW_FILE, "r", encoding="utf-8") as f:
        keywords = [l.strip() for l in f if l.strip() and not l.startswith("#")]

if len(keywords) < 2:
    st.warning("Not enough keywords.")
    keywords = ["AI", "Future", "Space", "History"]

if st.button("Mix & Search"):
    k1, k2 = random.sample(keywords, 2)
    combo = f"{k1} {k2}"
    st.header(f"🧪 {combo}")
    
    # Direct Integration with Deep Search [06] (Link)
    import urllib.parse
    q = urllib.parse.quote(combo)
    
    st.markdown(f"### Actions")
    st.markdown(f"- [Search Google](https://www.google.com/search?q={q})")
    st.markdown(f"- [Search Scholar](https://scholar.google.com/scholar?q={q})")
    
    st.info("💡 Concept: What connects these two?")
