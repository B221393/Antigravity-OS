import streamlit as st
import json
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import time
from datetime import datetime
import streamlit.components.v1 as components

# PAGE CONFIG
st.set_page_config(page_title="VECTIS COSMIC COMPENDIUM", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")

# PATHS
HISTORY_FILE = "c:\\Users\\Yuto\\Desktop\\app\\s_history.json"

# STYLE
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    .shinsho-card {
        background: #1a1a1a;
        border-left: 6px solid #ffcc00;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(255, 204, 0, 0.1);
        border-radius: 4px;
        transition: transform 0.2s;
        font-family: "Hiragino Mincho ProN", "Yu Mincho", serif;
    }
    .shinsho-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 25px rgba(255, 204, 0, 0.3);
    }
    .genre-tag {
        font-size: 0.8em;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }
    .shinsho-title {
        font-size: 1.4em;
        font-weight: bold;
        color: #fff;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    .shinsho-summary {
        font-size: 0.9em;
        color: #ccc;
        line-height: 1.6;
        max-height: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    h1 {
        font-family: "Hiragino Mincho ProN", "Yu Mincho", serif;
        text-align: center;
        margin-bottom: 40px;
        color: #ffcc00;
        text-shadow: 0 0 10px #ffcc00;
    }
</style>
""", unsafe_allow_html=True)

# LOAD DATA
def load_data():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("nodes", [])
        except:
            return []
    return []

nodes = load_data()

# HEADER
st.title("VECTIS 🌌 COSMIC LIBRARY")

# LAYOUT
col_graph, col_books = st.columns([3, 1])

# GRAPH GENERATION (3D FORCE GRAPH)
with col_graph:
    # Prepare Graph Data
    graph_nodes = [{"id": "ROOT", "name": "VECTIS", "val": 20, "color": "#ffffff"}]
    graph_links = []
    
    genres = {} # name -> id
    
    for book in nodes:
        b_id = book.get("id")
        b_title = book.get("source", "Untitled")
        b_genre = book.get("group", "Uncategorized")
        
        # Genre Node
        if b_genre not in genres:
            g_id = f"G_{b_genre}"
            genres[b_genre] = g_id
            # Distinct color for genres (simple hash or list)
            graph_nodes.append({"id": g_id, "name": b_genre, "val": 10, "color": "#ffcc00"})
            graph_links.append({"source": "ROOT", "target": g_id})
            
        # Book Node
        graph_nodes.append({"id": b_id, "name": b_title, "val": 5, "color": "#00aaff", "desc": book.get("content", "")[:100]})
        graph_links.append({"source": genres[b_genre], "target": b_id})

    json_nodes = json.dumps(graph_nodes)
    json_links = json.dumps(graph_links)

    html_code = f"""
    <head>
      <style> body {{ margin: 0; }} </style>
      <script src="//unpkg.com/3d-force-graph"></script>
    </head>
    <body>
      <div id="3d-graph"></div>
      <script>
        const gData = {{
          nodes: {json_nodes},
          links: {json_links}
        }};

        const Graph = ForceGraph3D()
          (document.getElementById('3d-graph'))
          .graphData(gData)
          .nodeLabel('name')
          .nodeColor('color')
          .nodeVal('val')
          .linkDirectionalParticles(2)
          .linkDirectionalParticleSpeed(d => 0.005)
          .backgroundColor('#000000');
          
        // Auto-orbit
        let angle = 0;
        setInterval(() => {{
          Graph.cameraPosition({{
            x: 400 * Math.sin(angle),
            z: 400 * Math.cos(angle)
          }});
          angle += Math.PI / 300;
        }}, 10);
      </script>
    </body>
    """
    components.html(html_code, height=700)

# BOOKS SIDEBAR (SHINSHO STYLE)
with col_books:
    st.subheader("📚 New Arrivals")
    
    # Reverse order (newest first)
    for book in reversed(nodes):
        with st.container():
            st.markdown(f"""
            <div class="shinsho-card">
                <div class="genre-tag">{book.get('group', 'GENERAL')}</div>
                <div class="shinsho-title">{book.get('source')}</div>
                <div class="shinsho-summary">
                    {book.get('content', '').replace('#', '').strip()[:150]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📖 Read", key=book.get('id')):
                # Show Full Modal (using expander for now)
                with st.expander("Full Content", expanded=True):
                    st.markdown(book.get('content'))

# AUTO REFRESH (Simulated Loop)
if st.button("🔄 Refresh Library"):
    st.rerun()

time.sleep(10)
st.rerun()
