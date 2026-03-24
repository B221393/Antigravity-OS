"""
📺 VECTIS HUB - 自分ステーション・ダッシュボード
=============================================
Port: 8501
全アプリの司令塔となるメインハブ。
YouTubeの新規性分析結果や、各チャンネルへのクイックアクセスを提供。
"""

import streamlit as st
import json
import os
import sys
import random
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import glob
import re

# Load Env
load_dotenv("../../.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Module Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header
from modules.vision_action import VisionAgent

# Try to import Rust-powered core (10-50x faster)
try:
    from modules import vectis_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

# Config
st.set_page_config(page_title="📺 VECTIS HUB | 自分ステーション", page_icon="📺", layout="wide")
apply_vectis_style()

# Custom CSS for VECTIS ARK HUD (Premium SF style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;500;700&family=Oswald:wght@400;700&display=swap');

    body, p, span, div, .stMarkdown {
        font-family: 'Roboto Mono', monospace !important;
        color: #E0F7FA !important;
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #05101a 0%, #000205 100%) !important;
    }

    /* Fixed Top/Bottom Bar simulation */
    .stHeader {
        background: rgba(0, 0, 0, 0) !important;
    }

    /* Floating HUD Console (Bottom) */
    .hud-bottom-console {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 120px;
        background: linear-gradient(180deg, rgba(0, 255, 255, 0.05) 0%, rgba(0, 50, 70, 0.5) 100%);
        border-top: 2px solid #00FFFF;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
        clip-path: polygon(0% 20%, 5% 0%, 95% 0%, 100% 20%, 100% 100%, 0% 100%);
    }

    .hud-console-content {
        display: flex;
        gap: 40px;
        color: #00FFFF;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.8rem;
    }

    .hud-stat-box {
        border-left: 2px solid #00FFFF;
        padding-left: 10px;
    }

    .hud-stat-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #fff;
        text-shadow: 0 0 10px #00FFFF;
    }

    /* Node Inspector - SF Hologram HUD Style */
    .node-inspector {
        position: fixed;
        top: 15%;
        right: 30px;
        width: 320px;
        background: rgba(5, 15, 25, 0.4);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 2px solid var(--genre-color, #00FFFF);
        padding: 20px;
        clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px));
        box-shadow: 
            0 0 30px var(--genre-color, #00FFFF),
            inset 0 0 60px rgba(0, 255, 255, 0.05),
            0 8px 32px rgba(0, 0, 0, 0.6);
        z-index: 1000;
        animation: hologram-flicker 3s infinite alternate;
        font-family: 'Roboto Mono', monospace;
    }
    
    .node-inspector::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, 
            transparent 0%, 
            var(--genre-color, #00FFFF) 50%, 
            transparent 100%);
        clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px));
        opacity: 0.3;
        z-index: -1;
        filter: blur(8px);
    }
    
    .node-inspector::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            rgba(255, 255, 255, 0.03) 0px,
            transparent 1px,
            transparent 2px,
            rgba(255, 255, 255, 0.03) 3px
        );
        pointer-events: none;
        animation: scanline-move 8s linear infinite;
    }
    
    @keyframes hologram-flicker {
        0%, 100% { opacity: 0.95; }
        50% { opacity: 1; }
    }
    
    @keyframes scanline-move {
        0% { transform: translateY(0); }
        100% { transform: translateY(20px); }
    }
    
    .node-inspector-header {
        font-size: 0.65rem;
        letter-spacing: 2px;
        opacity: 0.5;
        margin-bottom: 12px;
        text-transform: uppercase;
        color: var(--genre-color, #00FFFF);
        text-shadow: 0 0 8px var(--genre-color, #00FFFF);
    }
    
    .node-inspector-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--genre-color, #00FFFF);
        margin-bottom: 12px;
        line-height: 1.3;
        text-shadow: 
            0 0 15px var(--genre-color, #00FFFF),
            0 0 30px var(--genre-color, rgba(0, 255, 255, 0.4));
        animation: title-glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes title-glow {
        0% { filter: brightness(1); }
        100% { filter: brightness(1.15); }
    }
    
    .node-inspector-watch-label {
        font-size: 0.7rem;
        opacity: 0.8;
        margin-bottom: 6px;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .node-inspector-watch-label::before {
        content: '▶';
        color: var(--genre-color, #00FFFF);
        font-size: 0.6rem;
    }

    /* Scanline effect */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        z-index: 9999;
        background-size: 100% 4px, 3px 100%;
        pointer-events: none;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(0,255,255,0.05);
        border: 1px solid rgba(0,255,255,0.2) !important;
        border-radius: 4px 4px 0 0;
        color: #00FFFF !important;
    }
    /* Vignette Overlay */
    .stApp::after {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: radial-gradient(circle, transparent 50%, rgba(0,0,0,0.8) 120%);
        z-index: 10001;
        pointer-events: none;
    }


    .progress-bar-container {
        height: 12px;
        background: rgba(0, 0, 0, 0.4);
        margin: 10px 0 20px 0;
        border-radius: 2px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
    }
    
    .progress-bar-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 255, 255, 0.1) 50%, 
            transparent 100%);
        animation: progress-shimmer 2s infinite;
    }
    
    @keyframes progress-shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, 
            var(--genre-color, #00FFFF) 0%, 
            var(--genre-color-light, #66FFFF) 50%,
            var(--genre-color, #00FFFF) 100%);
        box-shadow: 
            0 0 20px var(--genre-color, #00FFFF),
            0 0 40px var(--genre-color, rgba(0, 255, 255, 0.5)),
            inset 0 0 10px rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 255, 255, 0.4) 50%, 
            transparent 100%);
        animation: progress-glow 1.5s infinite;
    }
    
    @keyframes progress-glow {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(200%); }
    }
    
    .node-inspector-details {
        font-size: 0.7rem;
        line-height: 1.8;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .node-inspector-detail-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }
    
    .node-inspector-detail-item::before {
        content: '◆';
        color: var(--genre-color, #00FFFF);
        font-size: 0.5rem;
        opacity: 0.6;
    }
    
    .node-inspector-energy-line {
        position: absolute;
        width: 2px;
        height: 60px;
        background: linear-gradient(180deg, 
            var(--genre-color, #00FFFF) 0%, 
            transparent 100%);
        top: -60px;
        left: 50%;
        transform: translateX(-50%);
        box-shadow: 0 0 10px var(--genre-color, #00FFFF);
        animation: energy-pulse 2s ease-in-out infinite;
    }
    
    @keyframes energy-pulse {
        0%, 100% { opacity: 0.6; height: 60px; }
        50% { opacity: 1; height: 80px; }
    }
</style>
""", unsafe_allow_html=True)

# Paths
BASE_DIR = Path(__file__).parents[2]
SCORES_FILE = BASE_DIR / "AUTO_YOUTUBE" / "novelty_scores_v2.json"
NOTES_DIR = BASE_DIR / "apps" / "memory" / "data" / "youtube_notes"

# --- Data Loading ---
@st.cache_data(ttl=600)
def load_youtube_data():
    if SCORES_FILE.exists():
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            return None
    return None

def load_note_content(filename):
    """Load the markdown content of a potential note file."""
    # File name in JSON is like "YouTube_....md"
    # It should be in NOTES_DIR
    note_path = NOTES_DIR / filename
    if note_path.exists():
        with open(note_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# --- Main Interface ---

def main():
    # Sidebar
    with st.sidebar:
        render_global_road()
        st.markdown("---")
        
        # --- MINECRAFT STYLE SORTER ---
        st.markdown('<p class="sorter-title">📦 VECTIS INTAKE (自動分別機)</p>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="sorter-box">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("搬入口 (Image Only)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True, caption="スキャン待機中...")
                
                if st.button("🚀 分別開始 (SCAN)", use_container_width=True):
                    if not GEMINI_API_KEY:
                        st.error("API Key missing in .env")
                    else:
                        with st.spinner("📦 AIが分類先を計算中..."):
                            agent = VisionAgent(GEMINI_API_KEY)
                            result = agent.image_to_knowledge(img)
                            
                            if "status" in result and result["status"] == "ERROR":
                                st.error(f"Error: {result.get('message')}")
                            else:
                                # Minecraft-style Sorting Logic
                                cat = result.get("category", "KNOWLEDGE")
                                title = result.get("title", "Scanned Data")
                                content = result.get("content", "")
                                rarity = result.get("rarity", "Common")
                                
                                st.success(f"📦 分別完了: {cat}")
                                st.markdown(f"**{title}**")
                                st.caption(f"レア度: {rarity} | 理由: {result.get('reason')}")
                                
                                # Saving Logic
                                success = False
                                if cat == "JOB_HUNTING":
                                    save_dir = BASE_DIR / "apps" / "job_hunting" / "scanned"
                                    os.makedirs(save_dir, exist_ok=True)
                                    filename = f"scan_{int(datetime.now().timestamp())}.kcard"
                                    with open(save_dir / filename, "w", encoding="utf-8") as f:
                                        json.dump({"title": title, "content": content, "genre": "Scanned", "rarity": rarity, "created": datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
                                    success = True
                                elif cat == "DIARY":
                                    diary_file = BASE_DIR / "apps" / "diary" / "data" / "entries.json"
                                    os.makedirs(diary_file.parent, exist_ok=True)
                                    entries = []
                                    if diary_file.exists():
                                        with open(diary_file, "r", encoding="utf-8") as f:
                                            entries = json.load(f)
                                    entries.append({"title": title, "content": content, "date": datetime.now().isoformat()})
                                    with open(diary_file, "w", encoding="utf-8") as f:
                                        json.dump(entries, f, indent=2, ensure_ascii=False)
                                    success = True
                                else: # KNOWLEDGE
                                    save_dir = BASE_DIR / "apps" / "memory" / "data" / "youtube_notes"
                                    os.makedirs(save_dir, exist_ok=True)
                                    filename = f"knowledge_{int(datetime.now().timestamp())}.md"
                                    with open(save_dir / filename, "w", encoding="utf-8") as f:
                                        f.write(f"# 📺 {title}\n\n{content}\n\n*Scanned via VECTIS Sorter*")
                                    success = True
                                
                                if success:
                                    st.balloons()
                                    st.toast("チェストに格納しました！", icon="📦")
                                    
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("🧠 AGI INTERNAL MONOLOGUE")
        # Generate some thoughts based on recent synapses
        synapses = glob.glob(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned" / "*.synapse"))
        latest_thought = "Scanning Knowledge Galaxy for connections..."
        if synapses:
            latest_f = max(synapses, key=os.path.getmtime)
            with open(latest_f, "r", encoding="utf-8") as f:
                s_data = json.load(f)
                latest_thought = f"Detected connection: {s_data.get('title')}"
        
        st.markdown(f"""
        <div style="background:rgba(204, 255, 0, 0.05); border:1px solid rgba(204,255,0,0.2); padding:10px; border-radius:8px; font-family:'Share Tech Mono'; font-size:0.75rem; color:#CCFF00;">
            <span style="color:#ff3333;">&#9654;</span> {latest_thought}<br>
            <span style="color:#ff3333;">&#9654;</span> 次のフェーズ: 就活イベント情報の自動マッピングの検討中...
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("🚨 EMERGENCY DEADLINE")
        # Kodansha Jan 13 12:00
        kd_deadline = datetime(2026, 1, 13, 12, 0)
        kd_delta = kd_deadline - datetime.now()
        kd_days = kd_delta.days
        kd_hours = kd_delta.seconds // 3600
        
        st.markdown(f"""
        <div style="background:rgba(255, 51, 102, 0.1); border:1px solid #FF3366; padding:10px; border-radius:8px;">
            <b style="color:#FF3366;">講談社 ES提出〆切まで</b><br>
            <span style="font-family:'Share Tech Mono'; font-size:1.2rem; color:#fff;">
                {kd_days}d {kd_hours}h REMAINING
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("🎯 CURRENT FOCUS: TOEIC")
        st.info("自律ちゃん稼働中: 講談社に向けた英語戦略を構築しています。")

        st.markdown("---")
        st.caption("SYSTEM INFO")
        st.code(f"USER: Yuto\nOS: VECTIS 2.0\nPORT: 8501\nMODE: AGI_AUTONOMY", language="yaml")

    # Header
    st.markdown(get_station_header(
        title="VECTIS HUB",
        subtitle="自分ステーション・コントロールセンター",
        channel_id="HUB.01"
    ), unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🌟 YouTube Analysis", "🚀 Applications", "🏹 System Mission"])

    # --- Tab 1: YouTube High Novelty Picks ---
    with tab1:
        st.markdown("### 🌟 独創的コンテンツ・ピックアップ")
        st.markdown("AIが発見した「新規性が高い」動画サマリー。知の探求を加速させる。")
        
        col_ctrl1, col_ctrl2 = st.columns([3, 1])
        with col_ctrl2:
            if st.button("🔄 最新データをロード", key="btn_reload_data"):
                load_youtube_data.clear()
                st.rerun()

        yt_data = load_youtube_data()
        
        if yt_data:
            scores = yt_data.get("scores", {})
            
            # Convert to list
            items = []
            for filename, info in scores.items():
                items.append({
                    "filename": filename,
                    "title": info.get("title", "No Title"),
                    "topic": info.get("topic", "Unknown"),
                    "score": info.get("novelty_score", 0)
                })
            
            # Filtering
            topics = sorted(list(set([i["topic"] for i in items])))
            with col_ctrl1:
                selected_topic = st.selectbox("Topic Filter", ["All"] + topics, index=0)
            
            if selected_topic != "All":
                items = [i for i in items if i["topic"] == selected_topic]

            # Sort by score descending
            items = sorted(items, key=lambda x: x["score"], reverse=True)
            
            # Pagination or Limit
            # Showing top 12
            top_items = items[:12]
            
            # Display Grid
            cols = st.columns(3)
            for idx, item in enumerate(top_items):
                with cols[idx % 3]:
                    score_val = item['score']
                    score_color = "#CCFF00" if score_val >= 1.0 else "#00AAFF"
                    score_formatted = f"{score_val:.2f}"
                    
                    st.markdown(f"""
                    <div class="station-card" style="height: 220px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <span class="station-badge" style="margin-bottom: 8px;">{item['topic']}</span>
                            <div style="font-size: 1.0rem; font-weight: 700; line-height: 1.4; margin-top: 8px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                                {item['title']}
                            </div>
                        </div>
                        <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 12px; padding-top: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-family: monospace; color: {score_color}; font-size: 0.9rem;">NOVELTY: {score_formatted}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Read Content Button
                    if st.button("📄 内容を読む", key=f"btn_read_{idx}"):
                        content = load_note_content(item['filename'])
                        if content:
                            st.info(f"Summary for: {item['title']}")
                            st.markdown(content)
                        else:
                            st.warning("Note file not found locally.")

        else:
            st.info("YouTube分析データがまだありません。RUN_WATCHER.bat を実行してください。")
            
        # --- 3D MANDALA MATRIX VISUALIZATION ---
        st.markdown("---")
        st.markdown("### 🌌 曼荼羅マトリックス (MANDALA MATRIX)")
        st.markdown("YouTube動画と知識を構造化して視覚化。**ダブルクリックでソースへジャンプ**、**Wikiリンクで連鎖検索**")
        
        # HUD Floating Console (Inject at the end of the script usually, but we can do it here)
        st.markdown(f"""
        <div class="hud-bottom-console">
            <div class="hud-console-content">
                <div class="hud-stat-box">
                    <div style="font-size: 0.6rem;">MEMORY_STABILITY</div>
                    <div class="hud-stat-value">98.4%</div>
                </div>
                <div class="hud-stat-box">
                    <div style="font-size: 0.6rem;">NODE_DENSITY</div>
                    <div class="hud-stat-value">{len(load_youtube_data()) if 'load_youtube_data' in locals() else 0}</div>
                </div>
                <div class="hud-stat-box">
                    <div style="font-size: 0.6rem;">SYSTEM_UPTIME</div>
                    <div class="hud-stat-value">{'00:42:01'}</div>
                </div>
                <div class="hud-stat-box" style="border-right: 2px solid #00FFFF; padding-right: 10px;">
                    <div style="font-size: 0.6rem;">NEURAL_LOAD</div>
                    <div class="hud-stat-value">LOW</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🖥️ HUD SETTINGS")
            max_nodes = st.slider("NODES_CAP", 10, 200, 60)
            sphere_size = st.slider("CORE_INTENSITY", 3, 15, 8)
            bloom_intensity = st.slider("BLOOM_ALPHA", 0.05, 0.4, 0.15)
            
        show_lines = False
            
        try:
            # Inline data loading function with recency
            def dashboard_load_nodes_v2():
                nodes = []
                base_dir = Path(__file__).parents[1]
                
                # 1. YouTube Notes (.md)
                youtube_pattern = base_dir / "memory" / "data" / "youtube_notes" / "*.md"
                for i, f in enumerate(glob.glob(str(youtube_pattern))):
                    try:
                        mtime = os.path.getmtime(f)
                        with open(f, "r", encoding="utf-8") as f_in:
                            content = f_in.read()
                            lines_raw = content.split('\n')
                            title = lines_raw[0].replace('# 📺 ', '').strip() if lines_raw else "YouTube"
                            keywords = set(re.findall(r'[a-zA-Z]{4,}|[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}', content.lower()))
                            url_match = re.search(r'URL:\s*(https?://\S+)', content)
                            nodes.append({
                                "id": f"Y_{i}",
                                "title": title[:50], "type": "YouTube", "content": content,
                                "mtime": mtime, "keywords": keywords, "url": url_match.group(1) if url_match else "", "filepath": f
                            })
                    except: pass
                
                # 2. Knowledge Cards (.kcard)
                kcard_pattern = base_dir / "apps" / "job_hunting" / "scanned" / "*.kcard"
                for i, f in enumerate(glob.glob(str(kcard_pattern))):
                    try:
                        mtime = os.path.getmtime(f)
                        with open(f, "r", encoding="utf-8") as f_in:
                            data = json.load(f_in)
                            nodes.append({
                                "id": f"K_{i}",
                                "title": data.get("title", "K-Card")[:50], "type": data.get("genre", "Knowledge"),
                                "content": data.get("content", ""), "mtime": mtime, "keywords": set(), "url": data.get("url", ""), "filepath": f
                            })
                    except: pass

                # 3. Compressed Nodes (.vcc)
                vcc_pattern = base_dir / "apps" / "job_hunting" / "scanned" / "*.vcc"
                for i, f in enumerate(glob.glob(str(vcc_pattern))):
                    try:
                        mtime = os.path.getmtime(f)
                        from modules import vectis_core
                        with open(f, "rb") as f_in:
                            raw_bin = f_in.read()
                            decompressed = vectis_core.decompress_data(raw_bin)
                            if decompressed:
                                data = json.loads(decompressed)
                                nodes.append({
                                    "id": f"V_{i}",
                                    "title": data.get("title", "Compressed Core")[:50], "type": "NeuralSeed",
                                    "content": data.get("content", ""), "mtime": mtime, "keywords": set(), "url": data.get("url", ""), "filepath": f
                                })
                    except: pass
                
                return nodes
            
            # Analysis function
            def dashboard_analyze_v2(node):
                content = node['content'].lower()
                title = node['title'].lower()
                combined = content + title
                
                ent_kw = ['おもしろ', '笑', '雑談', 'ネタ', '爆笑', 'エンタメ', '面白', 'ゆる']
                aca_kw = ['研究', '論文', '理論', '分析', '専門', '学術', '科学', '哲学']
                x = sum(5 for k in ent_kw if k in combined) - sum(5 for k in aca_kw if k in combined)
                
                easy_kw = ['初心者', '簡単', 'わかりやすい', '入門', '基礎']
                hard_kw = ['高度', '専門的', '難解', '複雑', '詳細']
                y = sum(5 for k in hard_kw if k in combined) - sum(5 for k in easy_kw if k in combined) + min(len(content)/1000, 20)
                
                theo_kw = ['なぜ', '考察', '歴史', '起源', '概念']
                prac_kw = ['方法', 'やり方', 'コツ', '実践', '活用']
                z = sum(5 for k in prac_kw if k in combined) - sum(5 for k in theo_kw if k in combined)
                
                return x, y, z
            
            # Similarity function
            def keyword_similarity(n1, n2):
                if not n1['keywords'] or not n2['keywords']:
                    return 0
                intersection = len(n1['keywords'] & n2['keywords'])
                union = len(n1['keywords'] | n2['keywords'])
                return intersection / union if union > 0 else 0
            
            all_nodes = dashboard_load_nodes_v2()
            
            if all_nodes:
                # Random sampling for clarity
                if len(all_nodes) > max_nodes:
                    nodes = random.sample(all_nodes, max_nodes)
                else:
                    nodes = all_nodes
                
                # Sort by recency for color gradient
                min_time = min(n['mtime'] for n in nodes)
                max_time = max(n['mtime'] for n in nodes)
                time_range = max_time - min_time if max_time > min_time else 1
                
                # === QUADRANT NEURAL TREE LAYOUT ===
                # Quadrant colors: Programming(Cyan), Philosophy(Purple), Languages(Orange), History(Green)
                quad_map = {
                    0: {"color": "#00FFFF", "name": "PROGRAMMING", "angle": 0.75 * np.pi}, # Top Left
                    1: {"color": "#FF00FF", "name": "PHILOSOPHY", "angle": 0.25 * np.pi}, # Top Right
                    2: {"color": "#FFA500", "name": "LANGUAGES", "angle": 1.25 * np.pi}, # Bottom Left
                    3: {"color": "#00FF00", "name": "HISTORY", "angle": 1.75 * np.pi}    # Bottom Right
                }
                
                new_x, new_y, new_z = [], [], []
                trunk_x, trunk_y, trunk_z = [], [], []
                branch_x, branch_y, branch_z = [], [], []
                leaf_line_x, leaf_line_y, leaf_line_z = [], [], []
                syn_x, syn_y, syn_z = [], [], []
                
                final_nodes = []
                final_colors = []
                
                categories = sorted(list(set(n['type'] for n in nodes)))
                
                for c_idx, cat in enumerate(categories):
                    q_idx = c_idx % 4
                    q_conf = quad_map[q_idx]
                    angle_base = q_conf["angle"]
                    
                    r_hub = 150
                    cx, cy = r_hub * np.cos(angle_base), r_hub * np.sin(angle_base)
                    cz = np.random.uniform(-30, 30)
                    
                    # Trunk with Quadrant Color
                    trunk_x.extend([0, cx, None]); trunk_y.extend([0, cy, None]); trunk_z.extend([0, cz, None])
                    
                    cat_items = [n for n in nodes if n['type'] == cat]
                    n_sub = 2 if len(cat_items) > 5 else 1
                    
                    for s_idx in range(n_sub):
                        s_angle = angle_base + (s_idx - (n_sub-1)/2) * 0.5
                        r_s = 70
                        sx, sy = cx + r_s * np.cos(s_angle), cy + r_s * np.sin(s_angle)
                        sz = cz + np.random.uniform(-50, 50)
                        branch_x.extend([cx, sx, None]); branch_y.extend([cy, sy, None]); branch_z.extend([cz, sz, None])
                        
                        sub_items = cat_items[s_idx::n_sub]
                        for i_idx, node in enumerate(sub_items):
                            phi = (2 * np.pi * i_idx) / (len(sub_items) or 1)
                            theta = np.random.uniform(0.1, 1.4)
                            r_l = 50
                            lx = sx + r_l * np.sin(theta) * np.cos(phi)
                            ly = sy + r_l * np.sin(theta) * np.sin(phi)
                            lz = sz + r_l * np.cos(theta)
                            
                            new_x.append(lx); new_y.append(ly); new_z.append(lz)
                            leaf_line_x.extend([sx, lx, None]); leaf_line_y.extend([sy, ly, None]); leaf_line_z.extend([sz, lz, None])
                            final_nodes.append(node)
                            final_colors.append(q_conf["color"])

                x, y, z = np.array(new_x), np.array(new_y), np.array(new_z)
                
                fig = go.Figure()

                # Structural Layers
                fig.add_trace(go.Scatter3d(x=trunk_x, y=trunk_y, z=trunk_z, mode='lines', line=dict(color='rgba(0,255,255,0.4)', width=5), hoverinfo='none', name='Trunks'))
                fig.add_trace(go.Scatter3d(x=branch_x, y=branch_y, z=branch_z, mode='lines', line=dict(color='rgba(0,255,255,0.2)', width=3), hoverinfo='none', name='Branches'))
                fig.add_trace(go.Scatter3d(x=leaf_line_x, y=leaf_line_y, z=leaf_line_z, mode='lines', line=dict(color='rgba(0,255,255,0.1)', width=1), hoverinfo='none', name='Filaments'))

                # Category Hubs (Hexagonal look)
                hub_x, hub_y, hub_z, hub_colors = [], [], [], []
                for c_idx, cat in enumerate(categories):
                    q_idx = c_idx % 4
                    angle_base = quad_map[q_idx]["angle"]
                    r_hub = 150
                    hub_x.append(r_hub * np.cos(angle_base))
                    hub_y.append(r_hub * np.sin(angle_base))
                    hub_z.append(0)
                    hub_colors.append(quad_map[q_idx]["color"])
                
                fig.add_trace(go.Scatter3d(x=hub_x, y=hub_y, z=hub_z, mode='markers+text', 
                    marker=dict(size=25, color=hub_colors, symbol='diamond-open', line=dict(color='white', width=2)),
                    text=[quad_map[i%4]["name"] for i in range(len(categories))], textposition="bottom center",
                    textfont=dict(color="white", size=10), name='Category Hubs'))

                # Neural Core
                fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                    marker=dict(size=50, color='#00FFFF', opacity=0.1, symbol='circle'), hoverinfo='none'))
                fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                    marker=dict(size=20, color='#FFFFFF', symbol='diamond', line=dict(color='#00FFFF', width=3)), name='CORE_SELF'))

                # Memory Nodes with Bloom
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers',
                    marker=dict(size=sphere_size * 2, color=final_colors, opacity=bloom_intensity), hoverinfo='none'))
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers',
                    marker=dict(size=sphere_size, color=final_colors, opacity=0.9, line=dict(color='white', width=1)),
                    text=[f"{n['title']}" for n in final_nodes],
                    customdata=[n.get('url', '') for n in final_nodes],
                    hoverinfo='text', name='Memories'))
                
                fig.update_layout(
                    scene=dict(
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
                        zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
                        bgcolor="rgba(0,0,0,0)",
                        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
                    ),
                    margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor="rgba(0,0,0,0)", height=700, showlegend=False
                )
                
                # Floating Node Inspector - SF Hologram HUD
                # Expanded genre color mapping with granular categories
                genre_colors = {
                    'ai_tech': {'color': '#00FFFF', 'light': '#66FFFF'},           # Cyan - AI/Tech
                    'language': {'color': '#FF6B35', 'light': '#FF9966'},          # Orange - Language/Linguistics
                    'philosophy': {'color': '#B565D8', 'light': '#D499F0'},        # Purple - Philosophy
                    'science': {'color': '#00FF88', 'light': '#66FFAA'},           # Green - Science
                    'geopolitics': {'color': '#FFD700', 'light': '#FFE44D'},       # Gold - Geopolitics
                    'news': {'color': '#FF3366', 'light': '#FF6699'},              # Pink/Red - News
                    'product': {'color': '#00AAFF', 'light': '#66CCFF'},           # Light Blue - Product Reviews
                    'quantum': {'color': '#9D4EDD', 'light': '#C77DFF'},           # Violet - Quantum Computing
                    'education': {'color': '#06FFA5', 'light': '#4DFFB8'},         # Mint - Education
                    'culture': {'color': '#FFB627', 'light': '#FFC857'},           # Amber - Culture/Society
                    'default': {'color': '#888888', 'light': '#AAAAAA'}            # Gray - Other
                }
                
                # Topic to genre mapping function with granular categories
                def map_topic_to_genre(topic_or_genre):
                    """Map topic/genre string to color category with granular classification"""
                    topic_lower = str(topic_or_genre).lower()
                    
                    # Quantum Computing (most specific, check first)
                    if any(kw in topic_lower for kw in ['quantum', '量子']):
                        return 'quantum'
                    
                    # AI/Tech keywords (check before Education to prioritize AI content)
                    elif any(kw in topic_lower for kw in ['ai', 'gemini', 'chatgpt', 'プログラミング', 'programming', 'python', 'rust', 'tech', 'code', 'developer', 'エンジニア', '開発', 'robot', 'ロボット', 'deeplearning', '機械学習', 'neural']):
                        return 'ai_tech'
                    
                    # Language/Linguistics keywords
                    elif any(kw in topic_lower for kw in ['言語', 'language', '英語', 'english', 'toeic', '語学', '外国語', '言語学', 'linguistic', 'ラジオ']):
                        return 'language'
                    
                    # Philosophy/Humanities keywords
                    elif any(kw in topic_lower for kw in ['哲学', 'philosophy', '思想', '人文', '心理', 'psychology']):
                        return 'philosophy'
                    
                    # Science keywords
                    elif any(kw in topic_lower for kw in ['科学', 'science', '物理', '化学', '生物', '数学', 'math', 'physics']):
                        return 'science'
                    
                    # Geopolitics keywords
                    elif any(kw in topic_lower for kw in ['地政学', 'geopolit', '国際', 'international']):
                        return 'geopolitics'
                    
                    # News keywords
                    elif any(kw in topic_lower for kw in ['ニュース', 'news', 'google', 'tbs', 'dig']):
                        return 'news'
                    
                    # Product/Device Reviews
                    elif any(kw in topic_lower for kw in ['pixel', 'product', '紹介', 'review', 'unbox']):
                        return 'product'
                    
                    # Culture/Society
                    elif any(kw in topic_lower for kw in ['文化', 'culture', '社会', 'society', '歴史', 'history']):
                        return 'culture'
                    
                    # Business keywords
                    elif any(kw in topic_lower for kw in ['ビジネス', 'business', '経営', '就活', 'job', 'career', '企業', '経済']):
                        return 'geopolitics'  # Using geopolitics color for business
                    
                    # Education/Tutorial (check after AI to avoid misclassification)
                    elif any(kw in topic_lower for kw in ['使い方', 'tutorial', 'how to', '解説', '入門', '学習']):
                        return 'education'
                    
                    return 'default'
                
                # Select a random node to display from YouTube data
                yt_data = load_youtube_data()
                if yt_data and final_nodes:
                    scores = yt_data.get("scores", {})
                    if scores:
                        # Get a random YouTube entry
                        random_key = random.choice(list(scores.keys()))
                        yt_entry = scores[random_key]
                        
                        # Get topic from YouTube data
                        node_topic = yt_entry.get('topic', 'Unknown')
                        selected_genre = map_topic_to_genre(node_topic)
                        genre_color = genre_colors.get(selected_genre, genre_colors['default'])
                        
                        # Extract display information
                        node_title = yt_entry.get('title', 'Unknown Node')
                        
                        # Calculate mock watch percentage (based on novelty score)
                        novelty_score = yt_entry.get('novelty_score', 0.5)
                        watch_percent = int(60 + (novelty_score * 40))  # 60-100% range
                        
                        st.markdown(f"""
                        <style>
                            .node-inspector {{
                                --genre-color: {genre_color['color']};
                                --genre-color-light: {genre_color['light']};
                            }}
                        </style>
                        <div class="node-inspector">
                            <div class="node-inspector-energy-line"></div>
                            <div class="node-inspector-header">NODE_INSPECTOR // ACTIVE_STREAM</div>
                            <div class="node-inspector-title">{node_title}</div>
                            <div class="node-inspector-watch-label">スコア: {watch_percent}%</div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: {watch_percent}%;"></div>
                            </div>
                            <div class="node-inspector-details">
                                <div class="node-inspector-detail-item">Genre: {selected_genre.upper()}</div>
                                <div class="node-inspector-detail-item">Topic: {node_topic}</div>
                                <div class="node-inspector-detail-item">Novelty: {novelty_score:.3f}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No YouTube data available")
                else:
                    # Fallback if no nodes
                    st.info("No nodes available for display")

                st.plotly_chart(fig, use_container_width=True, key="chart_knowledge_mandala")
                st.components.v1.html(r"""
                <script>
                    const chart = window.parent.document.querySelector('div[data-testid="stPlotlyChart"]');
                    if (chart) {
                        chart.addEventListener('dblclick', function() {
                            const plot = chart.querySelector('.js-plotly-plot');
                            if (plot && plot._hoverdata && plot._hoverdata.length > 0) {
                                const url = plot._hoverdata[0].customdata;
                                if (url && (url.startsWith('http') || url.startsWith('file'))) {
                                    window.parent.open(url, '_blank');
                                }
                            }
                        });
                    }
                    
                    // Auto Shutdown Heartbeat: Detect window close
                    window.addEventListener('beforeunload', function (e) {
                         // Send a terminal stop command if this is the last session
                         // For Streamlit, we cannot easily kill process from JS without a backend trigger,
                         // but we can log the exit for the Orchestrator to handle.
                         console.log("Streamlit Session Closing...");
                    });
                </script>
                """, height=0)
                
                # Wiki Link Support for Dashboard HUD
                def dashboard_wiki_links(text):
                    if not RUST_AVAILABLE: return text
                    keywords = vectis_core.extract_keywords(text)
                    processed = text
                    sorted_kws = sorted(list(keywords), key=len, reverse=True)
                    for kw in sorted_kws:
                        if len(kw) < 2: continue
                        link_html = f'<span style="color:#00FFCC; border-bottom:1px dotted #00FFCC; cursor:pointer;" title="連鎖検索: {kw}">{kw}</span>'
                        processed = processed.replace(kw, link_html)
                    return processed

                # Twitter-like detail panel (HUD Style)
                st.markdown('<div style="background:rgba(10,10,20,0.6); padding:20px; border-radius:15px; border:1px solid rgba(0,255,204,0.2);">', unsafe_allow_html=True)
                node_titles = [f"{i+1}. {n['title']}" for i, n in enumerate(nodes)]
                
                if st.button("🌌 フルスクリーンで探索", key="btn_launch_memory_3d"):
                     st.markdown(f'<meta http-equiv="refresh" content="0; url=http://localhost:8512">', unsafe_allow_html=True)
            else:
                st.info("No data for 3D map.")
        except Exception as e:
            st.error(f"3D Map Error: {e}")

    # --- Tab 2: VECTIS Apps ---
    with tab2:
        st.markdown("### 🏗️ VECTIS Applications Dashboard")
        
        # Categorized Apps matching modules/nav.py + known apps
        app_categories = {
            "Job Hunting (就活)": [
                {"name": "🎖️ 就活司令部", "port": 8517, "desc": "Job HQ - 選考管理"},
                {"name": "🗺️ 就活ナビ", "port": 8501, "desc": "Hub / Main Dashboard"},
                {"name": "✍️ ES工房", "port": 8506, "desc": "ES Creation Assistant"},
                {"name": "🔭 就活早耳", "port": 8509, "desc": "Job Trends & Scout"},
            ],
            "Learning (学習)": [
                {"name": "🌌 記憶バンク", "port": 8512, "desc": "Memory 3D - 知識宇宙の探索"},
                {"name": "🎯 英語道場", "port": 8502, "desc": "TOEIC Mastery AI"},
                {"name": "🏛️ 日本史/教養", "port": 8505, "desc": "History & General Knowledge"},
                {"name": "🧠 雑学王", "port": 8516, "desc": "Trivia King"},
            ],
            "AGI & Intelligent Tools": [
                {"name": "🎙️ ｼﾞｬｰﾋﾞｽ HUD", "port": 8520, "desc": "AGI視覚意識レイヤー - 画面監視"},
                {"name": "📺 動画要約", "port": 8511, "desc": "YouTube Summarizer"},
                {"name": "📊 システム監視", "port": 8504, "desc": "System Monitor Monitor"},
                {"name": "📓 日記バンク", "port": 8503, "desc": "Diary & Reflection"},
            ]
        }

        for category, apps in app_categories.items():
            st.markdown(f"#### {category}")
            cols = st.columns(4)
            for i, app in enumerate(apps):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="station-card" style="height: 180px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #CCFF00;">{app['name']}</div>
                        <div style="font-size: 0.85rem; color: #888; margin-top: 8px; flex-grow: 1;">{app['desc']}</div>
                        <div style="text-align: right;">
                            <span class="station-badge station-badge-blue">PORT {app['port']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    launch_url = app.get("url", f"http://localhost:{app['port']}")
                    if st.button(f"起動", key=f"launch_{category}_{i}"):
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={launch_url}">', unsafe_allow_html=True)

    # --- Tab 3: System Mission ---
    with tab3:
        st.markdown("### 🏹 Autonomous Mission HQ")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📜 Recent Activity Log")
            log_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs" / "activity_log.md"
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                # Display only last 5 entries to avoid scrolling too much
                entries = log_content.split("---")
                st.markdown("---".join(entries[-10:]))
            else:
                st.info("No activity logs found yet. Start an autonomous mission to see logs.")

        with col2:
            st.markdown("#### 🎯 Active Mission Status")
            # Masao AI style narrative for current status
            st.markdown("""
            <div style="background:rgba(204, 255, 0, 0.1); border-left:5px solid #CCFF00; padding:15px; border-radius:10px; margin-bottom:15px;">
                <b style="color:#CCFF00;">[AGI MISSION: LIVE] Multi-Path Explorer v2.0</b><br>
                <p style="font-size:0.85rem; color:#ccc; margin-top:10px;">
                指定された「出版・関西圏・官僚」の3軸で同時並行リサーチを実行中です。
                各分野に特化した戦略的ES（編集力・地域貢献・国家基盤）を自動執筆し、曼荼羅マトリックスの重要結節点を強化しています。
                </p>
                <div style="font-family:'Share Tech Mono'; font-size:0.75rem; color:#CCFF00; margin-top:5px;">
                    MISSION: TARGETED_CAREER_SYNC<br>
                    AXIS: PUBLISHING / KANSAI / NATIONAL<br>
                    STATUS: REASONING_DRAFTS
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### 🛠️ Quick Diagnostics")
            rust_status = "✅ ONLINE" if RUST_AVAILABLE else "⚠️ OFFLINE"
            st.write(f"- **Rust Engine (Core):** {rust_status}")
            st.write("- **Vision/Action:** ✅ READY")
            st.write("- **Research Agent:** ✅ READY")
            
            if st.button("🔄 Clean Temporary Files"):
                import shutil
                tmp_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs"
                for f in tmp_dir.glob("auto_step_*.png"):
                    f.unlink()
                st.success("Cleaned step screenshots.")

    # Footer
    render_station_footer()

if __name__ == "__main__":
    main()
