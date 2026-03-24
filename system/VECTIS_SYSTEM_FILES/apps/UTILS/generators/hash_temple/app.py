import streamlit as st
import hashlib

st.set_page_config(page_title="Hash Temple", page_icon="🏯")
st.title("🏯 Hash Temple (ハッシュ寺院)")

txt = st.text_input("Enter String")
if txt:
    b = txt.encode('utf-8')
    st.code(f"MD5:    {hashlib.md5(b).hexdigest()}")
    st.code(f"SHA1:   {hashlib.sha1(b).hexdigest()}")
    st.code(f"SHA256: {hashlib.sha256(b).hexdigest()}")
    st.code(f"SHA512: {hashlib.sha512(b).hexdigest()}")
