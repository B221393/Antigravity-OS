"""
🧠 雑学王 (Daily Trivia) - 自分ステーション
Port: 8516
毎日1つの雑学を取得、英語翻訳付き
"""

import streamlit as st
import json
import os
import random
from datetime import datetime, date
import sys

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Config
DATA_DIR = os.path.dirname(__file__)
TRIVIA_FILE = os.path.join(DATA_DIR, "trivia_history.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")

# Page Config
st.set_page_config(page_title="🧠 雑学王 | 自分ステーション", page_icon="🧠", layout="centered")
apply_vectis_style()

# Custom Styles (自分ステーション統一デザイン拡張)
st.markdown("""
<style>
    .trivia-card {
        background: linear-gradient(135deg, #141414, #1a1a1a);
        border: 2px solid rgba(255, 153, 0, 0.3);
        border-radius: 20px;
        padding: 32px;
        margin: 24px 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    .trivia-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FF9900, #FF00AA);
    }
    .trivia-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .trivia-date {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85em;
        color: #FF9900;
        opacity: 0.9;
    }
    .trivia-source {
        font-size: 0.8em;
        color: #888888;
        margin-top: 4px;
    }
    .trivia-content {
        font-size: 1.25em;
        line-height: 1.9;
        color: #ffffff;
        margin: 20px 0;
        padding: 24px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        border-left: 4px solid #FF9900;
    }
    .english-section {
        background: rgba(0, 170, 255, 0.08);
        border: 1px solid rgba(0, 170, 255, 0.25);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    .english-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75em;
        color: #00AAFF;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    .english-text {
        font-size: 1.05em;
        line-height: 1.7;
        color: #BBBBBB;
    }
    .channel-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7em;
        font-family: 'Share Tech Mono', monospace;
        margin-right: 8px;
        background: rgba(255, 153, 0, 0.15);
        border: 1px solid rgba(255, 153, 0, 0.4);
        color: #FF9900;
    }
    .lightbulb {
        font-size: 3em;
        margin-right: 16px;
    }
    .history-item {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s;
    }
    .history-item:hover {
        border-color: rgba(255, 153, 0, 0.3);
        transform: translateX(4px);
    }
</style>
""", unsafe_allow_html=True)



# === Default Channels ===
DEFAULT_CHANNELS = [
    {
        "name": "ゆる言語学ラジオ",
        "id": "UCmpkIzF3xFzhPez7gXOyhVg",
        "category": "言語",
        "color": "#FF6B6B"
    },
    {
        "name": "3Blue1Brown",
        "id": "UCYO_jab_esuFRV4b17AJtAw",
        "category": "数学",
        "color": "#4ECDC4"
    },
    {
        "name": "Vsauce",
        "id": "UC6nSFpj9HTCZ5t-N3Rm3-HA",
        "category": "科学",
        "color": "#45B7D1"
    },
    {
        "name": "Kurzgesagt",
        "id": "UCsXVk37bltHxD1rDPwtNM8Q",
        "category": "科学",
        "color": "#96CEB4"
    },
    {
        "name": "ゆるコンピュータ科学ラジオ",
        "id": "UCpLu0KjNy616-E95gXx5Rog",
        "category": "IT",
        "color": "#9B59B6"
    }
]

# === Sample Trivia Database (Fallback) ===
SAMPLE_TRIVIA = [
    {
        "japanese": "「了解」という言葉は、もともと「理解した」という意味に加えて「承知した」というニュアンスを含んでいる。これは日本語特有の「察する」文化と関係がある。",
        "english": "The Japanese word 'ryoukai' (了解) originally contains both the meaning of 'understood' and the nuance of 'acknowledged'. This is related to Japan's unique culture of 'reading between the lines'.",
        "source": "ゆる言語学ラジオ",
        "category": "言語"
    },
    {
        "japanese": "円周率πは無理数であり、その小数点以下は無限に続く。しかし面白いことに、πの中には私たちの誕生日や電話番号など、あらゆる数字の並びが含まれていると考えられている。",
        "english": "Pi is an irrational number with infinite decimal places. Interestingly, it's believed that pi contains every possible sequence of numbers, including your birthday and phone number.",
        "source": "3Blue1Brown",
        "category": "数学"
    },
    {
        "japanese": "人間の脳は約860億個のニューロンで構成されており、これは銀河系の星の数とほぼ同じ。つまり、私たちは頭の中に宇宙を持っているようなものだ。",
        "english": "The human brain consists of about 86 billion neurons, roughly the same as the number of stars in our galaxy. In a sense, we all carry a universe inside our heads.",
        "source": "Kurzgesagt",
        "category": "科学"
    },
    {
        "japanese": "日本語の「もったいない」は他の言語に直接翻訳できない。物を大切にする日本独自の精神を表す言葉として、国際的に注目されている。",
        "english": "The Japanese word 'mottainai' cannot be directly translated into other languages. It represents Japan's unique spirit of cherishing things and has gained international attention.",
        "source": "ゆる言語学ラジオ",
        "category": "言語"
    },
    {
        "japanese": "線形代数の固有ベクトルは、変換後も方向が変わらないベクトル。これを理解すると、データ分析やAIの仕組みがより深く理解できる。",
        "english": "Eigenvectors in linear algebra are vectors that don't change direction after transformation. Understanding this helps us better grasp data analysis and AI mechanisms.",
        "source": "3Blue1Brown",
        "category": "数学"
    },
    {
        "japanese": "プログラミング言語Pythonの名前は、コメディグループ「モンティ・パイソン」に由来する。開発者のグイド・ヴァンロッサムがファンだったため。",
        "english": "The programming language Python is named after the comedy group 'Monty Python'. The creator Guido van Rossum was a fan of their work.",
        "source": "ゆるコンピュータ科学ラジオ",
        "category": "IT"
    },
    {
        "japanese": "宇宙の年齢は約138億年だが、観測可能な宇宙の直径は約930億光年もある。これは宇宙の膨張速度が光速を超えることができるため。",
        "english": "The universe is about 13.8 billion years old, yet the observable universe spans about 93 billion light-years. This is because the expansion of space can exceed the speed of light.",
        "source": "Kurzgesagt",
        "category": "科学"
    }
]

# === Data Functions ===
def load_trivia_history():
    if os.path.exists(TRIVIA_FILE):
        with open(TRIVIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_trivia_history(history):
    with open(TRIVIA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_today_trivia():
    """Get or generate today's trivia"""
    history = load_trivia_history()
    today_str = date.today().isoformat()
    
    # Check if already generated today
    for item in history:
        if item.get("date") == today_str:
            return item
    
    # Generate new trivia (using sample database for now)
    trivia = random.choice(SAMPLE_TRIVIA)
    new_entry = {
        "date": today_str,
        "japanese": trivia["japanese"],
        "english": trivia["english"],
        "source": trivia["source"],
        "category": trivia["category"],
        "generated_at": datetime.now().isoformat()
    }
    
    history.insert(0, new_entry)
    save_trivia_history(history)
    return new_entry

def translate_with_ai(text):
    """Translate Japanese to English using Groq"""
    try:
        from modules.researcher import ResearchAgent
        from dotenv import load_dotenv
        load_dotenv()
        
        agent = ResearchAgent()
        prompt = f"""Translate the following Japanese trivia into natural, engaging English.
Keep it educational and interesting:

{text}

Provide only the English translation, nothing else."""
        
        return agent._call_llm(prompt)
    except Exception as e:
        return f"(Translation unavailable: {e})"

# === Sidebar ===
with st.sidebar:
    render_global_road()
    
    st.markdown("---")
    st.markdown("##### 📺 ソースチャンネル")
    
    # Channel Selection
    st.markdown("##### 📺 ソースチャンネル")
    for ch in DEFAULT_CHANNELS:
        st.markdown(f"• **{ch['name']}** ({ch['category']})")
    
    st.markdown("---")
    
    if st.button("🔄 新しい雑学を取得", use_container_width=True):
        # Force refresh (remove today's entry)
        history = load_trivia_history()
        today_str = date.today().isoformat()
        history = [h for h in history if h.get("date") != today_str]
        save_trivia_history(history)
        st.rerun()

# === Main Content ===
st.markdown(get_station_header(
    title="🧠 雑学王",
    subtitle="Today's Trivia - 毎日1つ、知識を広げる",
    channel_id="CH.04"
), unsafe_allow_html=True)

# Get today's trivia
trivia = get_today_trivia()

# Display main trivia card (no indentation to prevent code block rendering)
trivia_html = f'''<div class="trivia-card"><div class="trivia-header"><span class="lightbulb">💡</span><div><div class="trivia-date">📅 {trivia['date']}</div><div class="trivia-source"><span class="channel-badge">{trivia.get('category', '雑学')}</span> from {trivia.get('source', 'Unknown')}</div></div></div><div class="trivia-content">{trivia['japanese']}</div><div class="english-section"><div class="english-label">🌐 ENGLISH TRANSLATION</div><div class="english-text">{trivia['english']}</div></div></div>'''
st.markdown(trivia_html, unsafe_allow_html=True)

# Action buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📋 コピー", use_container_width=True):
        st.code(f"📌 {trivia['japanese']}\n\n🌐 {trivia['english']}")
with col2:
    if st.button("🔊 読み上げ", use_container_width=True):
        st.info("音声読み上げ機能は開発中です")
with col3:
    if st.button("📥 保存", use_container_width=True):
        # Save as knowledge card
        try:
            kpath = f"apps/job_hunting/TRIVIA_{date.today().isoformat()}.kcard"
            card_data = {
                "title": f"[雑学] {trivia['source']} - {trivia['date']}",
                "content": f"📌 {trivia['japanese']}\n\n🌐 {trivia['english']}",
                "genre": "Trivia",
                "rarity": "Common",
                "tags": ["trivia", trivia.get("category", "general")],
                "timestamp": datetime.now().isoformat()
            }
            os.makedirs("apps/job_hunting", exist_ok=True)
            with open(kpath, "w", encoding="utf-8") as f:
                json.dump(card_data, f, indent=2, ensure_ascii=False)
            st.success("知識カードとして保存しました！")
        except Exception as e:
            st.error(f"保存エラー: {e}")

# Custom trivia input
st.markdown("---")
with st.expander("✏️ 自分で雑学を追加"):
    with st.form("custom_trivia"):
        custom_jp = st.text_area("日本語の雑学", height=100, placeholder="今日学んだ面白いことを入力...")
        custom_source = st.text_input("出典（任意）", placeholder="どこで知った？")
        
        col_a, col_b = st.columns(2)
        with col_a:
            auto_translate = st.checkbox("自動で英訳", value=True)
        
        if st.form_submit_button("💾 追加"):
            if custom_jp:
                english = translate_with_ai(custom_jp) if auto_translate else "(翻訳なし)"
                history = load_trivia_history()
                history.insert(0, {
                    "date": date.today().isoformat(),
                    "japanese": custom_jp,
                    "english": english,
                    "source": custom_source or "自分のメモ",
                    "category": "カスタム",
                    "generated_at": datetime.now().isoformat()
                })
                save_trivia_history(history)
                st.success("追加しました！")
                st.rerun()

# History
st.markdown("---")
st.markdown("### 📚 過去の雑学")

history = load_trivia_history()
if len(history) > 1:
    for item in history[1:6]:  # Show last 5 (excluding today)
        st.markdown(f"""
        <div class="history-item">
            <div class="trivia-date">{item.get('date', '')} • {item.get('source', '')}</div>
            <div style="margin-top:8px;">{item.get('japanese', '')[:100]}...</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("明日以降、履歴がここに表示されます")

# Station Footer
render_station_footer()
