import streamlit as st

st.set_page_config(page_title="Idea Flow", page_icon="💭", layout="wide")
st.title("💭 Idea Flow [Upper Rank 11]")

# Quick Outliner
# Enhancement: Export to Wiki Lite [16] format automatically

if 'nodes' not in st.session_state:
    st.session_state.nodes = ["Root Idea"]

c1, c2 = st.columns([3, 1])

with c1:
    txt = st.text_area("Brainstorming Area", "\n".join(st.session_state.nodes), height=500)

with c2:
    st.subheader("Actions")
    if st.button("Save & Sync"):
        st.session_state.nodes = txt.split("\n")
        st.success("Synced!")
    
    if st.button("Export to Wiki"):
        # Save as Markdown in Wiki Lite folder
        import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
        from datetime import datetime
        WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/wiki_lite/data"))
        fn = f"Idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(os.path.join(WIKI_DIR, fn), "w", encoding="utf-8") as f:
            f.write(f"# Idea Flow Export\n\n{txt}")
        st.success(f"Exported: {fn}")

    st.info("💡 Tip: Use '-' for list items.")
