
import streamlit as st
import os
import sys
import json
import time
import subprocess
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(page_title="📱 Mobile Link | 自分ステーション", page_icon="📱", layout="wide")

# Styling
# --- STYLES: VECTIS CORE ---
apply_vectis_style()
st.markdown("""
<style>
    /* Mobile-specific highlight override */
    h1, h2, h3 { color: #00FF99 !important; }

    .mobile-status {
        background: rgba(0, 255, 153, 0.1);
        border: 1px solid rgba(0, 255, 153, 0.3);
        padding: 20px;
        border-radius: 12px;
        font-family: 'Share Tech Mono', monospace;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
        color: #00FF99;
    }
    .device-card {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .screen-shot {
        width: 100%;
        max-width: 260px;
        aspect-ratio: 9/16;
        background: #000;
        border: 6px solid #222;
        border-radius: 30px;
        margin: 0 auto 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #444;
        font-size: 0.8em;
        font-family: 'Share Tech Mono', monospace;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🛠️ MCP MCP CONFIG")
    mcp_running = st.toggle("MCP SERVER ACTIVE", value=False)
    device_type = st.radio("TARGET DEVICE", ["Android Emulator", "iOS Simulator", "Physical Device"])

# Main UI
st.markdown(get_station_header(
    title="📱 MOBILE LINK",
    subtitle="Neural Link to Native Environment",
    channel_id="TOOL.07"
), unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="device-card">', unsafe_allow_html=True)
    st.markdown('<div class="screen-shot">NO SIGNAL<br>(Connect MCP)</div>', unsafe_allow_html=True)
    st.button("🔄 REFRESH SCREEN", use_container_width=True)
    st.button("📸 TAKE SNAPSHOT", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="mobile-status">
        STATUS: {"ONLINE" if mcp_running else "OFFLINE"}<br>
        DEVICE: {device_type}<br>
        PROTOCOL: Model Context Protocol (MCP)
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["🤖 Automation", "📂 Screen Data", "📋 Logs", "🍎 iPhone Setup Guide"])
    
    with tabs[0]:
        st.markdown("### > TRIGGER ACTION")
        st.info("MCP Server is not connected.")
    
    with tabs[1]:
        st.info("No screen data available.")
        
    with tabs[2]:
        st.code("System logs will appear here...", language="text")

    with tabs[3]:
        st.markdown("### 🍎 Windows から iPhone を制御する準備")
        st.info("通常、iOS の自動化には Mac が必要ですが、以下のブリッジ設定を行うことで Windows (Surface) からも操作可能です。")
        
        st.markdown("""
        **STEP 1: go-ios のインストール**  
        ```bash
        npm install -g go-ios
        ```
        
        **STEP 2: WebDriverAgent のサイドロード**  
        - [AltStore](https://altstore.io/) 等を使用して、`WebDriverAgentRunner.ipa` を iPhone にインストール。
        - iPhone でアプリを開き、動作を確認。
        
        **STEP 3: 通信トンネルの開始** (別のターミナルで実行)
        ```bash
        ios tunnel start --userspace
        ios forward 8100 8100
        ```
        """)
        
        if st.button("🔌 CHECK iOS CONNECTION (Port 8100)"):
            import socket
            with st.spinner("Pinging localhost:8100..."):
                try:
                    socket.create_connection(("localhost", 8100), timeout=2)
                    st.success("SUCCESS: iPhone (WDA) connected via Bridge!")
                except:
                    st.error("FAILED: Port 8100 is closed. Ensure go-ios forward is running and WDA is open on iPhone.")

st.markdown("---")
render_station_footer()
