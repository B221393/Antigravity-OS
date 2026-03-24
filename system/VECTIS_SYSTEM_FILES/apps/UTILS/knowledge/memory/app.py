
import streamlit as st
import os
import sys
import glob
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Try to import Rust-powered core (10-50x faster)
try:
    from modules import vectis_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

# Page Config
st.set_page_config(page_title="🌌 Memory 3D | 自分ステーション", page_icon="🌌", layout="wide")

# --- STYLES: VECTIS CORE ---
apply_vectis_style()
st.markdown("""
<style>
    /* Premium Cyber-Station HUD */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0a0a20 0%, #050510 100%);
    }
    
    h1, h2, h3 { 
        color: #00E5FF !important; 
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        font-family: 'Oswald', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(20, 20, 40, 0.6) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
    }

    /* Floating HUD Panel */
    .hud-panel {
        background: rgba(10, 10, 30, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 15px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
    }
    
    .rarity-tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8em;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🖥️ ターミナル設定")
    sphere_size = st.slider("ノード感度", 5, 20, 8)
    line_alpha = st.slider("通信強度の視認性", 0.1, 1.0, 0.5)
    similarity_threshold = st.slider("相関同期しきい値 (%)", 5, 50, 15)
    st.info("知識と記憶のバイナリ・マトリックスを3D空間で結合中...")

# Data Loading (unchanged logic)
def load_all_nodes():
    nodes = []
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # K-Cards
    kcard_pattern = os.path.join(BASE_DIR, "apps", "job_hunting", "**", "*.kcard")
    for f in glob.glob(kcard_pattern, recursive=True):
        try:
            with open(f, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)
                nodes.append({
                    "id": f"K_{len(nodes)}",
                    "title": data.get("title", "K-Card"),
                    "type": "Knowledge",
                    "content": data.get("content", ""),
                    "rarity": data.get("rarity", "Common")
                })
        except: pass
        
    # Diary
    diary_file = os.path.join(BASE_DIR, "apps", "diary", "data", "entries.json")
    if os.path.exists(diary_file):
        try:
            with open(diary_file, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)
                for d in data:
                    nodes.append({
                        "id": f"D_{len(nodes)}",
                        "title": d.get("title", "Diary"),
                        "type": "Diary",
                        "content": d.get("content", ""),
                        "rarity": "Common"
                    })
        except: pass
    
    # YouTube Notes
    youtube_pattern = os.path.join(BASE_DIR, "apps", "memory", "data", "youtube_notes", "*.md")
    for f in glob.glob(youtube_pattern):
        try:
            with open(f, "r", encoding="utf-8") as f_in:
                content = f_in.read()
                lines = content.split('\n')
                title = lines[0].replace('# 📺 ', '').strip() if lines else "YouTube"
                nodes.append({
                    "id": f"Y_{len(nodes)}",
                    "title": title,
                    "type": "YouTube",
                    "content": content,
                    "rarity": "Rare"
                })
        except: pass

    # 4. Identity Logs (To-Do)
    todo_file = os.path.join(BASE_DIR, "apps", "todo", "data", "todo_log.json")
    if os.path.exists(todo_file):
        try:
            with open(todo_file, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)
                for d in data:
                    if d.get('done'):
                        nodes.append({
                            "id": f"I_{len(nodes)}",
                            "title": d.get("title", "Identity"),
                            "type": "Identity",
                            "content": d.get("note", ""),
                            "rarity": "Epic" if "技術" in d.get('cat', '') else "Common"
                        })
        except: pass

    # 5. Agent Logs (Scribed from logs)
    agent_log_pattern = os.path.join(BASE_DIR, "VECTIS_SYSTEM_FILES", "apps", "job_hunting", "scanned", "agent_log_*.kcard")
    for f in glob.glob(agent_log_pattern):
        try:
            with open(f, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)
                nodes.append({
                    "id": f"A_{len(nodes)}",
                    "title": data.get("title", "Agent Entry"),
                    "type": "AgentLog",
                    "content": data.get("content", ""),
                    "rarity": data.get("rarity", "Epic"),
                    "mtime": os.path.getmtime(f)
                })
        except: pass

    # 6. Synapses (AI-generated connections)
    synapse_pattern = os.path.join(BASE_DIR, "VECTIS_SYSTEM_FILES", "apps", "job_hunting", "scanned", "*.synapse")
    for f in glob.glob(synapse_pattern):
        try:
            with open(f, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)
                nodes.append({
                    "id": f"S_{len(nodes)}",
                    "title": data.get("title", "Synapse"),
                    "type": "Synapse",
                    "content": data.get("content", ""),
                    "rarity": "Legendary",
                    "mtime": os.path.getmtime(f)
                })
        except: pass

    # 7. VCC (Vectis Compressed Core)
    vcc_pattern = os.path.join(BASE_DIR, "VECTIS_SYSTEM_FILES", "apps", "job_hunting", "scanned", "*.vcc")
    for f in glob.glob(vcc_pattern):
        try:
            if RUST_AVAILABLE:
                with open(f, "rb") as f_in:
                    raw_bin = f_in.read()
                    from modules import vectis_core
                    decompressed_text = vectis_core.decompress_data(raw_bin)
                    if decompressed_text:
                        data = json.loads(decompressed_text)
                        nodes.append({
                            "id": f"V_{len(nodes)}",
                            "title": data.get("title", "Compressed Node"),
                            "type": "Compressed",
                            "content": data.get("content", ""),
                            "rarity": data.get("rarity", "Mythic"),
                            "mtime": os.path.getmtime(f)
                        })
        except: pass

    return nodes

nodes = load_all_nodes()

# --- Wiki Link Logic ---
def apply_wiki_links(text):
    """Detect keywords and wrap them with clickable links"""
    if not RUST_AVAILABLE:
        return text
    keywords = vectis_core.extract_keywords(text)
    processed = text
    sorted_kws = sorted(list(keywords), key=len, reverse=True)
    for kw in sorted_kws:
        if len(kw) < 2: continue
        link_html = f'<span class="wiki-link" onclick="window.parent.postMessage({{type:\'wiki_search\', query:\'{kw}\'}}, \'*\')">{kw}</span>'
        processed = processed.replace(kw, link_html)
    return processed

st.markdown(get_station_header(
    title="🌌 MANDALA MATRIX",
    subtitle="構造化された知識の多層曼荼羅",
    channel_id="MM.01"
), unsafe_allow_html=True)

if not nodes:
    st.warning("マトリックスにデータが見つかりません。")
else:
    # --- Structural Clustering (Mandala Logic) ---
    # Divide nodes by type and keywords to create "Islands"
    df_nodes = pd.DataFrame(nodes)
    
    # Calculate positions based on Similarity Islands, not arbitrary axes
    if RUST_AVAILABLE:
        contents_titles = [(n['content'], n['title']) for n in nodes]
        # We still use analyze_3d for raw coords, but we'll snap them to a Grid
        raw_positions = vectis_core.batch_analyze_3d(contents_titles)
    else:
        raw_positions = [(np.random.normal(0, 20), np.random.normal(0, 20), np.random.normal(0, 20)) for _ in nodes]

    # Snap to Mandala Grid (3D Blocks)
    grid_size = 15
    x = np.array([round(p[0] / grid_size) * grid_size for p in raw_positions])
    y = np.array([round(p[1] / grid_size) * grid_size for p in raw_positions])
    z = np.array([round(p[2] / grid_size) * grid_size for p in raw_positions])

    # Color Mapping
    color_map = {
        'Knowledge': '#00E5FF', 
        'Diary': '#FFBB00', 
        'YouTube': '#FF3366', 
        'Identity': '#CC00FF',
        'AgentLog': '#00FF99',
        'Synapse': '#FFD700',
        'DimensionRift': '#FF00FF' # Neon Purple for Rifts/Dreams
    }
    colors = [color_map.get(n['type'], '#FFFFFF') for n in nodes]
    
    fig = go.Figure()

    # MANDALA STRUCTURE: Clean grid lines (Optional/Subtle)
    # Removing "creepy lines". Only showing nodes.
    
    # NODES: Pulsing Data Points
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z, mode='markers',
        marker=dict(
            size=sphere_size, color=colors, opacity=0.9,
            line=dict(color='rgba(255,255,255,0.5)', width=1)
        ),
        text=[n['title'] for n in nodes],
        customdata=[n.get('id', '') for n in nodes],
        hoverinfo='text'
    ))
    
    # CONNECTIONS: Sequence of Agent Logs
    agent_nodes = [i for i, n in enumerate(nodes) if n['type'] == 'AgentLog']
    if len(agent_nodes) > 1:
        # Sort by mtime (if available) or order
        agent_nodes.sort(key=lambda i: nodes[i].get('mtime', 0))
        cx, cy, cz = [], [], []
        for i in range(len(agent_nodes)-1):
            idx1, idx2 = agent_nodes[i], agent_nodes[i+1]
            cx.extend([x[idx1], x[idx2], None])
            cy.extend([y[idx1], y[idx2], None])
            cz.extend([z[idx1], z[idx2], None])
        
        fig.add_trace(go.Scatter3d(
            x=cx, y=cy, z=cz, mode='lines',
            line=dict(color='#00FF99', width=2, dash='dot'),
            opacity=0.3, hoverinfo='none', name='Mission Path'
        ))

    # Layout: Dark Station Style
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="", showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(title="", showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(title="", showgrid=False, zeroline=False, showticklabels=False),
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=600,
        showlegend=False
    )
    
    # --- Double Click & Click Handler (JS Injection) ---
    st.plotly_chart(fig, use_container_width=True, key="mandala_chart")

    # JavaScript to handle double clicks and jumps
    st.components.v1.html(f"""
    <script>
        const chart = window.parent.document.querySelector('div[data-testid="stPlotlyChart"]');
        if (chart) {{
            chart.addEventListener('dblclick', function() {{
                // Detect which point was clicked via Streamlit/Plotly bridge
                // Since pure double-click handling in Streamlit is limited,
                // we'll trigger a message to the parent to check selection.
                window.parent.postMessage({{type: 'mandala_dblclick'}}, '*');
            }});
        }}
    </script>
    """, height=0)

    # UI: Detail HUD Panel
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    col_hud1, col_hud2 = st.columns([1, 2])
    
    with col_hud1:
        st.markdown("### 🛰️ NODE SELECTOR")
        selected_title = st.selectbox("マトリックスから選択", [n['title'] for n in nodes])
        selected_node = next(n for n in nodes if n['title'] == selected_title)
        
        # Determine target URL
        jump_urls = {
            'Knowledge': "http://localhost:8517", # To Job HQ/Scout
            'Diary': "http://localhost:8503",
            'Identity': "http://localhost:8519",
            'YouTube': "http://localhost:8501"
        }
        target_url = jump_urls.get(selected_node['type'], "#")

        st.markdown(f"""
        <div style="margin-top:20px;">
            <span class="rarity-tag" style="background: rgba(0,229,255,0.2); color: #00E5FF; border: 1px solid #00E5FF;">
                {selected_node['type']}
            </span>
            <a href="{target_url}" target="_blank" style="text-decoration:none;">
                <button style="
                    background: #00FFCC; 
                    color: #000; 
                    border: none; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold; 
                    width: 100%; 
                    cursor: pointer;
                    margin-top: 15px;
                    font-family: 'Share Tech Mono', monospace;
                ">
                    🚀 JUMP TO SOURCE
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    with col_hud2:
        st.markdown(f"#### 🛰️ DATA STREAM: {selected_node['title']}")
        
        # Masao AI Style Logic
        if selected_node['type'] == 'AgentLog':
            st.markdown(f"""
            <div style="background: rgba(0, 255, 153, 0.1); border-left: 4px solid #00FF99; padding: 10px; margin-bottom: 15px;">
                <b>[まさおAI じっくり解説] 代行行動の記録</b><br>
                エージェントが自律的に実行したステップです。
            </div>
            """, unsafe_allow_html=True)
            
        if selected_node['type'] == 'Synapse':
             st.markdown(f"""
            <div style="background: rgba(255, 215, 0, 0.1); border-left: 4px solid #FFD700; padding: 10px; margin-bottom: 15px;">
                <b>[まさおAI じっくり解説] 知識の結合（シナプス）</b><br>
                これは驚くべき発見です。異なるソースから、AIが共通項を見出しました。
            </div>
            """, unsafe_allow_html=True)
            
        if selected_node['type'] == 'DimensionRift':
             st.markdown(f"""
            <div style="background: rgba(255, 0, 255, 0.15); border: 1px solid #FF00FF; padding: 10px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(255,0,255,0.3);">
                <b style="color:#FF00FF;">[まさおAI じっくり解説] 次元の裂け目（RIFT）</b><br>
                警告：これは現在の現実ではなく、「あり得たかもしれない未来」の断片です。
                エージェントの深層思考（夢）から生成された、極端な推論結果です。
            </div>
            """, unsafe_allow_html=True)
            
        wiki_content = apply_wiki_links(selected_node['content'])
        st.markdown(f"""
        <div style="color: #ccc; font-family: 'Share Tech Mono', monospace; font-size: 0.9em; height: 200px; overflow-y: auto; padding-right:10px; line-height:1.6;">
            {wiki_content.replace('\n', '<br>')}
        </div>
        <style>
            .wiki-link {{
                color: #00FFCC;
                border-bottom: 1px dotted #00FFCC;
                cursor: pointer;
            }}
            .wiki-link:hover {{
                background: rgba(0, 255, 204, 0.2);
            }}
        </style>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---")
render_station_footer()

st.markdown("---")
render_station_footer()
