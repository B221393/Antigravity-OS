import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import glob
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="Corpus Map", page_icon="🕸️", layout="wide")
st.title("🕸️ Corpus Map (Knowledge Graph)")

# Scan markdown files in youtube summarized folder
MD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../AUTO_YOUTUBE/summarized"))

files = glob.glob(os.path.join(MD_DIR, "**/*.md"), recursive=True)

if not files:
    st.warning("No markdown files found to map.")
    st.stop()

st.write(f"Scanning {len(files)} nodes...")

G = nx.Graph()

for f in files:
    name = os.path.basename(f).replace(".md", "")
    G.add_node(name)
    
    # Mock edges: Connect if names share words
    # (Real implementation would parse [[WikiLinks]])
    words = set(name.split())
    
    # Simple connect to random existing for viz
    # This simulates "hidden connections"
    if len(G.nodes) > 1:
        target = list(G.nodes)[-2] # prev
        G.add_edge(name, target)

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, font_size=8, ax=ax)
st.pyplot(fig)
