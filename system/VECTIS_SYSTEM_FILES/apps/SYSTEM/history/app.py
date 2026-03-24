"""
🏛️ 教養チャンネル (History) - 自分ステーション
Port: 8505
日本史・世界史をタイムラインとクイズで学習
"""

import streamlit as st
import json
import random
import os
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Config
st.set_page_config(page_title="🏛️ 教養チャンネル | 自分ステーション", page_icon="🏛️", layout="wide")

# Apply Station Style
apply_vectis_style()

# Custom extension (cyan/teal theme)
st.markdown("""
<style>
    h1 {
        color: #00FFCC !important;
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.4) !important;
    }
    
    .timeline-card {
        background: #141414;
        border: 1px solid rgba(0, 255, 204, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    
    .timeline-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #00FFCC, #00AAFF);
    }
    
    .timeline-card:hover {
        border-color: #00FFCC;
        transform: translateX(10px);
        box-shadow: 0 10px 30px rgba(0, 255, 204, 0.15);
    }
    
    .timeline-date {
        color: #00FFCC;
        font-weight: 800;
        font-size: 1.1rem;
        font-family: 'Share Tech Mono', monospace;
    }
    
    .timeline-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 8px 0;
        color: #FFFFFF;
    }
    
    .timeline-desc {
        color: #AAAAAA;
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    .quiz-container {
        background: #141414;
        border: 2px solid rgba(0, 255, 204, 0.3);
        border-radius: 20px;
        padding: 48px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .quiz-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00FFCC, #CCFF00);
    }
    
    .quiz-question {
        font-size: 1.8rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 32px;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading
def load_history_data():
    try:
        with open(os.path.join(os.path.dirname(__file__), "history_data.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

HISTORY_EVENTS = load_history_data()

QUIZ_DATA = [
    {"q": "1600年に起こった「天下分け目の戦い」は？", "a": ["関ヶ原の戦い", "桶狭間の戦い", "長篠の戦い", "本能寺の変"], "correct": "関ヶ原の戦い"},
    {"q": "織田信長が今川義元を破った戦いは？", "a": ["桶狭間の戦い", "姉川の戦い", "三方ヶ原の戦い", "長篠の戦い"], "correct": "桶狭間の戦い"},
    {"q": "江戸幕府を開いたのは誰？", "a": ["徳川家康", "豊臣秀吉", "織田信長", "明智光秀"], "correct": "徳川家康"},
    {"q": "1853年、浦賀に来航したアメリカ人は？", "a": ["ペリー", "ザビエル", "マッカーサー", "ハリス"], "correct": "ペリー"},
    {"q": "「敵は本能寺にあり」と言ったとされる武将は？", "a": ["明智光秀", "豊臣秀吉", "柴田勝家", "石田三成"], "correct": "明智光秀"},
]

# BOOKSHELF Saving Mechanism (教養＝本として保存)
def save_learning_to_book(fact, score):
    try:
        book_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../OBSIDIAN_WRITING/BOOKSHELF/05_Manual_Notes"))
        os.makedirs(book_dir, exist_ok=True)
        book_path = os.path.join(book_dir, "History_Learning_Log.md")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"| {timestamp} | ✅ Learned | {fact} | Score: {score} |\n"
        
        # Create header if new
        if not os.path.exists(book_path):
            with open(book_path, "w", encoding="utf-8") as f:
                f.write("# 🏛️ History Learning Log\n\n| Date | Status | Fact | Score |\n|---|---|---|---|\n")
        
        with open(book_path, "a", encoding="utf-8") as f:
            f.write(entry)
            
    except Exception as e:
        print(f"Failed to save to book: {e}")

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    
    mode = st.radio("モード選択", [
        "📜 タイムライン",
        "🧠 クイズ",
        "🤖 AIチューター"
    ])

# Header
st.markdown(get_station_header(
    title="🏛️ 教養チャンネル",
    subtitle="Efficient Learning Module - 歴史を楽しく学ぶ",
    channel_id="CH.03"
), unsafe_allow_html=True)

# Main Content
if mode == "📜 タイムライン":
    st.markdown("### ⏳ 年表ストリーム")
    
    for event in HISTORY_EVENTS:
        st.markdown(f'''<div class="timeline-card"><div class="timeline-date">{event['year']} [{event['era']}]</div><div class="timeline-title">{event['title']}</div><div class="timeline-desc">{event['desc']}</div></div>''', unsafe_allow_html=True)

elif mode == "🧠 クイズ":
    st.markdown("### 🧠 知識チェック")
    
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "current_q_index" not in st.session_state:
        st.session_state.current_q_index = 0
    if "quiz_shuffled" not in st.session_state:
        idxs = list(range(len(QUIZ_DATA)))
        random.shuffle(idxs)
        st.session_state.quiz_shuffled = idxs
    
    q_idx = st.session_state.current_q_index
    
    if q_idx < len(QUIZ_DATA):
        actual_index = st.session_state.quiz_shuffled[q_idx]
        q_data = QUIZ_DATA[actual_index]
        
        st.markdown(f'''<div class="quiz-container"><div style="color:#888; margin-bottom:10px;">QUESTION {q_idx + 1} / {len(QUIZ_DATA)}</div><div class="quiz-question">{q_data['q']}</div></div>''', unsafe_allow_html=True)
        
        opts = q_data['a'].copy()
        
        def check_answer(ans):
            if ans == q_data['correct']:
                st.session_state.quiz_score += 10
                st.toast("✅ 正解！BOOKSHELFに記録しました", icon="⭕")
                # SAVE TO BOOK
                save_learning_to_book(f"Answered correctly: {q_data['q']} -> {ans}", st.session_state.quiz_score)
            else:
                st.toast(f"❌ 不正解... 答え: {q_data['correct']}", icon="❌")
            st.session_state.current_q_index += 1
        
        col1, col2 = st.columns(2)
        for i, opt in enumerate(opts):
            if i % 2 == 0:
                with col1:
                    if st.button(opt, key=f"q{q_idx}_opt{i}", use_container_width=True):
                        check_answer(opt)
                        st.rerun()
            else:
                with col2:
                    with st.container(): # fix layout
                        if st.button(opt, key=f"q{q_idx}_opt{i}", use_container_width=True):
                            check_answer(opt)
                            st.rerun()
    else:
        st.markdown(f'''<div class="quiz-container"><h1 style="color:#00FFCC;">🎉 セッション完了!</h1><div style="font-size:3rem; font-weight:bold; color:#CCFF00;">スコア: {st.session_state.quiz_score}</div><p style="margin-top:20px; color:#888;">学習記録はBOOKSHELFに保存されました。</p></div>''', unsafe_allow_html=True)
        
        if st.button("🔄 もう一度", use_container_width=True):
            st.session_state.quiz_score = 0
            st.session_state.current_q_index = 0
            idxs = list(range(len(QUIZ_DATA)))
            random.shuffle(idxs)
            st.session_state.quiz_shuffled = idxs
            st.rerun()

elif mode == "🤖 AIチューター":
    st.markdown("### 🤖 AIチューター")
    st.info("歴史についてなんでも質問してください。")
    
    user_q = st.text_input("質問を入力 (例: なぜ江戸時代は終わったの？)")
    if user_q:
        with st.spinner("歴史データを分析中..."):
            try:
                from modules.researcher import ResearchAgent
                agent = ResearchAgent()
                res = agent.search_web(f"日本史 {user_q}", max_results=1)
                if res:
                    st.subheader(res[0]['title'])
                    st.write(res[0]['body'])
                    st.caption(f"Source: {res[0]['href']}")
                    
                    # Also save research to book
                    save_learning_to_book(f"Researched: {user_q} -> {res[0]['title']}", 0)
                    st.success("調査結果をBOOKSHELFに保存しました。")
                else:
                    st.error("該当する歴史記録が見つかりません。")
            except Exception as e:
                st.error(f"エラー: {e}")

# Footer
render_station_footer()
