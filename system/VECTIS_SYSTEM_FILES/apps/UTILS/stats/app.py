"""
📈 利用分析 (Stats) - 自分ステーション
Port: 8510
学習時間、知識蓄積量、成長グラフを可視化
"""

import streamlit as st
import os
import glob
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# Navigation
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(page_title="📈 利用分析 | 自分ステーション", page_icon="📈", layout="wide")

# Apply Station Style
apply_vectis_style()

# Custom extension (lime/cyan theme for stats)
st.markdown("""
<style>
    .stat-card {
        background: #141414;
        border: 1px solid rgba(204, 255, 0, 0.2);
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    
    .stat-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #CCFF00, #00AAFF);
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: #CCFF00;
        box-shadow: 0 15px 40px rgba(204, 255, 0, 0.1);
    }
    
    .stat-value {
        font-family: 'Share Tech Mono', monospace;
        font-size: 3rem;
        color: #CCFF00;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(204, 255, 0, 0.3);
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 📊 分析オプション")
    date_range = st.selectbox("期間", ["今週", "今月", "全期間"])
    st.caption("Usage analytics & Growth visualizer")

# Header
st.markdown(get_station_header(
    title="📈 利用分析",
    subtitle="Neural OS Activity Analysis & Knowledge Growth Metrics",
    channel_id="TOOL.06"
), unsafe_allow_html=True)

# Data Collection
def get_stats():
    cards = glob.glob("../job_hunting/*.kcard")
    
    log_file = "../../activity_log.md"
    log_size = 0
    if os.path.exists(log_file):
        log_size = os.path.getsize(log_file)
    
    diaries = glob.glob("../diary/data/*.json")
    
    return {
        "cards_count": len(cards),
        "log_kb": round(log_size / 1024, 2),
        "diary_count": len(diaries)
    }

stats = get_stats()

# Metric Cards
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["cards_count"]}</div><div class="stat-label">Knowledge Cards</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["log_kb"]} KB</div><div class="stat-label">Neural Activity Log</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["diary_count"]}</div><div class="stat-label">Diary Logs</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Knowledge Distribution
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Knowledge Distribution")
    if stats["cards_count"] > 0:
        genres = []
        for f in glob.glob("../job_hunting/*.kcard"):
            try:
                with open(f, "r", encoding="utf-8") as j:
                    d = json.load(j)
                    genres.append(d.get("genre", "Unknown"))
            except: pass
        
        if genres:
            df_genre = pd.DataFrame(genres, columns=["Genre"])
            fig = px.pie(df_genre, names="Genre", title="ジャンル別知識分布", hole=0.4, template="plotly_dark")
            fig.update_traces(marker=dict(colors=['#CCFF00', '#00AAFF', '#FF00AA', '#FF9900', '#00FF88']))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("知識カードがまだありません。")

with col2:
    st.markdown("### 📈 Activity Waveform")
    dummy_data = pd.DataFrame({
        'Date': pd.date_range(start='2026-01-01', periods=10),
        'Activity': [10, 15, 8, 22, 30, 25, 40, 35, 50, 60]
    })
    fig2 = px.line(dummy_data, x='Date', y='Activity', title="Interaction Frequency", template="plotly_dark")
    fig2.update_traces(line_color='#CCFF00')
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Footer
render_station_footer()
