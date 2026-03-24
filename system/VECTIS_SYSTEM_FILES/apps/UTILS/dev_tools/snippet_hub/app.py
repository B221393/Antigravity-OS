import streamlit as st
import json
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="Snippet Hub", page_icon="📋")
st.title("📋 Snippet Hub")

DATA_FILE = "snippets.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"Example": "This is a sample snippet."}, f)

with open(DATA_FILE, "r") as f:
    snippets = json.load(f)

# Sidebar: Add New
with st.sidebar:
    st.header("Add New")
    new_title = st.text_input("Title")
    new_content = st.text_area("Content")
    if st.button("Save"):
        if new_title and new_content:
            snippets[new_title] = new_content
            with open(DATA_FILE, "w") as f:
                json.dump(snippets, f)
            st.rerun()

# Main: List
for title, content in snippets.items():
    with st.expander(title):
        st.code(content, language=None)
        if st.button("Delete", key=f"del_{title}"):
            del snippets[title]
            with open(DATA_FILE, "w") as f:
                json.dump(snippets, f)
            st.rerun()
