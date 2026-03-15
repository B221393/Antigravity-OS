import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

st.set_page_config(page_title="Skill Tree", page_icon="🌲", layout="wide")
st.title("🌲 Skill Tree (Interactive) [Rank 20]")

# Define Skills (Mock for demo, normally load from json)
skills = {
    "VECTIS OS": ["Python", "Rust", "Streamlit", "AI Agents"],
    "Python": ["Pandas", "NetworkX", "FastAPI"],
    "Rust": ["Clap", "Rayon", "Serde"],
    "AI Agents": ["RAG", "Function Calling", "Prompt Eng"]
}

# Build pyvis network
net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')

for parent, children in skills.items():
    net.add_node(parent, label=parent, color='#FF5733', size=20)
    for child in children:
        net.add_node(child, label=child, color='#33FF57', size=15)
        net.add_edge(parent, child)

# Options
net.repulsion(node_distance=100, spring_length=200)

# Generate HTML
try:
    path = os.path.join(os.path.dirname(__file__), "graph.html")
    net.save_graph(path)
    
    with open(path, 'r', encoding='utf-8') as f:
        html_string = f.read()
    
    components.html(html_string, height=520)
except Exception as e:
    st.error(f"Graph gen error: {e}")
    st.info("Please install pyvis: `pip install pyvis`")
