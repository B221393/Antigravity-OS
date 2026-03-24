import streamlit as st
import glob
import os
# EGO共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import json
import time

st.set_page_config(page_title="Ego Engine", page_icon="🧠", layout="wide")
st.title("🧠 Ego Engine Core [Rank 35]")

# Matrix style logs
st.markdown("""
<style>
.stApp { background-color: #000000; color: #00FF00; }
div.stMarkdown { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

MEMORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../memory"))
files = sorted(glob.glob(os.path.join(MEMORY_DIR, "*.json")), reverse=True)

if files:
    latest = files[0]
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    st.header(f"THOUGHT_CYCLE: {os.path.basename(latest)}")
    st.code(json.dumps(data, indent=2, ensure_ascii=False), language="json")
    
    st.subheader("HISTORY_DUMP")
    for f in files[1:6]:
         with open(f, "r", encoding="utf-8") as fp:
             d = json.load(fp)
             st.text(f"[{d.get('timestamp', '?')}] {d.get('thought', '')[:100]}...")
else:
    st.warning("NO_SIGNAL")

if st.button("FORCE_THINK"):
    # Trigger python script
    p = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../run_ego_think.py"))
    os.system(f"start python \"{p}\"")
    st.success("SIGNAL_SENT")
