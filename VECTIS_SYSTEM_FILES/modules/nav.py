
import streamlit as st
from modules.style import apply_vectis_style

def render_global_road():
    """
    自分ステーション - 統一サイドバーナビゲーション
    全アプリ共通で使用するナビゲーションメニュー
    """
    # Apply Station Style
    apply_vectis_style()
    
    # ナビゲーションヘッダー
    st.sidebar.markdown("""
    <div style="
        background: rgba(204, 255, 0, 0.1);
        border: 1px solid rgba(204, 255, 0, 0.2);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span style="
            width: 8px;
            height: 8px;
            background: #ff3333;
            border-radius: 50%;
            animation: pulse 1s infinite;
        "></span>
        <span style="
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.75rem;
            color: #ff3333;
            letter-spacing: 2px;
        ">ON AIR</span>
    </div>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ホームボタン
    if st.sidebar.button("🏠 ホームへ戻る", use_container_width=True, type="primary"):
        st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8501">', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # === Global Search ===
    st.sidebar.markdown('<p style="font-family: Share Tech Mono; font-size: 0.7rem; color: #FFFFFF; letter-spacing: 2px;">🔍 GLOBAL SEARCH</p>', unsafe_allow_html=True)
    search_q = st.sidebar.text_input("Global Search", label_visibility="collapsed", placeholder="知識宇宙を検索...")
    
    if search_q:
        st.sidebar.info(f"Searching for: {search_q}")
        # We can implement a simple result display or redirect to a search results page
        # For now, let's keep it simple.
    
    # === セクション別ナビゲーション ===
    
    # 学習チャンネル
    st.sidebar.markdown('<p style="font-family: Share Tech Mono; font-size: 0.7rem; color: #CCFF00; letter-spacing: 2px; margin-bottom: 8px;">📚 学習</p>', unsafe_allow_html=True)
    study_apps = [
        ("🎯 英語道場", "http://localhost:8502"),
        ("🐍 Python", "http://localhost:8518"),
        ("🏛️ 教養", "http://localhost:8505"),
        ("🧠 雑学王", "http://localhost:8516"),
    ]
    cols = st.sidebar.columns(2)
    for i, (name, url) in enumerate(study_apps):
        with cols[i % 2]:
            if st.button(name, key=f"nav_study_{i}", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
    
    st.sidebar.markdown("")
    
    # 就活チャンネル
    st.sidebar.markdown('<p style="font-family: Share Tech Mono; font-size: 0.7rem; color: #00AAFF; letter-spacing: 2px; margin-bottom: 8px;">💼 就活</p>', unsafe_allow_html=True)
    job_apps = [
        ("🗺️ ナビ", "http://localhost:8501"),
        ("🎖️ 司令部", "http://localhost:8517"),
        ("✍️ ES工房", "http://localhost:8506"),
        ("🔭 早耳", "http://localhost:8509"),
    ]
    cols = st.sidebar.columns(2)
    for i, (name, url) in enumerate(job_apps):
        with cols[i % 2]:
            if st.button(name, key=f"nav_job_{i}", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
    
    st.sidebar.markdown("")
    
    # ツールチャンネル
    st.sidebar.markdown('<p style="font-family: Share Tech Mono; font-size: 0.7rem; color: #FF00AA; letter-spacing: 2px; margin-bottom: 8px;">🔧 ツール</p>', unsafe_allow_html=True)
    tool_apps = [
        ("📓 ひとくち", "http://localhost:8503"),
        ("📋 ｱｲﾃﾞﾝﾃｨﾃｨ", "http://localhost:8519"),
        ("🌌 記憶", "http://localhost:8512"),
        ("🎙️ ｼﾞｬｰﾋﾞｽ", "http://localhost:8520"),
    ]
    cols = st.sidebar.columns(2)
    for i, (name, url) in enumerate(tool_apps):
        with cols[i % 2]:
            if st.button(name, key=f"nav_tool_{i}", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # システムステータス
    st.sidebar.markdown("""
    <div style="
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 8px;
        padding: 10px 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span style="
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
        "></span>
        <span style="
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.7rem;
            color: #00ff88;
            letter-spacing: 1px;
        ">SYSTEM ONLINE</span>
    </div>
    """, unsafe_allow_html=True)


def render_station_footer():
    """統一フッター"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.9rem;
            color: #CCFF00;
            letter-spacing: 2px;
            margin-bottom: 8px;
        ">自分STATION</div>
        <div style="
            font-size: 0.75rem;
            color: #555;
        ">Powered by AI × Human Creativity</div>
    </div>
    """, unsafe_allow_html=True)
