import streamlit as st
import glob
import os
# EGO共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Knowledge Network", page_icon="🕸️", layout="wide")
st.title("🕸️ Knowledge Network (Wiki Map) [Rank 21]")

WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/wiki_lite/data"))
files = glob.glob(os.path.join(WIKI_DIR, "*.md"))

if not files:
    st.warning("No Wiki files found.")
    st.stop()

net = Network(height='600px', width='100%', bgcolor='#0E1117', font_color='white')

# Simple Link Analysis based on filename mention
# (Real logic would parse [[]] wiki links)

file_names = [os.path.basename(f).replace(".md", "") for f in files]

for name in file_names:
    net.add_node(name, label=name, title=name, color='#4F8BF9')

# Create Edges (Mock: if name parts overlap)
for i, name1 in enumerate(file_names):
    for name2 in file_names[i+1:]:
        # Simple Co-occurrence logic or random for demo if no real content links
        # Let's link if share a word prefix (3 chars)
        if name1[:3].lower() == name2[:3].lower():
            net.add_edge(name1, name2)

net.barnes_hut()
tmp_path = os.path.join(os.path.dirname(__file__), "kn_graph.html")
net.save_graph(tmp_path)

with open(tmp_path, 'r', encoding='utf-8') as f:
    components.html(f.read(), height=620)
