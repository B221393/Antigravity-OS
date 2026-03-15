"""
🪄 カード工房 (Creator) - 自分ステーション
Port: 8507
知識カードを新規作成・編集
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(
    page_title="🪄 カード工房 | 自分ステーション",
    page_icon="🪄",
    layout="wide"
)

# Load Env
load_dotenv("../../.env")

# Apply Station Style
apply_vectis_style()

# Custom extension for Creator (pink theme)
st.markdown("""
<style>
    /* Creator-specific accent color: Hot Pink */
    h1 {
        color: var(--hot-pink) !important;
        text-shadow: 0 0 15px var(--hot-pink-glow) !important;
    }
    
    .creator-card {
        background: linear-gradient(135deg, var(--bg-secondary), rgba(255, 0, 170, 0.05));
        border: 2px solid rgba(255, 0, 170, 0.2);
        border-radius: 20px;
        padding: 40px;
        margin: 20px 0;
        position: relative;
        overflow: hidden;
    }
    
    .creator-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--hot-pink), var(--electric-blue));
    }
    
    .stButton > button:hover {
        border-color: var(--hot-pink) !important;
        box-shadow: 0 0 20px var(--hot-pink-glow) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--hot-pink), #CC0088) !important;
        color: white !important;
    }
    
    .rarity-legendary {
        color: #FFD700;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    
    .rarity-epic {
        color: #9B59B6;
    }
    
    .rarity-rare {
        color: var(--electric-blue);
    }
    
    .rarity-common {
        color: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()

# Header
st.markdown(get_station_header(
    title="🪄 カード工房",
    subtitle="知識の「点」を新たに生成する",
    channel_id="TOOL.04"
), unsafe_allow_html=True)

# Main Form
st.markdown('<div class="creator-card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    title = st.text_input("📝 タイトル", placeholder="例: 講談社の社風")
    genre = st.selectbox("🏷️ ジャンル", [
        "Technology", "Business", "Job Hunting", "Career", 
        "Vision", "Language", "History", "Science", "General"
    ])
    rarity = st.select_slider(
        "⭐ 重要度 (Rarity)", 
        options=["Common", "Rare", "Epic", "Legendary"],
        help="Legendaryは特に重要な学び"
    )

with col2:
    content = st.text_area(
        "📄 内容・知見", 
        height=200, 
        placeholder="ここに得られた知識や思考を記してください...\n\n例:\n- 何を学んだか\n- なぜ重要か\n- どう活用するか"
    )

tags = st.text_input("🔖 タグ (カンマ区切り)", placeholder="publishing, kodansha, culture")

# Rarity Preview
rarity_class = f"rarity-{rarity.lower()}"
st.markdown(f"""
<div style="text-align: center; margin: 20px 0;">
    <span class="{rarity_class}" style="font-size: 1.5rem; font-weight: bold;">
        ⭐ {rarity} Card
    </span>
</div>
""", unsafe_allow_html=True)

# Submit Button
if st.button("🚀 知識カードを射出 (CREATE CARD)", type="primary", use_container_width=True):
    if title and content:
        # Generate filename
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).rstrip()
        filename = f"apps/job_hunting/{safe_title.replace(' ', '_')}.kcard"
        
        card_data = {
            "title": title,
            "content": content,
            "genre": genre,
            "rarity": rarity,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "timestamp": datetime.now().isoformat(),
            "source": "Creator"
        }
        
        try:
            os.makedirs("apps/job_hunting", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(card_data, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ カードを生成しました: `{filename}`")
            st.balloons()
            
            # Show preview
            with st.expander("📋 カードプレビュー", expanded=True):
                st.json(card_data)
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
    else:
        st.warning("⚠️ タイトルと内容を入力してください。")

st.markdown('</div>', unsafe_allow_html=True)

# Tips
with st.expander("💡 カード作成のコツ"):
    st.markdown("""
    ### 良いカードの条件
    
    1. **具体的なタイトル**: 何についてのカードか一目で分かるように
    2. **構造化された内容**: 箇条書きや段落で整理
    3. **適切なタグ**: 後から検索しやすいキーワードを設定
    
    ### Rarity の目安
    
    | Rarity | 説明 |
    |--------|------|
    | Common | 一般的な知識・メモ |
    | Rare | 面接で使える具体的なエピソード |
    | Epic | 志望動機の核になる重要な気づき |
    | Legendary | 人生の軸になる価値観・ビジョン |
    """)

# Footer
render_station_footer()
