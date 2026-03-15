"""
🔭 早耳ニュース (Scout) - 自分ステーション
Port: 8509
早期選考・インターン情報をAIがリアルタイム収集
"""

import streamlit as st
import os
import sys
import json
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.researcher import ResearchAgent
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(page_title="🔭 早耳ニュース | 自分ステーション", page_icon="🔭", layout="wide")

# Apply Station Style
apply_vectis_style()

# Custom extension (orange theme for scout)
st.markdown("""
<style>
    h1 {
        color: #FF9900 !important;
        text-shadow: 0 0 15px rgba(255, 153, 0, 0.4) !important;
    }
    
    .scout-card {
        background: #141414;
        border: 1px solid rgba(255, 153, 0, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    
    .scout-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #FF9900, #FF00AA);
    }
    
    .scout-card:hover {
        border-color: #FF9900;
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(255, 153, 0, 0.15);
    }
    
    .scout-title {
        color: #FF9900;
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    .scout-body {
        color: #BBBBBB;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .scout-meta {
        font-size: 0.7rem;
        color: #FF9900;
        opacity: 0.7;
        margin-top: 16px;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🔍 検索設定")
    target = st.text_input("キーワード", "出版 日本 2027 採用")
    depth = st.slider("検索深度", 1, 10, 5)
    
    if st.button("🔍 スカウト開始", type="primary", use_container_width=True):
        st.session_state.scout_results = "running"
    
    st.markdown("---")
    st.caption("企業・業界情報をAIが自動収集")

# Header
st.markdown(get_station_header(
    title="🔭 早耳ニュース",
    subtitle="就活情報・業界ニュースをAIが集める",
    channel_id="JOB.04"
), unsafe_allow_html=True)

# Search Execution
if "scout_results" in st.session_state and st.session_state.scout_results == "running":
    with st.spinner("🔍 AIエージェントが情報を収集中..."):
        agent = ResearchAgent()
        queries = [
            f"{target} 日本 早期選考",
            f"{target} 日本 インターンシップ 情報",
            f"{target} 日本 採用 2027 スケジュール",
            f"{target} 日本 トレンド 分析"
        ]
        
        all_results = []
        for q in queries:
            try:
                res = agent.search_web(q, max_results=3)
                all_results.extend(res)
            except: pass
        
        st.session_state.scout_data = all_results
        st.session_state.scout_results = "done"

# Display Results
if "scout_data" in st.session_state:
    st.markdown(f"### 📡 検索結果: {target}")
    
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.scout_data):
        with cols[i % 2]:
            title = item.get('title', 'Unknown')
            body = item.get('body', '')[:250]
            href = item.get('href', '#')
            
            st.markdown(f'''<div class="scout-card"><div class="scout-title">▸ {title}</div><div class="scout-body">{body}...</div><div class="scout-meta">DETECTED: {datetime.now().strftime('%Y-%m-%d')} | SOURCE: WEB_INTEL</div></div>''', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📥 保存", key=f"save_{i}", use_container_width=True):
                    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
                    filename = f"apps/job_hunting/SC_{safe_title.replace(' ', '_')}_{int(datetime.now().timestamp())}.kcard"
                    card_data = {
                        "title": f"[SCOUT] {title}",
                        "content": item.get('body', ''),
                        "genre": "Scout",
                        "rarity": "Rare",
                        "tags": ["scout", target],
                        "timestamp": datetime.now().isoformat()
                    }
                    os.makedirs("apps/job_hunting", exist_ok=True)
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(card_data, f, indent=2, ensure_ascii=False)
                    st.success("✅ 保存完了")
            with col_b:
                st.link_button("🔗 開く", href, use_container_width=True)
else:
    st.info("左のサイドバーからキーワードを入力して、スカウトプロトコルを開始してください。")

# Footer
render_station_footer()
