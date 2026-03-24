import streamlit as st
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import json

st.set_page_config(page_title="System Config", page_icon="⚙️")
st.title("⚙️ System Config [Upper Rank 12]")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
ENV_FILE = os.path.join(ROOT_DIR, ".env")
KEYWORDS_FILE = os.path.join(ROOT_DIR, "AUTO_YOUTUBE/MY_KEYWORDS.txt")

tabs = st.tabs([".env Config", "Keywords", "Vectis Core"])

with tabs[0]:
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f: c = f.read()
        new_c = st.text_area(".env Content", c, height=200)
        if st.button("Save .env"):
            with open(ENV_FILE, 'w', encoding='utf-8') as f: f.write(new_c)
            st.success("Saved!")

with tabs[1]:
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f: k = f.read()
        new_k = st.text_area("YouTube Keywords", k, height=200)
        if st.button("Save Keywords"):
            with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f: f.write(new_k)
            st.success("Saved!")

with tabs[2]:
    st.write("Rust Core Status")
    core_path = os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/apps/vectis_core/target/release/vectis_core.exe")
    if os.path.exists(core_path):
        st.success("✅ Installed")
        st.code(core_path)
    else:
        st.error("❌ Not Found")
        st.info("Run `cargo build --release` in `apps/vectis_core`")
