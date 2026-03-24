import streamlit as st
import re
import sys
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../modules")))
import vectis_ui

vectis_ui.setup_page("Regex Dojo", "🥋")
st.title("🥋 Regex Dojo [Rank 29]")

c1, c2 = st.columns([1, 3])
pattern = c1.text_input("Pattern (Regex)", r"\d+")
flags = c1.multiselect("Flags", ["IGNORECASE", "MULTILINE", "DOTALL"])

text = c2.text_area("Test Text", "Phone: 123-4567\nID: 999\nDate: 2025-01-01")

# Apply Flags
f_val = 0
if "IGNORECASE" in flags: f_val |= re.IGNORECASE
if "MULTILINE" in flags: f_val |= re.MULTILINE
if "DOTALL" in flags: f_val |= re.DOTALL

st.subheader("Matches")
try:
    matches = list(re.finditer(pattern, text, f_val))
    if matches:
        st.success(f"Found {len(matches)} matches.")
        for i, m in enumerate(matches):
            with st.expander(f"Match {i+1}: '{m.group()}'"):
                st.write(f"Span: {m.span()}")
                st.write(f"Groups: {m.groups()}")
    else:
        st.warning("No matches.")
except Exception as e:
    st.error(f"Regex Error: {e}")
