import streamlit as st
import difflib

st.set_page_config(page_title="Diff Eye", page_icon="👁️", layout="wide")
st.title("👁️ Diff Eye (差分眼力)")

c1, c2 = st.columns(2)
t1 = c1.text_area("Text A", height=300)
t2 = c2.text_area("Text B", height=300)

if st.button("Compare"):
    diff = difflib.unified_diff(
        t1.splitlines(),
        t2.splitlines(),
        fromfile='Text A',
        tofile='Text B',
        lineterm=''
    )
    
    diff_text = "\n".join(diff)
    if not diff_text:
        st.success("Identical!")
    else:
        st.code(diff_text, language="diff")
        
    # Html diff using HtmlDiff (optional, but nice)
    d = difflib.HtmlDiff()
    html = d.make_file(t1.splitlines(), t2.splitlines())
    st.components.v1.html(html, height=600, scrolling=True)
