import streamlit as st
import time

st.set_page_config(page_title="Zen Focus", page_icon="🧘", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    .timer-display {
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        color: #FFFFFF;
        font-family: 'Courier New', monospace;
        background-color: #222;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .status-text {
        text-align: center;
        font-size: 24px;
        color: #AAAAAA;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧘 Zen Focus")
st.write("Deep Work Timer & Ambience")

# --- SETTINGS ---
minutes = st.slider("Focus Duration (min)", 5, 120, 25)
sound_option = st.selectbox("Ambience Mode", [
    "Silent (Visual Only)",
    "Rain Sounds 🌧️",
    "Forest Stream 🌲",
    "Crackling Fire 🔥",
    "Lofi Beats 🎧"
])

# --- YOUTUBE AMBIENCE ---
AMBIENCE_URLS = {
    "Rain Sounds 🌧️": "https://www.youtube.com/watch?v=mPZkdNFkNps",
    "Forest Stream 🌲": "https://www.youtube.com/watch?v=Ip0QA9qYh6I",
    "Crackling Fire 🔥": "https://www.youtube.com/watch?v=K0pJRo0XU8s",
    "Lofi Beats 🎧": "https://www.youtube.com/watch?v=jfKfPfyJRdk"
}

# --- TIMER LOGIC ---
if st.button("Start Focus Session", type="primary"):
    if sound_option != "Silent (Visual Only)":
        st.video(AMBIENCE_URLS[sound_option], autoplay=True)
        st.info("💡 Ambience playing below. Scroll down if needed.")
    
    placeholder = st.empty()
    bar = st.progress(0)
    
    total_seconds = minutes * 60
    
    for i in range(total_seconds):
        remaining = total_seconds - i
        mins = remaining // 60
        secs = remaining % 60
        
        # Format MM:SS
        time_str = f"{mins:02d}:{secs:02d}"
        
        placeholder.markdown(f"""
        <div class="timer-display">{time_str}</div>
        <div class="status-text">Stay Focused.</div>
        """, unsafe_allow_html=True)
        
        bar.progress((i + 1) / total_seconds)
        time.sleep(1)
        
    # DONE
    placeholder.markdown(f"""
    <div class="timer-display">00:00</div>
    <div class="status-text" style="color: #00FF00;">Session Complete! Take a break.</div>
    """, unsafe_allow_html=True)
    st.balloons()
