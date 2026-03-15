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
import random

st.set_page_config(page_title="Ego Voice", page_icon="🗣️")
st.title("🗣️ Ego Voice (Thought Reader)")

MEMORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../memory"))

if st.button("Listen to Ego (Simulated)"):
    # Find latest memory
    files = glob.glob(os.path.join(MEMORY_DIR, "*.json"))
    if files:
        latest = max(files, key=os.path.getmtime)
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        thought = data.get("thought", "Hello. I am functioning normally.")
        
        st.write(f"**Thought**: {thought}")
        
        # In a real local app, we could use pyttsx3, but streamlit cloud doesn't support audio out easily.
        # We'll pretend or use st.audio if we had a GENERATED file.
        # For this version, we emphasize the TEXT and visual "Speaking"
        
        st.info("🔊 (Imagine a calm, synthetic voice reading the text above...)")
        
    else:
        st.error("No thoughts found.")
