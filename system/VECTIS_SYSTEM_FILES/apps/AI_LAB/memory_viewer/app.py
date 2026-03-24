import streamlit as st
import glob
import json
import os
# EGO共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Memory Viewer", page_icon="🧠", layout="wide")
st.title("🧠 Memory Viewer (Ego Link)")

# Path to Ego Memories (Assuming standard path)
MEMORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../memory"))

if not os.path.exists(MEMORY_DIR):
    st.error(f"Memory directory not found: {MEMORY_DIR}")
    st.stop()

# Load files
files = glob.glob(os.path.join(MEMORY_DIR, "*.json"))
st.write(f"Found {len(files)} memory fragments.")

data = []
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fp:
            content = json.load(fp)
            # Adapt to whatever format Ego uses
            entry = {
                "Filename": os.path.basename(f),
                "Timestamp": content.get("timestamp", datetime.fromtimestamp(os.path.getmtime(f))),
                "Type": content.get("type", "Generic"),
                "Content": str(content.get("content", content))[:100] + "..."
            }
            data.append(entry)
    except: pass

if data:
    df = pd.DataFrame(data)
    df = df.sort_values("Timestamp", ascending=False)
    
    st.dataframe(df, use_container_width=True)
    
    # Detail View
    selected = st.selectbox("Select Memory to Inspect", df["Filename"])
    if selected:
        full_path = os.path.join(MEMORY_DIR, selected)
        with open(full_path, "r", encoding="utf-8") as fp:
            st.json(json.load(fp))
else:
    st.info("No memories found. Run Ego Engine [04] to generate insights.")
