import streamlit as st
from datetime import datetime
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="Journal Plus", page_icon="📓")
st.title("📓 Journal Plus [Rank 17]")

date = st.date_input("Date", datetime.now())

# Sections
st.subheader("1. Achievements")
achieve = st.text_area("Achievements", height=100)

st.subheader("2. Learnings")
learn = st.text_area("Learnings", height=100)

st.subheader("3. Tomorrow")
plan = st.text_area("Plan", height=100)

if st.button("Generate & Save to Wiki"):
    report = f"""# Daily Report: {date}
-----------------------
## ✅ Achievements
{achieve}

## 🧠 Learnings
{learn}

## 🚀 Tomorrow
{plan}
-----------------------
"""
    st.code(report, language="markdown")
    
    # Save to Wiki
    WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/wiki_lite/data"))
    fname = f"Journal_{date.strftime('%Y-%m-%d')}.md"
    path = os.path.join(WIKI_DIR, fname)
    
    if not os.path.exists(WIKI_DIR): os.makedirs(WIKI_DIR)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
        
    st.success(f"Saved to Wiki: {fname}")
