import streamlit as st
import pandas as pd
import json
import glob
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import subprocess

st.set_page_config(page_title="Data Lake Viewer", page_icon="🌊", layout="wide")
st.title("🌊 Data Lake Viewer [Upper Rank 4]")

# Path Config
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
# Rust Grep Tool (Flash Grep) - Assuming it's compiled at apps/flash_grep or similar
FLASH_GREP_EXE = os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/apps/flash_grep/target/release/flash_grep.exe")

# Sources
SOURCES = {
    "YouTube History": "AUTO_YOUTUBE/video_history.csv",
    "Job DB": "VECTIS_SYSTEM_FILES/apps/job_hq/job_db.json",
    "Books": "VECTIS_SYSTEM_FILES/apps/book_keeper/books.json",
    "System Logs": "logs/LAST_ERROR.md"
}

# 1. Search Bar (Rust Powered)
st.subheader("🚀 High-Speed Search")
query = st.text_input("Deep Search across ALL files (uses Flash Grep)")

if query and st.button("Search"):
    if os.path.exists(FLASH_GREP_EXE):
        try:
            # Search in the whole ROOT_DIR context generally or specific folders
            # Let's search inside 'AUTO_YOUTUBE' and 'VECTIS_SYSTEM_FILES'
            search_dirs = [os.path.join(ROOT_DIR, "AUTO_YOUTUBE"), os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/apps")]
            
            results = []
            for d in search_dirs:
                cmd = [FLASH_GREP_EXE, query, d]
                # Windows hide window
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
                if res.stdout.strip():
                    results.append(res.stdout)
            
            if results:
                st.success("Found matches!")
                for r in results:
                    st.code(r)
            else:
                st.warning("No matches found.")
        except Exception as e:
            st.error(f"Rust Tool Error: {e}")
    else:
        st.warning("Flash Grep not found. Please compile App [27] first.")

st.divider()

# 2. Data Browser
st.subheader("📂 Data Browser")
target = st.selectbox("Select Source", list(SOURCES.keys()))
rel_path = SOURCES[target]
full_path = os.path.join(ROOT_DIR, rel_path)

if os.path.exists(full_path):
    if full_path.endswith(".csv"):
        df = pd.read_csv(full_path)
        st.dataframe(df, use_container_width=True)
    elif full_path.endswith(".json"):
        with open(full_path, "r", encoding="utf-8") as f:
            st.json(json.load(f))
    elif full_path.endswith(".md"):
        with open(full_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
else:
    st.error(f"File not found: {rel_path}")
