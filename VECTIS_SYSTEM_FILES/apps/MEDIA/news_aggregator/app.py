import streamlit as st
import feedparser
import urllib.parse
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="News Aggregator", page_icon="📰", layout="wide")
st.title("📰 News Aggregator [Upper Rank 5]")

FEEDS = {
    "Reuters Tech": "http://feeds.reuters.com/reuters/technologyNews",
    "Hacker News": "https://news.ycombinator.com/rss",
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "ArXiv AI": "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=10&sortBy=lastUpdatedDate&sortOrder=descending"
}

target = st.sidebar.selectbox("Feed", list(FEEDS.keys()))

if st.button("Fetch"):
    try:
        f = feedparser.parse(FEEDS[target])
        for entry in f.entries[:10]:
            with st.container():
                st.subheader(entry.title)
                st.write(entry.get("summary", "")[:200] + "...")
                st.write(f"Published: {entry.get('published', 'N/A')}")
                
                c1, c2 = st.columns([1, 4])
                c1.link_button("Read", entry.link)
                
                # Integration with Abstract Writer [07]
                # Since we can't easily POST to another Streamlit app instance, 
                # we save to a transfer file or copy to clipboard logic.
                # Here we just prepare the text.
                if c2.button("Send to AI Summary", key=entry.link):
                    st.session_state['transfer_text'] = entry.summary + "\nSource: " + entry.link
                    st.success("Copied to Transfer Buffer! Open [07] Abstract Writer.")
                    
                    # Save to temp file for 07 to pickup
                    tf = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../transfer.txt"))
                    with open(tf, "w", encoding="utf-8") as tfp:
                        tfp.write(entry.get("summary", "") + "\n" + entry.link)
                    
            st.divider()
    except Exception as e:
        st.error(f"Error: {e}")
