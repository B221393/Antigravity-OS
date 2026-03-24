import streamlit as st
import urllib.parse

st.set_page_config(page_title="URL Keeper", page_icon="🔖")
st.title("🔖 URL Keeper (書庫番人)")

mode = st.radio("Mode", ["Encode", "Decode"])
txt = st.text_area("Input URL")

if st.button("Execute"):
    if mode == "Encode":
        st.code(urllib.parse.quote(txt))
    else:
        st.code(urllib.parse.unquote(txt))
