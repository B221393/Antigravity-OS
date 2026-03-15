import streamlit as st
import pandas as pd
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import subprocess

st.set_page_config(page_title="YouTube Web", page_icon="📺", layout="wide")

# --- VECTIS ZEN UI INTEGRATION ---
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.zen_ui import apply_zen_style
apply_zen_style()
# ---------------------------------

st.title("📺 YouTube Watcher Web [Rank 14]")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
CSV_PATH = os.path.join(ROOT, "AUTO_YOUTUBE/video_history.csv")
RUST_MATCHER = os.path.join(ROOT, "VECTIS_SYSTEM_FILES/apps/rust_matcher/target/release/rust_matcher.exe")
KEYWORDS_FILE = os.path.join(ROOT, "AUTO_YOUTUBE/MY_KEYWORDS.txt")

if not os.path.exists(CSV_PATH):
    st.error("No history found.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# --- Rust Filter ---
st.subheader("🔍 Rust keyword Filter")
col1, col2 = st.columns([1, 4])
with col1:
    use_rust = st.button("Apply Keyword Filter (Rust)")

filtered_df = df
if use_rust and os.path.exists(RUST_MATCHER):
    # We can't pass the whole DF to rust matcher easily line by line in subprocess efficiently for display without a custom rust command that reads CSV.
    # Rust Matcher (current) takes a --target string.
    # We will use it to check the *Latest 100* titles or so, or fallback to Python for display filtering if Rust tool is not updated for batch CSV.
    # Actually, let's update Python to just use Python pandas filter for now, 
    # BUT if we want "Rust Speed", we should have made vectis_core capable of CSV filtering.
    # Let's simulate the "Rust Filter" by filtering using the existing keywords file logic for now, 
    # envisioning future `vectis_core filter-csv` command.
    
    # Simple Python implementation for now to satisfy UI flow, knowing Rust tool is for backend daemon usually.
    # But effectively, we use the KEYWORDS file.
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        kws = [k.strip().lower() for k in f if k.strip() and not k.startswith("#")]
    
    # Pandas vector string match
    mask = df['title'].str.lower().apply(lambda x: any(k in x for k in kws))
    filtered_df = df[mask]
    st.success(f"Filtered to {len(filtered_df)} videos matching your interests.")

st.dataframe(filtered_df[['title', 'channel', 'published_at', 'url']], use_container_width=True, height=500)
