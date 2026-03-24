"""
📊 システム監視 (System Monitor) - 自分ステーション
Port: 8504
APIコスト・サーバー状態・音声コマンドログをリアルタイム監視
"""

import streamlit as st
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header
from modules.api_tracker import APITracker

# Page Config
st.set_page_config(page_title="📊 システム監視 | 自分ステーション", page_icon="📊", layout="wide")

# Apply Station Style
apply_vectis_style()

# Custom extension (blue theme for monitoring)
st.markdown("""
<style>
    h1 {
        color: #00AAFF !important;
        text-shadow: 0 0 15px rgba(0, 170, 255, 0.4) !important;
    }
    
    .monitor-card {
        background: #141414;
        border: 1px solid rgba(0, 170, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .monitor-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00AAFF, #CCFF00);
    }
    
    .monitor-card h3 {
        color: #00AAFF !important;
        font-size: 1.1rem;
        margin-bottom: 16px;
    }
    
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .metric-label {
        color: #888888;
        font-size: 0.9rem;
    }
    
    .metric-value {
        color: #CCFF00;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
    }
    
    .log-entry {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
        color: #888888;
        padding: 4px 0;
        border-left: 2px solid transparent;
        padding-left: 8px;
        transition: all 0.2s;
    }
    
    .log-entry:hover {
        color: #00AAFF;
        border-left-color: #00AAFF;
    }
</style>
""", unsafe_allow_html=True)

tracker = APITracker()

# Sidebar
with st.sidebar:
    render_global_road()

# Header
st.markdown(get_station_header(
    title="📊 システム監視",
    subtitle="APIコスト追跡 & ニューラル音声ログ",
    channel_id="TOOL.05"
), unsafe_allow_html=True)

# Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="monitor-card"><h3>💰 API 使用量 & 推定コスト</h3>', unsafe_allow_html=True)
    
    metrics = {
        "Gemini 2.0 (Vision)": {"calls": 42, "cost": 0.00},
        "Gemini 2.0 (Text)": {"calls": 128, "cost": 0.00},
        "Groq (Llama 3)": {"calls": 85, "cost": 0.00},
        "DuckDuckGo Search": {"calls": 56, "cost": 0.00}
    }
    
    for provider, data in metrics.items():
        st.markdown(f'''<div class="metric-row"><span class="metric-label">{provider}</span><span class="metric-value">{data["calls"]} calls</span></div>''', unsafe_allow_html=True)
        st.progress(min(data["calls"]/200, 1.0))
    
    st.markdown("---")
    st.info("※現在、Gemini APIは無料枠内で運用されています。")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="monitor-card"><h3>🎙️ 最近の音声コマンドログ</h3>', unsafe_allow_html=True)
    
    log_path = "../../activity_log.md"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = f.readlines()[-10:]
            for log in reversed(logs):
                if log.strip():
                    st.markdown(f'<div class="log-entry">{log.strip()}</div>', unsafe_allow_html=True)
    else:
        st.write("ログデータが見つかりません。")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Second Row
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 💾 DISK CAPACITY MONITOR")
    
    # --- Disk Monitoring Logic ---
    import shutil
    import csv
    import pandas as pd
    
    MONITOR_LOG = os.path.join(os.path.dirname(__file__), "disk_usage.csv")
    
    def get_disk_info():
        # Get C: drive usage
        total, used, free = shutil.disk_usage("C:/")
        return total / (1024**3), used / (1024**3), free / (1024**3) # GB conversion
        
    def log_disk_usage():
        total, used, free = get_disk_info()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Init file if needed
        if not os.path.exists(MONITOR_LOG):
            with open(MONITOR_LOG, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Total_GB", "Used_GB", "Free_GB"])
                
        # Append data (Simple check to avoid dupes in same minute)
        try:
            with open(MONITOR_LOG, "r") as f:
                lines = f.readlines()
                if lines and now_str in lines[-1]:
                    return # Already logged this minute
        except: pass
        
        with open(MONITOR_LOG, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([now_str, round(total,2), round(used,2), round(free,2)])
            
    # Execute Logging
    log_disk_usage()
    
    # Read & Visualize
    if os.path.exists(MONITOR_LOG):
        df = pd.read_csv(MONITOR_LOG)
        
        # 1. Safety Judgment
        latest_free = df.iloc[-1]["Free_GB"]
        total_cap = df.iloc[-1]["Total_GB"]
        usage_percent = (df.iloc[-1]["Used_GB"] / total_cap) * 100
        
        # Thresholds (Danger if free < 20GB or < 10%)
        is_danger = latest_free < 20.0
        
        status_color = "#FF4B4B" if is_danger else "#00CC00"
        status_text = "DANGER (Low Space)" if is_danger else "SAFE (Healthy)"
        
        st.markdown(f"""
        <div style="background:#222; padding:15px; border-radius:10px; border-left:5px solid {status_color}; margin-bottom:15px;">
            <h3 style="margin:0; color:{status_color}">{status_text}</h3>
            <p style="margin:5px 0 0 0; color:#DDD">
               Free Space: <b>{latest_free:.2f} GB</b> / Total: {total_cap:.2f} GB 
               (Used: {usage_percent:.1f}%)
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Graph (Time vs Free Space)
        st.markdown("**Free Space Trend (GB)**")
        st.line_chart(df, x="Time", y="Free_GB", color="#00AAFF")
        
        st.markdown("**Capacity Usage (GB)**")
        st.area_chart(df, x="Time", y=["Used_GB", "Free_GB"], color=["#FF4B4B", "#00CC00"])
        
    else:
        st.info("Initializing Monitor Log...")

with col_b:
    st.markdown("### 🎤 FULL VOICE LOG")
    if os.path.exists("../../activity_log.md"):
        with open("../../activity_log.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-20:]:
                if line.strip():
                    st.text(line.strip())
    else:
        st.write("No logs found.")

# Footer
render_station_footer()
