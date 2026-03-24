import streamlit as st
import subprocess
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import json
import time

st.set_page_config(page_title="Panic Button", page_icon="🚨", layout="centered")
st.title("🚨 PANIC BUTTON [Rank 34]")

KILLER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../apps/process_killer/target/release/process_killer.exe"))

st.error("⚠️ EMERGENCY SYSTEM KILL SWITCH")
st.write("This will terminate ALL Python, Node, Streamlit processes immediately.")

if st.button("EXECUTE KILL (Rust)", type="primary", use_container_width=True):
    if os.path.exists(KILLER):
        # Run killer
        try:
            # We use creationflags to run detached if possible, or just run
            subprocess.Popen([KILLER, "--force"], shell=True)
            st.success("KILL SIGNAL SENT.")
            time.sleep(2)
            st.warning("Connection Lost (Expected)")
        except Exception as e:
            st.error(f"Failed: {e}")
    else:
        st.error("Rust binary not found. Compiling fallback...")
        # Fallback python kill
        os.system("taskkill /F /IM python.exe")
