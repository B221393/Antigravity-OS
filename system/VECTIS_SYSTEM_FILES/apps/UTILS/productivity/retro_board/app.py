import streamlit as st

st.set_page_config(page_title="Retro Board", page_icon="🧘", layout="wide")
st.title("🧘 KPT Retro Board")

# Initialize
for k in ["Keep", "Problem", "Try"]:
    if k not in st.session_state: st.session_state[k] = []

c1, c2, c3 = st.columns(3)

def render_col(col, name, color):
    with col:
        st.header(f"{name}")
        with st.form(f"add_{name}"):
            txt = st.text_input("New Item")
            if st.form_submit_button("Add"):
                if txt: st.session_state[name].append(txt)
                st.rerun()
        
        for idx, item in enumerate(st.session_state[name]):
            st.info(item)
            if st.button("x", key=f"del_{name}_{idx}"):
                st.session_state[name].pop(idx)
                st.rerun()

render_col(c1, "Keep", "green")
render_col(c2, "Problem", "red")
render_col(c3, "Try", "blue")

st.divider()
if st.button("Clear All"):
    for k in ["Keep", "Problem", "Try"]: st.session_state[k] = []
    st.rerun()
