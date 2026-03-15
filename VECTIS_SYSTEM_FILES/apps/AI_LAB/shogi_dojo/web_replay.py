import streamlit as st
import os
import sys

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

st.set_page_config(page_title="SHOGI DOJO - REPLAY", page_icon="☖", layout="wide")

# CSS for "Organic/Cyber" UI (Matching User's Vision)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&family=JetBrains+Mono:wght@400&display=swap');

    /* Global */
    .stApp {
        background-color: #05070a;
        background-image: radial-gradient(circle at 50% 50%, #111926 0%, #05070a 80%);
        color: #fff;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'JetBrains Mono', monospace;
        color: #00f3ff !important;
        text-shadow: 0 0 10px #00f3ff;
        text-align: center;
    }

    /* Container centering */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Chat Bubble / Log */
    .chat-bubble {
        background: rgba(20, 30, 40, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 3px solid #ff9900;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Buttons */
    .stButton button {
        background: rgba(0, 243, 255, 0.1);
        border: 1px solid #00f3ff;
        color: #00f3ff;
        font-family: 'JetBrains Mono', monospace;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background: #00f3ff;
        color: #000;
        box-shadow: 0 0 15px #00f3ff;
    }

    /* Board Frame */
    iframe {
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
        border: 1px solid rgba(0, 243, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("☖ SHOGI DOJO REPLAY")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📺 Game Board")
    # Display the HTML Board Viewer
    # Ideally we pass SFEN via GET param if we serve it, but reading file is local.
    # We use basic HTML component.
    
    html_path = os.path.join(os.path.dirname(__file__), "resources/board_viewer.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    st.components.v1.html(html_content, height=600, scrolling=False)

with col2:
    st.markdown("### 💬 Move Log (Chat Style)")
    
    # List latest games
    log_dir = os.path.join(os.path.dirname(__file__), "training_logs")
    if os.path.exists(log_dir):
        files = sorted([f for f in os.listdir(log_dir) if f.endswith(".sfen")], reverse=True)
        
        selected_file = st.selectbox("Select Game Record", files)
        
        if selected_file:
            path = os.path.join(log_dir, selected_file)
            with open(path, "r") as f:
                content = f.read()
            
            st.code(content, language="text")
            
            st.info("💡 Copy the SFEN above and click 'Load from Clipboard' on the board!")
            
            # Chat Analysis (Simulation)
            st.markdown("---")
            st.markdown("#### 🧠 AI Analysis")
            if "EGO" in selected_file:
                st.markdown("""
                <div class='chat-bubble'>
                    <b>EGO AI:</b> This was a tough game. The middle game strategy was AGGRESSIVE.
                </div>
                """, unsafe_allow_html=True)
                
    else:
        st.write("No game logs found.")

st.markdown("---")
if st.button("Launch Native GUI App"):
    # Trigger the separate process?
    # Streamlit cannot easily launch GUI on server side if headless, but locally OK.
    st.warning("Please use the Dashboard to launch the Native App.")
