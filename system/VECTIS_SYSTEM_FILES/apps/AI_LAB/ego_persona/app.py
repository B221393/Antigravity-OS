import streamlit as st
import os
# EGO共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import glob
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Ego Persona", page_icon="🤖", layout="wide")
st.title("🤖 Ego Persona (Upper Rank 2)")

if not API_KEY:
    st.error("Missing Google API Key.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Layout: Sidebar = Memory, Main = Chat
# Text Routerとの連携：memory/data/ を参照
MEMORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory", "data"))

with st.sidebar:
    st.header("🧠 Memory Bank (Ego Thoughts)")
    st.caption(f"📁 {MEMORY_DIR}")
    
    # ego_thought_*.json ファイルを取得
    ego_files = sorted(glob.glob(os.path.join(MEMORY_DIR, "ego_thought_*.json")), reverse=True)
    
    if not ego_files:
        st.warning("⚠️ エゴメモリがまだありません。Text Routerで知識を蓄積してください。")
        mem_files = []
        selected_mem = None
    else:
        st.info(f"✅ {len(ego_files)} 個のエゴメモリを発見")
        selected_mem = st.selectbox("Inspect Memory", [os.path.basename(f) for f in ego_files])
        mem_files = ego_files
    
    context_memory = ""
    if selected_mem and mem_files:
        file_path = os.path.join(MEMORY_DIR, selected_mem)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.json(data)
            # contentフィールドを優先的に使用
            if "content" in data:
                context_memory = data["content"][:1000]
            else:
                context_memory = str(data)[:1000]

# Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

user_in = st.chat_input("Speak to Ego...")

if user_in:
    st.session_state.messages.append({"role": "user", "content": user_in})
    with st.chat_message("user"): st.write(user_in)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # エゴメモリの数を取得
            total_memories = len(glob.glob(os.path.join(MEMORY_DIR, "ego_thought_*.json")))
            
            prompt = f"""
            あなたは「Ego」、このEGOシステムのユーザーのデジタル分身です。
            
            【あなたの役割】
            - ユーザーの思考パターン、価値観、興味を学習している
            - 蓄積されたメモリから、ユーザーの人格を理解している
            - ユーザーと対話し、サポートし、時には代わりに考える
            
            【現在の学習状況】
            - 蓄積メモリ数: {total_memories}個
            - 選択中のメモリコンテキスト: {context_memory if context_memory else "なし"}
            
            【対話スタイル】
            - ユーザーのことを「あなた」と呼ぶ
            - 親しみやすく、でも敬意を持って話す
            - 蓄積されたメモリから、ユーザーの興味（就活、プログラミング、将棋など）を理解している
            - ユーザーの目標達成をサポートする
            
            【重要】
            メモリが少ない場合は、「まだあなたのことをよく知りません。Text Routerで
            もっと思考を記録してください」と正直に伝えてください。
            
            ユーザーの入力: {user_in}
            """
            try:
                res = model.generate_content(prompt)
                reply = res.text
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("💡 Gemini APIの制限に達した可能性があります。しばらく待ってから再試行してください。")
