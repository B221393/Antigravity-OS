import streamlit as st
import uuid

st.set_page_config(page_title="UUID Forge", page_icon="🆔")
st.title("🆔 UUID Forge (識別子工房)")

count = st.number_input("Count", 1, 100, 5)
ver = st.selectbox("Version", [4, 1])

if st.button("Forge"):
    out = ""
    for _ in range(count):
        if ver == 4: u = uuid.uuid4()
        else: u = uuid.uuid1()
        out += str(u) + "\n"
    st.text_area("Result", out, height=200)
