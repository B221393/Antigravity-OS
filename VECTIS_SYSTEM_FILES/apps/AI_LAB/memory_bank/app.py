"""
🧠 Memory Bank (記憶バンク) - 自分ステーション
Port: 8518
Geminiとの対話を「長期記憶」として保存・統合・活用する専用アプリ。
"""

import streamlit as st
import json
import os
import glob
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Path setup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Config
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Page Config
st.set_page_config(page_title="🧠 Memory Bank | 自分ステーション", page_icon="🧠", layout="wide")
apply_vectis_style()

# Custom Styles
st.markdown("""
<style>
    .memory-card {
        background: rgba(15, 15, 30, 0.8);
        border: 1px solid rgba(100, 100, 255, 0.2);
        border-left: 4px solid #6666FF;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 16px;
        transition: transform 0.2s;
    }
    .memory-card:hover {
        transform: translateX(5px);
        border-color: #8888FF;
        box-shadow: 0 4px 20px rgba(100, 100, 255, 0.15);
    }
    .memory-meta {
        font-family: 'Share Tech Mono', monospace;
        color: #8888FF;
        font-size: 0.8rem;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }
    .memory-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 12px;
    }
    .memory-content {
        font-size: 0.95rem;
        color: #DDDDDD;
        line-height: 1.6;
        max-height: 150px;
        overflow: hidden;
        position: relative;
    }
    .memory-content::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 40px;
        background: linear-gradient(transparent, rgba(15, 15, 30, 0.95));
    }
    .tag-badge {
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- Logic ---

def save_memory(title, content, tags):
    mem_id = str(uuid.uuid4())
    data = {
        "id": mem_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": title,
        "content": content,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "type": "conversation_log"
    }
    fname = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(DATA_DIR, fname), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def load_memories():
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    files.sort(key=os.path.getmtime, reverse=True)
    memories = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fin:
                memories.append(json.load(fin))
        except: pass
    return memories

# --- UI ---

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    view_mode = st.radio("View Mode", ["📥 インポート (Import)", "🔍 記憶検索 (Recall)", "📊 統合分析 (Synthesis)"])

# Header
st.markdown(get_station_header(
    title="🧠 MEMORY BANK",
    subtitle="Externalized Brain & Conversation Archive",
    channel_id="MEM.01"
), unsafe_allow_html=True)

if view_mode == "📥 インポート (Import)":
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### 📥 会話ログの定着")
        st.info("Geminiとの対話をここにペーストしてください。分身(Clone)の重要な学習源になります。")
        
        input_title = st.text_input("タイトル / テーマ", placeholder="例: リーダーシップについての議論")
        input_content = st.text_area("会話ログ本文", height=400, placeholder="User: ...\nGemini: ...")
    
    with c2:
        st.markdown("### 🏷️ タグ付け")
        input_tags = st.text_input("タグ (カンマ区切り)", placeholder="価値観, 就活, 哲学")
        st.caption("適切なタグをつけることで、検索精度と学習効率が向上します。")
        
        st.markdown("---")
        if st.button("🧠 記憶領域に保存", type="primary", use_container_width=True):
            if input_title and input_content:
                save_memory(input_title, input_content, input_tags)
                st.success("記憶が保存されました。")
            else:
                st.warning("タイトルと本文は必須です。")

elif view_mode == "🔍 記憶検索 (Recall)":
    st.markdown("### 🔍 記憶の呼び出し")
    query = st.text_input("キーワード検索", placeholder="Search memories...")
    
    memories = load_memories()
    if query:
        memories = [m for m in memories if query.lower() in str(m).lower()]
    
    st.markdown(f"**Found {len(memories)} memories**")
    
    for m in memories:
        tags_html = "".join([f'<span class="tag-badge">{t}</span>' for t in m.get("tags", [])])
        st.markdown(f"""
        <div class="memory-card">
            <div class="memory-meta">
                <span>{m.get('timestamp')}</span>
                <span>{tags_html}</span>
            </div>
            <div class="memory-title">{m.get('summary')}</div>
            <div class="memory-content">{m.get('content').replace('<','&lt;').replace('\n','<br>')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"📖 Read Full: {m.get('summary')}"):
            st.text(m.get('content'))
            if st.button("🗑️ 忘却 (Delete)", key=f"del_{m.get('id')}"):
                # Mock delete logic provided (re-implement with actual file deletion if needed)
                st.warning("削除機能は安全のため無効化されています。(File operation required)")

elif view_mode == "📊 統合分析 (Synthesis)":
    st.markdown("### 📊 記憶の統合")
    st.info("蓄積された会話から、あなたの「思考マップ」を生成します。（開発中）")
    
    memories = load_memories()
    if not memories:
        st.warning("データが足りません。")
    else:
        # Simple stats
        total_chars = sum([len(m.get('content','')) for m in memories])
        st.metric("Total Knowledge Volume", f"{total_chars:,} chars")
        st.metric("Memory Fragments", len(memories))
        
        # Tag cloud (Mock)
        all_tags = []
        for m in memories:
            all_tags.extend(m.get("tags", []))
        
        if all_tags:
            st.markdown("#### Top Concepts")
            from collections import Counter
            counts = Counter(all_tags)
            st.write(dict(counts))

st.markdown("---")
render_station_footer()
