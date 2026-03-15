
import streamlit as st
import os
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(
    page_title="❓ Help Center | 自分ステーション",
    page_icon="❓",
    layout="wide"
)

# Load Env
load_dotenv("../../.env")

# --- STYLES: VECTIS CORE ---
apply_vectis_style()
st.markdown("""
<style>
    .help-section {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #00FFCC;
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    h3 { margin-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()

# Header
st.markdown(get_station_header(
    title="❓ 操作ガイド",
    subtitle="全システムの運用プロトコルと解説",
    channel_id="SYS.HELP"
), unsafe_allow_html=True)

st.markdown("""
<div class="help-section">
    <h3>🚀 クイックスタート</h3>
    <p>1. <b>VECTIS_START_ALL.bat</b> を実行して、全6つのサーバーを起動します。</p>
    <p>2. 自動で開く <b>Hub画面</b> があなたの司令塔です。</p>
    <p>3. 終了時は <b>VECTIS_STOP_ALL.bat</b> を実行してください。</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🗺️ 就活・知の探索", "🎯 TOEIC AI", "✍️ ES マスター", "🪄 Creator"])

with tabs[0]:
    st.subheader("就活ダッシュボードの歩き方")
    st.write("""
    - **知識空間 (3D Map)**: 蓄積された知識カードを3D空間で視覚化します。線で結ばれた点は関連性が高いことを示します。
    - **大西配列練習**: 左手で母音、右手で子音を司る効率的な配列を学びながら、就活日記を綴ります。
    - **教養の泉 (Ocean)**: 就活に必要な時事、歴史、一般常識を自動で収集・表示します。
    """)

with tabs[1]:
    st.subheader("TOEIC Mastery AI の運用")
    st.write("""
    - **Part 1-7 連続学習**: 本番同様の構成で問題を解き進めます。
    - **AI 写真描写**: Part 1 ではAIが生成したキーワードに基づき、リアルな写真が表示されます。
    - **990点スコアリング**: 精度に基づき直感的なスコアを算出し、`activity_log.md` に自動保存します。
    """)

with tabs[2]:
    st.subheader("ES マスターの活用法")
    st.write("""
    - **敬語ラボ**: 送信前のメールやESの一文を、正しい謙譲語や尊敬語に磨き上げます。
    - **スタイルチェック**: 文章の癖や二重敬語をAIが瞬時に指摘します。
    """)

with tabs[3]:
    st.subheader("VECTIS Creator の役割")
    st.write("""
    - ターミナル操作は不要です。GUIからタイトル、内容、ジャンルを入力し「射出」ボタンを押すと、自動的に3Dマップに「点」が追加されます。
    """)

# Footer
render_station_footer()
