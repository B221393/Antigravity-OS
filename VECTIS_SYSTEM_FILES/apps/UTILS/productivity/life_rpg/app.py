import streamlit as st
import random
import os
import json
import sys
from datetime import datetime

# Add Parent for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.style import apply_vectis_style, get_station_header
from modules.nav import render_global_road, render_station_footer

def life_rpg_app():
    st.set_page_config(page_title="⚔️ LIFE RPG | 自分ステーション", page_icon="⚔️")
    apply_vectis_style()
    
    with st.sidebar:
        render_global_road()
        
    st.markdown(get_station_header("⚔️ LIFE RPG", "日常そのものをファンタジー化する", "CH.05"), unsafe_allow_html=True)
    
    # --- 0->1 CONCEPT: NARRATIVE QUEST SYSTEM ---
    # The user doesn't just "do tasks". They "advance the plot".
    
    if "chapter" not in st.session_state:
        st.session_state.chapter = 1
        st.session_state.exp = 0
        
    st.markdown(f"""
    <div style="background:linear-gradient(45deg, #220033, #000022); padding:20px; border-radius:12px; border:1px solid #9900FF; margin-bottom:20px;">
        <h2 style="color:#DDAAFF; margin:0;">CHAPTER {st.session_state.chapter}: 覚醒 (The Awakening)</h2>
        <p style="color:#BBB;">あなたは「現実」という名の荒野に降り立った。目の前には「講談社」という名の巨塔が聳え立っている...</p>
        <div style="height:10px; background:#333; margin-top:10px; border-radius:5px;">
            <div style="width:{st.session_state.exp}%; height:100%; background:#00FFCC; border-radius:5px;"></div>
        </div>
        <p style="text-align:right; color:#00FFCC; font-size:0.8em;">NEXT CHAPTER: {100 - st.session_state.exp} XP required</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 📜 Available Quests")
        
        quests = [
            {"title": "ES生成の儀式", "desc": "Job HQを使ってESを1つ生成する", "xp": 30, "type": "MAIN"},
            {"title": "英単語の鍛錬", "desc": "TOEICアプリでPart1をクリアする", "xp": 10, "type": "DAILY"},
            {"title": "雑念の浄化", "desc": "HUDのInboxを空にする", "xp": 15, "type": "SUB"},
        ]
        
        for q in quests:
            badge_color = "#FF0055" if q['type']=="MAIN" else "#00CCFF"
            if st.button(f"受諾: {q['title']} (+{q['xp']} XP)", key=q['title'], use_container_width=True):
                st.session_state.exp += q['xp']
                if st.session_state.exp >= 100:
                    st.session_state.chapter += 1
                    st.session_state.exp = 0
                    st.balloons()
                st.rerun()
                
    with c2:
        st.markdown("### 🎒 Inventory (Rewards)")
        st.info("ここに「完了したタスク」が『武器』や『アーティファクト』として変換され、コレクションされます。（開発中）")
        
    render_station_footer()

if __name__ == "__main__":
    life_rpg_app()
