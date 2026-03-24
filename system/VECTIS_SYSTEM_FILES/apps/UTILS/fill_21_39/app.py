import streamlit as st
import sys
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass

# Import unified UI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../modules")))
import vectis_ui

# --- Utility Hub Logic ---
# This app serves multiple launchers by checking command line args or default selection

# Map IDs to Functions
APPS = {
    "STOPWATCH": "⏱️ Stopwatch",
    "DICEROLLER": "🎲 Dice Roller",
    "TEXTCLEANER": "🧹 Text Cleaner",
    "IPCHECKER": "🌐 IP Checker",
    "SYSMONITOR": "🖥️ Sys Monitor",
    "MDCHEAT": "📝 MD Cheat",
    "GITCHEAT": "🐙 Git Cheat",
    "POMODORO": "🍅 Pomodoro",
    "BREATHE": "🧘 Breathe",
    "REACTION": "⚡ Reaction",
    "TYPING": "⌨️ Typing",
    "FLASHCARDS": "📇 Flashcards",
    "NOTEPAD": "🗒️ Notepad",
    "TODO": "✅ Todo Mini",
    "EXPENSE": "💰 Expense",
    "HABIT": "📅 Habit",
    "BIO": "💓 Bio Rhythm",
    "MOON": "🌑 Moon Phase",
    "WEATHER": "☀️ Weather Mock",
    "DEFAULT": "🧰 Utility Hub"
}

# Detect Mode from Args (passed by launcher: python app.py -- STOPWATCH)
mode = "DEFAULT"
if len(sys.argv) > 1:
    # Try to find a key in args
    for arg in sys.argv:
        u_arg = arg.upper().replace("_", "")
        # Fuzzy match arg to keys
        for k in APPS.keys():
            if k in u_arg:
                mode = k
                break

vectis_ui.setup_page(APPS.get(mode, "Utility"), "🧰")

# Render
st.title(APPS.get(mode, "Utility Hub"))

# --- Implementations (Enhanced) ---

if mode == "STOPWATCH":
    import time
    if 'stw_start' not in st.session_state: st.session_state.stw_start = None
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Start"): st.session_state.stw_start = time.time()
    if c2.button("Stop"): st.session_state.stw_start = None
    if c3.button("Reset"): st.session_state.stw_start = None; st.rerun()

    if st.session_state.stw_start:
        diff = time.time() - st.session_state.stw_start
        st.metric("Time", f"{diff:.2f} s")
        time.sleep(0.1); st.rerun()

elif mode == "TEXTCLEANER":
    txt = st.text_area("Input Text")
    c1, c2, c3 = st.columns(3)
    if c1.button("Remove Whitespace"):
        st.code(" ".join(txt.split()))
    if c2.button("To Uppercase"):
        st.code(txt.upper())
    if c3.button("To One Line"):
        st.code(txt.replace("\n", " "))

elif mode == "SYSMONITOR":
    import psutil
    import time
    placeholder = st.empty()
    if st.button("Start Monitor"):
        for _ in range(10): # Run for a bit
            with placeholder.container():
                c1, c2, c3 = st.columns(3)
                c1.metric("CPU", f"{psutil.cpu_percent()}%")
                c2.metric("RAM", f"{psutil.virtual_memory().percent}%")
                c3.metric("Disk", f"{psutil.disk_usage('/').percent}%")
            time.sleep(1)

elif mode == "MDCHEAT":
    st.markdown("""
    | Syntax | Description |
    |Str|Hdr|
    |---|---|
    |`# H1`|Header 1|
    |`**B**`|Bold|
    |`[Tx](Ur)`|Link|
    |`![Al](Im)`|Image|
    |`> Qt`|Quote|
    |`---`|Line|
    """)

else:
    # Default Hub View (if launched directly or unknown arg)
    st.info("Select specific utility mode or launch from Main Launcher.")
    sel = st.selectbox("Switch Mode", list(APPS.keys()))
    if st.button("Go"):
        st.query_params["mode"] = sel # Streamlit reloading logic trick
        st.rerun()
