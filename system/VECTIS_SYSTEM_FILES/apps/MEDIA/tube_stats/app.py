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

st.set_page_config(page_title="Tube Stats", page_icon="📺")
st.title("📺 Tube Stats (YouTube Link)")

# Path to logs (Assuming standard path in AUTO_YOUTUBE)
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../AUTO_YOUTUBE/video_history.csv"))
# Fallback to skipped log if main not found, or just demo
SKIPPED_LOG = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../AUTO_YOUTUBE/skipped_videos.log"))

# We'll try to find any CSV in AUTO_YOUTUBE if specific one misses
BASE_DIR = os.path.dirname(LOG_FILE)

if os.path.exists(LOG_FILE):
    try:
        df = pd.read_csv(LOG_FILE)
        st.write(f"Loaded {len(df)} records from History.")
        
        # Simple stats
        if "channel_name" in df.columns:
            st.subheader("Top Channels")
            st.bar_chart(df["channel_name"].value_counts().head(10))
            
    except Exception as e:
        st.error(f"Error reading history: {e}")

else:
    st.warning(f"History file not found at {LOG_FILE}")
    st.info("Showing mock data layout for now.")
    
    # Mock
    df = pd.DataFrame({
        "Channel": ["Tech News", "Music", "Vlog", "Tech News", "Gaming"],
        "Date": ["2026-01-01", "2026-01-02", "2026-01-02", "2026-01-03", "2026-01-03"]
    })
    st.table(df)
    st.bar_chart(df["Channel"].value_counts())
