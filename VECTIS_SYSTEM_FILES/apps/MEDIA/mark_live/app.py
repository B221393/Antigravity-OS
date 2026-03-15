import streamlit as st

st.set_page_config(page_title="Mark Live", page_icon="📝", layout="wide")
st.title("📝 Mark Live (即時記述)")

c1, c2 = st.columns(2)
md = c1.text_area("Markdown Input", "# Hello\n\n- List 1\n- List 2")

with c2:
    st.markdown(md)
    st.divider()
    st.subheader("HTML Source")
    st.code("<html>... (rendered by streamlit) ...</html>")
