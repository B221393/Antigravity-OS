import streamlit as st
import urllib.parse

st.set_page_config(page_title="Deep Search", page_icon="🔬")
st.title("🔬 Deep Search [Upper Rank 6]")

query = st.text_input("Query", "AI Ethics")

c1, c2, c3, c4 = st.columns(4)
pdf = c1.checkbox("PDF", True)
ppt = c2.checkbox("PPT")
edu = c3.checkbox("Academic (.edu)")
gov = c4.checkbox("Gov (.gov)")

if st.button("Construct & Search"):
    q = query
    if pdf: q += " filetype:pdf"
    if ppt: q += " filetype:ppt"
    
    sites = []
    if edu: sites.append("site:.edu")
    if gov: sites.append("site:.gov")
    
    if sites:
        q += " (" + " OR ".join(sites) + ")"
        
    encoded = urllib.parse.quote(q)
    
    st.markdown(f"### 🔍 {q}")
    st.markdown(f"[Google](https://www.google.com/search?q={encoded})")
    st.markdown(f"[Scholar](https://scholar.google.com/scholar?q={encoded})")
    st.markdown(f"[arXiv](https://arxiv.org/search/?query={urllib.parse.quote(query)})") # arXiv doesn't support filetype op in url same way often
