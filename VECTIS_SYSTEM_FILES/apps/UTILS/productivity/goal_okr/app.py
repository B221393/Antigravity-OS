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

st.set_page_config(page_title="Goal OKR", page_icon="🎯", layout="wide")
st.title("🎯 Goal OKR [Upper Rank 9]")

# Backed by Rust for heavy stats if we had millions of OKRs, 
# for now we use Rust Vectis Core to "Health Check" the file or analyze trends if it was CSV.
# Here we demonstrate Rust integration for "System Status" check displayed on dashboard.

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
VECTIS_CORE = os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/apps/vectis_core/target/release/vectis_core.exe")

# --- Rust Health Check Sidebar ---
if os.path.exists(VECTIS_CORE):
    try:
        # Check integrity
        res = subprocess.run([VECTIS_CORE, "health-check", "--root", os.path.join(ROOT_DIR, "apps")], capture_output=True, text=True)
        stats = json.loads(res.stdout)
        st.sidebar.metric("System Files", stats.get("total_files", 0))
        st.sidebar.caption("Verified by Rust Core")
    except: pass

# --- Main OKR Logic (Python UI) ---
if 'objectives' not in st.session_state:
    st.session_state.objectives = [{"Obj": "Master VECTIS", "KRs": [{"KR": "Complete 100 Apps", "Progress": 100}]}]

# (Simple CRUD logic preserved/enhanced)
for i, obj in enumerate(st.session_state.objectives):
    with st.expander(f"🎯 {obj['Obj']}", expanded=True):
        for kr in obj['KRs']:
            st.write(f"- {kr['KR']}")
            st.progress(kr['Progress'] / 100)
