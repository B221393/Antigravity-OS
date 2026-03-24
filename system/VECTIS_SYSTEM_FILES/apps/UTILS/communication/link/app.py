"""
🎮 つながりゲーム (Link) - 自分ステーション
Port: 8513
「すべてはすべてであるゲーム」- AIが出す2つの概念をつなげる
"""

import streamlit as st
import os
import sys
import json
import random

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header
from modules.researcher import ResearchAgent

# Page Config
st.set_page_config(page_title="🎮 つながりゲーム | 自分ステーション", page_icon="🎮", layout="wide")

# Apply Station Style
apply_vectis_style()

# Custom extension (yellow/gold theme for link game)
st.markdown("""
<style>
    h1 {
        color: #FFCC00 !important;
        text-shadow: 0 0 15px rgba(255, 204, 0, 0.4) !important;
    }
    
    .game-card {
        background: #141414;
        border: 2px solid rgba(255, 204, 0, 0.3);
        border-radius: 24px;
        padding: 48px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .game-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FFCC00, #FF9900);
    }
    
    .concept {
        font-size: 2.5rem;
        font-family: 'Share Tech Mono', monospace;
        color: #FFCC00;
        font-weight: 800;
        text-shadow: 0 0 30px rgba(255, 204, 0, 0.3);
    }
    
    .vs {
        font-size: 1.3rem;
        color: #00FFCC;
        margin: 24px 0;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 5px;
        opacity: 0.7;
    }
    
    .result-card {
        background: linear-gradient(135deg, #141414, rgba(255, 204, 0, 0.05));
        border: 1px solid rgba(255, 204, 0, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🎲 ゲームルール")
    st.markdown("""
    **「すべてはすべてである」**
    
    AIが出題する二つの無関係な事象を、
    論理や哲学で繋げてください。
    
    意外性・納得感・詩的な美しさで評価されます。
    """)

# Header
st.markdown(get_station_header(
    title="🎮 つながりゲーム",
    subtitle="すべてはすべてである - 知識を繋げるパズル",
    channel_id="FUN.02"
), unsafe_allow_html=True)

# Game State
if "concept_a" not in st.session_state:
    st.session_state.concept_a = "コンビニのおにぎり"
if "concept_b" not in st.session_state:
    st.session_state.concept_b = "量子もつれ"

# Game Card
st.markdown('<div class="game-card">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    st.markdown(f'<div class="concept">{st.session_state.concept_a}</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="vs">... IS ...</div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="concept">{st.session_state.concept_b}</div>', unsafe_allow_html=True)

st.markdown("---")

user_link = st.text_area("二つの概念を繋ぐ『共通点』や『物語』を記述してください...", 
                         placeholder="例: どちらも観測されるまでは状態が確定しない...",
                         height=120)

col_submit, col_next = st.columns(2)

with col_submit:
    if st.button("🚀 審判を仰ぐ", type="primary", use_container_width=True):
        if user_link:
            with st.spinner("AIが哲学的にリンクを解析中..."):
                agent = ResearchAgent()
                prompt = f"""
                「すべてはすべてである」という哲学に基づき、以下の二つの概念の繋がりをジャッジしてください。
                概念A: {st.session_state.concept_a}
                概念B: {st.session_state.concept_b}
                ユーザーの答え: {user_link}
                
                評価基準:
                1. 意外性 (5点満点)
                2. 納得感 (5点満点)
                3. 詩的な美しさ (5点満点)
                
                最後に、この繋がりを証明する一文を出力してください。
                """
                result = agent._call_llm(prompt)
                
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### 👁️ AIの審判")
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
                st.balloons()
        else:
            st.warning("⚠️ リンクを入力してください。")

with col_next:
    if st.button("🌀 次の問題", use_container_width=True):
        concepts = [
            "夏目漱石", "ブラックホール", "講談社の編集者", "たこ焼き", 
            "人工衛星", "セミの抜け殻", "ブロックチェーン", "マヨネーズ", 
            "相対性理論", "100円ショップの輪ゴム", "富士山", "AI面接",
            "コーヒーの香り", "就活のES", "新幹線", "インスタグラム"
        ]
        st.session_state.concept_a = random.choice(concepts)
        st.session_state.concept_b = random.choice(concepts)
        while st.session_state.concept_a == st.session_state.concept_b:
            st.session_state.concept_b = random.choice(concepts)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer
render_station_footer()
