import streamlit as st
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="Task Bridge", page_icon="🌉")
st.title("🌉 Task Bridge [Rank 39]")

# Sync with Ultimate Launcher Logic if needed.
# Here we provide a simple "Sync to Desktop" button
# that copies the web todo list to the desktop memo.txt

TODO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/todo/todo_list.txt"))
MEMO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/desktop_hud/memo.txt"))

c1, c2 = st.columns(2)
t_con = ""
m_con = ""

if os.path.exists(TODO):
    with open(TODO, "r") as f: t_con = f.read()
if os.path.exists(MEMO):
    with open(MEMO, "r") as f: m_con = f.read()

with c1:
    st.subheader("Web Todo")
    new_t = st.text_area("Todo", t_con, height=300)

with c2:
    st.subheader("Desktop Memo")
    st.text(m_con)

if st.button("Sync Web -> Desktop"):
    with open(MEMO, "w", encoding="utf-8") as f: f.write(new_t)
    st.success("Synced to HUD!")
