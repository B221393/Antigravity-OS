"""
📺 動画かみくだき (Stream) - 自分ステーション
Port: 8511
YouTube動画を自動解析、要約。時間を節約して知識を吸収。
"""

import streamlit as st
import os
import sys
import json
import time
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.researcher import ResearchAgent
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(page_title="📺 動画かみくだき | 自分ステーション", page_icon="📺", layout="wide")

# Apply Station Style
apply_vectis_style()

# Custom extension (red/pink theme for stream)
st.markdown("""
<style>
    h1 {
        color: #FF4444 !important;
        text-shadow: 0 0 15px rgba(255, 68, 68, 0.4) !important;
    }
    
    .stream-card {
        background: #141414;
        border: 1px solid rgba(255, 68, 68, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    
    .stream-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #FF4444, #FF00AA);
    }
    
    .stream-card:hover {
        border-color: #FF4444;
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(255, 68, 68, 0.15);
    }
    
    .stream-title {
        color: #FF4444;
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .live-tag {
        background: #FF4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7em;
        font-weight: 900;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .stream-meta {
        font-size: 0.75rem;
        color: #888888;
        margin: 10px 0;
    }
    
    .stream-summary {
        color: #BBBBBB;
        font-size: 0.9rem;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🧬 ストリーム設定")
    genre = st.selectbox("ジャンル", ["AI & Tech", "Economy", "Japanese History", "Self Improvement", "Random"])
    auto_refresh = st.checkbox("🔄 自動更新", value=False)
    depth = st.slider("解析深度", 1, 5, 3)
    
    if st.button("🔄 今すぐ取得", type="primary", use_container_width=True):
        st.session_state.last_sync = 0
        st.rerun()

# Header
st.markdown(get_station_header(
    title="📺 動画かみくだき",
    subtitle="Auto-Analytic Neural Pathway // YouTube Intelligence",
    channel_id="TOOL.02"
), unsafe_allow_html=True)

# State
if "stream_data" not in st.session_state:
    st.session_state.stream_data = []
if "last_sync" not in st.session_state:
    st.session_state.last_sync = 0

# Fetch Logic
def fetch_stream(g):
    agent = ResearchAgent()
    query = f"site:youtube.com {g} 最新 2026"
    if g == "Random":
        query = "site:youtube.com 人気 トレンド ニュース"
    
    results = agent.search_web(query, max_results=5)
    analyzed = []
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        import re
        
        for r in results:
            url = r.get('href', '')
            vid_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if vid_id_match:
                vid_id = vid_id_match.group(1)
                summary = "字幕なし: " + r.get('body', '')[:200]
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=['ja', 'en'])
                    full_text = " ".join([t['text'] for t in transcript[:15]])
                    summary = full_text[:400] + "..."
                except: pass
                
                analyzed.append({
                    "id": vid_id,
                    "title": r.get('title', 'Unknown Stream'),
                    "url": url,
                    "summary": summary,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
    except ImportError:
        for r in results:
            analyzed.append({
                "id": str(time.time()),
                "title": r.get('title', 'Unknown'),
                "url": r.get('href', '#'),
                "summary": r.get('body', '')[:300],
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
    
    return analyzed

# Sync Logic
current_time = time.time()
if current_time - st.session_state.last_sync > 300:
    with st.spinner("🔄 YouTube グローバルストリームと同期中..."):
        try:
            new_data = fetch_stream(genre)
            existing_ids = [x['id'] for x in st.session_state.stream_data]
            st.session_state.stream_data = [n for n in new_data if n['id'] not in existing_ids] + st.session_state.stream_data
            st.session_state.last_sync = current_time
        except Exception as e:
            st.error(f"取得エラー: {e}")

# Display
if not st.session_state.stream_data:
    st.info("🔍 シグナルを検索中...しばらくお待ちください。")
else:
    for i, item in enumerate(st.session_state.stream_data[:10]):
        st.markdown(f'''<div class="stream-card"><span class="live-tag">LIVE ANALYSIS</span><div class="stream-title">▸ {item['title']}</div><div class="stream-meta">DETECTED AT {item['timestamp']}</div><div class="stream-summary">{item['summary']}</div></div>''', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📥 保存", key=f"save_{item['id']}", use_container_width=True):
                os.makedirs("apps/job_hunting", exist_ok=True)
                safe_title = "".join([c for c in item['title'] if c.isalnum() or c in (' ', '_')]).strip()
                filename = f"apps/job_hunting/VS_{safe_title.replace(' ', '_')}_{int(time.time())}.kcard"
                card_data = {
                    "title": f"[STREAM] {item['title']}",
                    "content": item['summary'],
                    "genre": "VideoAnalysis",
                    "rarity": "Epic",
                    "tags": ["stream", genre],
                    "timestamp": datetime.now().isoformat()
                }
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(card_data, f, indent=2, ensure_ascii=False)
                st.success("✅ 保存完了")
        with col2:
            st.link_button("▶ 動画を見る", item['url'], use_container_width=True)

# Auto refresh
if auto_refresh:
    st.info("自動更新が有効です。60秒後にリフレッシュします。")

# Footer
render_station_footer()
