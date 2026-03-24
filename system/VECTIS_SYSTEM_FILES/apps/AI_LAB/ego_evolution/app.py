"""
🧬 EGO EVOLUTION - The Living Self Model
Port: 8521
Dialogue with your Digital Twin & Update your Ego Core.
"""

import streamlit as st
import os
import sys
import json
import time
import pandas as pd
from datetime import datetime

# --- PATH SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header
from modules.unified_llm import UnifiedLLM

# Import Ego Logic
try:
    from apps.ego_evolution.trainer import EgoSimulator
except ImportError:
    # Handle case where run from root
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    from trainer import EgoSimulator

# --- CONFIG ---
st.set_page_config(page_title="EGO EVOLUTION", page_icon="🧬", layout="wide")
apply_vectis_style()

# --- INITIALIZE ---
if "ego_sim" not in st.session_state:
    st.session_state.ego_sim = EgoSimulator()

sim = st.session_state.ego_sim
model_data = sim.model

# --- SIDEBAR ---
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🧬 EGO STATUS")
    
    identity = model_data.get("identity", {})
    st.info(f"**Archetype:**\n{identity.get('archetype', 'Uninitialized')}")
    
    st.markdown("**Core Values:**")
    for val in identity.get("core_values", ["-"]):
        st.caption(f"🔹 {val}")
        
    st.markdown("---")
    if st.button("🔄 Reload Core"):
        st.session_state.ego_sim.load_model()
        st.rerun()

# --- HEADER ---
st.markdown(get_station_header("20", "EGO EVOLUTION", "Recursive Self-Improvement System"), unsafe_allow_html=True)

# --- TABS ---
tab_chat, tab_train, tab_viz = st.tabs(["💬 Dialogue with Self", "🧠 Update Thoughts", "📊 Ego Metrics"])

# === TAB 1: DIALOGUE ===
with tab_chat:
    st.markdown("##### 🗣️ Talk to your Digital Twin")
    st.caption("このAIは、あなたの思考モデル（Ego Core）に基づいて応答します。悩みを打ち明けたり、議論したりしてください。")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Generate Response using Ego Context
            with st.spinner("Ego Core is thinking..."):
                try:
                    # Construct Prompt with Ego Context
                    system_prompt = sim._get_ego_prompt()
                    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nReply as the Ego Core. Be insightful, slightly philosophical, and true to your archetype."
                    
                    # Call Gemini
                    llm = GenerativeModel('gemini-2.0-flash-exp')
                    response = llm.generate_content(full_prompt)
                    full_response = response.text
                    
                    # Typewriter effect
                    displayed = ""
                    for chunk in full_response.split():
                        displayed += chunk + " "
                        message_placeholder.markdown(displayed + "▌")
                        time.sleep(0.05)
                    message_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"Error: {str(e)}"
                    message_placeholder.error(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# === TAB 2: UPDATE THOUGHTS (TRAINING) ===
with tab_train:
    st.markdown("##### 🧠 Ingest New Thoughts")
    st.caption("最近の気づき、読んだ本、強烈な体験などを入力してください。Ego Coreがそれを分析し、自己モデルを更新します。")
    
    input_text = st.text_area("Input your raw thoughts/experiences:", height=200)
    
    col_t1, col_t2 = st.columns([1, 1])
    
    with col_t1:
        if st.button("🚀 Update Ego Core (Deep Learning)", type="primary", use_container_width=True):
            if input_text:
                process_training(input_text)
            else:
                st.warning("Please enter some text.")

    with col_t2:
        st.markdown("###### 🔄 System Integration")
        if st.button("📥 Import & Train from EGO Apps", help="YouTube, Todo, Book Logなどのデータを統合して学習します。", use_container_width=True):
            # Gather Data
            imported_text = "【IMPORTED SYSTEM DATA】\n\n"
            
            # 1. YouTube Memos
            yt_path = os.path.join(os.path.dirname(__file__), "../youtube_channel/data/channel_memos.json")
            if os.path.exists(yt_path):
                try:
                    with open(yt_path, 'r', encoding='utf-8') as f:
                        yt_data = json.load(f)
                        imported_text += "### YouTube Learning History\n"
                        for vid, d in yt_data.items():
                            imported_text += f"- Watched: {d.get('title')}\n  Memo: {d.get('note')}\n  Summary: {d.get('summary')[:200]}...\n\n"
                        st.toast(f"Imported {len(yt_data)} videos.")
                except: pass
            
            # 2. Todo (if exists - currently empty but prepared)
            # ...
            
            if len(imported_text) > 50:
                process_training(imported_text)
            else:
                st.warning("No significant data found in other apps yet.")

def process_training(text_data):
    with st.status("Running Deep Analysis...", expanded=True) as status:
        st.write("📥 Ingesting text...")
        time.sleep(1)
        st.write("🧬 Consulting Gemini for Latent Variables...")
        
        # Run Training
        result = sim.train_from_memories(text_data)
        
        if result.get("status") == "error":
            status.update(label="Training Failed!", state="error")
            st.error(result.get("message"))
        else:
            status.update(label="Evolution Complete!", state="complete")
            
            st.success("Analysis Successful!")
            st.markdown("### 🔍 Analysis Report")
            st.info(result.get("analysis_summary"))
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**New Archetype:**")
                st.write(f"✨ {result.get('refined_archetype')}")
            with c2:
                st.markdown("**Vector Updates:**")
                st.json(result.get("vector_updates"))
                
            st.toast("Self Model Updated!")
            time.sleep(2)
            st.rerun()

# === TAB 3: VISUALIZATION ===
with tab_viz:
    st.markdown("##### 📊 Internal State Visualization")
    
    vectors = model_data.get("ego_vectors", {})
    if vectors:
        # Radar Chart Data
        df = pd.DataFrame(dict(
            r=list(vectors.values()),
            theta=list(vectors.keys())
        ))
        
        # Simple Bar Chart for now (Streamlit native)
        st.bar_chart(data=pd.Series(vectors))
        
        st.markdown("### 📜 Decision History")
        history = model_data.get("decision_history", [])
        for h in reversed(history[-10:]):
            with st.expander(f"{h['timestamp'][:16]} - {h.get('context', '')}"):
                st.write(f"**Decision:** {h.get('decision', {}).get('best_move')}")
                st.caption(f"Reasoning: {h.get('decision', {}).get('reasoning')}")
    else:
        st.warning("No Vector Data available. Please run training first.")

render_station_footer()
