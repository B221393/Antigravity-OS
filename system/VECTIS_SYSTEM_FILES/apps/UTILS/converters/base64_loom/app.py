import streamlit as st
import base64

st.set_page_config(page_title="Base64 Loom", page_icon="🧶")
st.title("🧶 Base64 Loom (機密織機)")

mode = st.radio("Mode", ["Encode", "Decode"])
txt = st.text_area("Input Text")

if st.button("Processing"):
    try:
        if mode == "Encode":
            res = base64.b64encode(txt.encode('utf-8')).decode('utf-8')
        else:
            res = base64.b64decode(txt).decode('utf-8')
        st.code(res)
    except Exception as e:
        st.error(f"Error: {e}")
