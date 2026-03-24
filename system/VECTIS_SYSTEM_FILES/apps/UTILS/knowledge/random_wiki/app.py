import streamlit as st
import glob
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import random

st.set_page_config(page_title="Random Wiki", page_icon="🎲")
st.title("🎲 Random Wiki [Rank 24]")

WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/wiki_lite/data"))
files = glob.glob(os.path.join(WIKI_DIR, "*.md"))

if st.button("Roll Dice 🎲") or 'rand_file' not in st.session_state:
    if files:
        st.session_state.rand_file = random.choice(files)
    else:
        st.session_state.rand_file = None

if st.session_state.rand_file:
    fpath = st.session_state.rand_file
    st.subheader(f"📄 {os.path.basename(fpath)}")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    st.markdown(content)
    
    # Integration with Abstract Writer [07]
    if st.button("Summarize this (To App 07)"):
        tf = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../transfer.txt"))
        with open(tf, "w", encoding="utf-8") as f:
            f.write(content[:5000]) # Limit
        st.success("Sent to Transfer Buffer! Open [07] Abstract Writer.")
