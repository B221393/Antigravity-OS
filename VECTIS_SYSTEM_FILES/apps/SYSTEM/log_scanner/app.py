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

st.set_page_config(page_title="Log Scanner", page_icon="🕵️", layout="wide")
st.title("🕵️ Log Scanner [Upper Rank 10]")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
VECTIS_CORE = os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/apps/vectis_core/target/release/vectis_core.exe")
LOG_PATH = os.path.join(ROOT_DIR, "logs/error_stream.jsonl")

# Use Rust to scan logs fast
if os.path.exists(VECTIS_CORE) and os.path.exists(LOG_PATH):
    st.info("⚡ Powered by Rust Vectis Core")
    try:
        cmd = [VECTIS_CORE, "scan-logs", "--path", LOG_PATH, "--limit", "100"]
        # Hide Window logic
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        res = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
        data = json.loads(res.stdout)
        
        lines = data.get("lines", [])
        st.write(f"Showing last {len(lines)} events from High-Speed Scan:")
        
        for line in reversed(lines):
            try:
                # Assuming line is json
                j = json.loads(line)
                lvl = j.get("level", "INFO")
                icon = "🔴" if lvl == "ERROR" else "ℹ️"
                st.code(f"{icon} [{j.get('timestamp')}] {j.get('message')}")
            except:
                st.text(line)
                
    except Exception as e:
        st.error(f"Rust Core Error: {e}")
else:
    st.warning("Rust Core or Log file missing. Falling back to Python slow read.")
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            st.text(f.read())
