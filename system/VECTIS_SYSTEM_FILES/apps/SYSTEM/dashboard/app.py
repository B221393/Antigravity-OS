import streamlit as st
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import subprocess
import json
import glob
from datetime import datetime

st.set_page_config(page_title="VECTIS Dashboard", page_icon="💠", layout="wide")
st.title("💠 VECTIS Dashboard [Rank 13]")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
VECTIS_CORE = os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/apps/vectis_core/target/release/vectis_core.exe")

# --- Rust Health Widget ---
st.subheader("🖥️ System Status")
cols = st.columns(4)

stats = {}
if os.path.exists(VECTIS_CORE):
    try:
        # Fast health check
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        res = subprocess.run([VECTIS_CORE, "health-check", "--root", os.path.join(ROOT_DIR, "apps")], capture_output=True, text=True, startupinfo=si)
        stats = json.loads(res.stdout)
    except: pass

with cols[0]:
    st.metric("Total Files", stats.get("total_files", "N/A"))
with cols[1]:
    size_mb = stats.get("total_size_bytes", 0) / (1024*1024)
    st.metric("System Size", f"{size_mb:.1f} MB")
with cols[2]:
    st.metric("Core Status", stats.get("status", "Unknown"))
with cols[3]:
    st.metric("Last Check", datetime.now().strftime("%H:%M"))

st.divider()

# --- Quick Launcher (Mini) ---
st.subheader("🚀 Quick Access")
quick_apps = {
    "Auto Watcher [03]": "03_Auto_Watcher.bat",
    "News [05]": "05_News_Aggregator.bat",
    "Wiki [16]": "16_Wiki_Lite.bat",
    "Journal [17]": "17_Journal_Plus.bat"
}

c = st.columns(len(quick_apps))
for i, (name, bat) in enumerate(quick_apps.items()):
    with c[i]:
        if st.button(name):
             subprocess.Popen(f'start "" "{bat}"', shell=True, cwd=ROOT_DIR)

st.divider()
st.info("For full app list, use [01] Ultimate Launcher.")
