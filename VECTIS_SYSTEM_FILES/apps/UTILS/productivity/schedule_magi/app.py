import streamlit as st
import pandas as pd
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import sys
import datetime
import json
import random

# Path setup for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from modules.unified_llm import UnifiedLLM

# --- DEPENDENCY CHECK ---
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Central Data Store
DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, '../../data/precog_schedules.json'))

st.set_page_config(page_title="VECTIS PRECOGNITION", page_icon="🔮", layout="wide")

# Initialize LLM (Optimized with Caching)
@st.cache_resource
def get_llm():
    return UnifiedLLM(provider="ollama", model_name="phi4")

llm = get_llm()

# --- CSS / MAGI UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* === GLOBAL RESET & BACKGROUND === */
    .stApp {
        background-color: #000000;
        /* Honeycomb Pattern */
        background-image: 
            radial-gradient(circle at center, transparent 0%, #000000 80%),
            linear-gradient(30deg, #110800 12%, transparent 12.5%, transparent 87%, #110800 87.5%, #110800),
            linear-gradient(150deg, #110800 12%, transparent 12.5%, transparent 87%, #110800 87.5%, #110800),
            linear-gradient(30deg, #110800 12%, transparent 12.5%, transparent 87%, #110800 87.5%, #110800),
            linear-gradient(150deg, #110800 12%, transparent 12.5%, transparent 87%, #110800 87.5%, #110800),
            linear-gradient(60deg, #22110077 25%, transparent 25.5%, transparent 75%, #22110077 75%, #22110077),
            linear-gradient(60deg, #22110077 25%, transparent 25.5%, transparent 75%, #22110077 75%, #22110077);
        background-size: 80px 140px;
        background-position: 0 0, 0 0, 0 0, 40px 70px, 40px 70px, 0 0, 40px 70px;
        font-family: 'Orbitron', monospace;
        color: #ff9900;
    }

    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, p, div, span, input, button {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    h1 {
        text-align: center;
        font-size: 3em !important;
        background: linear-gradient(to right, transparent, #ff9900 20%, #ff9900 80%, transparent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px #ff9900;
        border-bottom: 2px solid #ff9900;
        margin-bottom: 30px;
    }

    /* === MAGI HEXAGON SYSTEM (Vote Blocks) === */
    .magi-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 20px 0;
        padding: 20px;
        background: rgba(255,153,0,0.05);
        border-top: 2px solid #ff9900;
        border-bottom: 2px solid #ff9900;
    }
    
    .magi-hex {
        width: 250px;
        height: 140px;
        background: rgba(0,0,0,0.9);
        border-left: 5px solid #ff9900;
        border-right: 5px solid #ff9900;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 0 15px rgba(255, 153, 0, 0.4), inset 0 0 20px rgba(255, 153, 0, 0.2);
    }
    .magi-hex::before {
        content: "";
        position: absolute;
        top: -20px;
        left: 0;
        width: 100%;
        height: 20px;
        border-bottom: 2px solid #ff9900;
        background: linear-gradient(to bottom, transparent, rgba(255,153,0,0.2));
    }
    .magi-hex-title {
        font-size: 1.8em;
        font-weight: 900;
        color: #ff9900;
        text-shadow: 0 0 10px #ff9900;
    }
    .magi-hex-sub {
        font-size: 0.8em;
        color: #cc7a00;
    }
    .magi-hex-status {
        margin-top: 10px;
        font-size: 1.2em;
        padding: 2px 10px;
        background: #ff9900;
        color: #000;
        font-weight: bold;
        box-shadow: 0 0 10px #ff9900;
    }

    /* === INPUT TERMINAL === */
    .stTextInput input {
        background-color: #000 !important;
        border: 2px solid #ff9900 !important;
        color: #ff9900 !important;
        font-size: 1.2em;
        box-shadow: 0 0 10px rgba(255,153,0,0.3);
    }
    
    /* === BUTTONS === */
    .stButton button {
        background: #000;
        border: 2px solid #ff9900;
        color: #ff9900;
        font-weight: 900;
        transition: all 0.2s;
        text-shadow: 0 0 5px #ff9900;
    }
    .stButton button:hover {
        background: #ff9900;
        color: #000;
        box-shadow: 0 0 20px #ff9900, inset 0 0 10px #fff;
    }

    /* === SCHEDULE CARDS === */
    .schedule-card {
        border-left: 10px solid #ff9900;
        background: linear-gradient(90deg, rgba(255,153,0,0.1) 0%, rgba(0,0,0,0.8) 100%);
        margin-bottom: 10px;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,153,0,0.3);
    }
    .schedule-time {
        font-size: 2em;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 10px #fff;
        margin-right: 20px;
    }
    .schedule-event {
        font-size: 1.2em;
        flex-grow: 1;
        color: #ffcc00;
    }
    .schedule-priority {
        background: #ff0000;
        color: #fff;
        padding: 5px 10px;
        font-weight: bold;
        border: 1px solid #fff;
        box-shadow: 0 0 10px #ff0000;
    }
    
    /* === SCROLLBAR & SYSTEM === */
    ::-webkit-scrollbar { width: 10px; background: #000; }
    ::-webkit-scrollbar-thumb { background: #ff9900; border: 1px solid #fff; }

    /* === SCANLINE OVERLAY === */
    .scanlines {
        position: fixed;
        left: 0;
        top: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
        z-index: 9999;
        opacity: 0.6;
    }
</style>
<div class="scanlines"></div>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Date", "Time", "Event", "Type", "Priority", "Status"])
    
    # Check file extension to determine loader
    if DATA_FILE.endswith('.csv'):
        return pd.read_csv(DATA_FILE)
    elif DATA_FILE.endswith('.json'):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)

def save_data(df):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # Save as JSON for better structure preservation
    json_path = DATA_FILE.replace('.csv', '.json')
    data = df.to_dict(orient='records')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    # Keep CSV for backward compatibility / Excel viewing if needed
    if DATA_FILE.endswith('.csv'):
        df.to_csv(DATA_FILE, index=False)


# ... (Previous imports and functions) ...

# === THOUGHT INJECTION LOGIC ===
SELF_MODEL_FILE = os.path.join(DATA_DIR, "../apps/ego_evolution/data/self_model.json")

def inject_thought(thought_text):
    """Injects a raw thought/emotion into the Self Model's narrative log."""
    if not os.path.exists(SELF_MODEL_FILE):
        return "Ego Model Not Found."
    
    try:
        with open(SELF_MODEL_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Initialize thought log if missing
        if "thought_log" not in data:
            data["thought_log"] = []
            
        # Add Entry
        entry = {
            "timestamp": str(datetime.datetime.now()),
            "thought": thought_text,
            "type": "Raw Injection"
        }
        data["thought_log"].append(entry)
        
        # --- AI ARCHITECT UPDATE (Optional: Auto-update Vision?) ---
        # For now, we just save raw thoughts. Future: AI analyzes them to shift Ego Vectors.
        
        with open(SELF_MODEL_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return "THOUGHT INTEGRATED."
    except Exception as e:
        return f"INJECTION ERROR: {e}"

def analyze_input(text):
    """
    Enhanced MAGI Analysis.
    Detects if input is a 'Schedule' or a 'Thought Injection'.
    """
    
    # Check for direct thought injection keywords or context
    # Simple heuristic: If it looks philosophical or emotional, treat as thought.
    # But user wants a dedicated UI area maybe? Let's auto-detect for now.
    
    prompt = f"""
    【SYSTEM: MAGI CLASSIFIER】
    Input: "{text}"
    
    Classify this input into one of two types:
    A. "SCHEDULE": A request to add/check calendar events.
    B. "THOUGHT": A philosophical statement, emotion, or idea the user wants to 'inject' into their self-model.
    
    Output JSON: {{ "class": "SCHEDULE" or "THOUGHT" }}
    """
    try:
        # Pre-check for speed
        if len(text) > 10 and not any(k in text for k in ["明日", "来週", "予定", "スケジュール"]):
            # Let LLM decide strictly
            pass
            
        res_class = llm.generate(prompt)
        # ... parse logic ... 
        # For simplicity in this diff, we defaults to schedule analysis if ambiguous,
        # but let's add a dedicated "Injection" mode in UI handling.
    except:
        pass 

    # ... (Original Schedule Analysis Logic) ...
    # We will modify the UI part to handle 'Injection' separately for clarity.
    
    return json.loads(llm.generate(f"""
    【SYSTEM: MAGI CRITERIA】
    Analyze: "{text}"
    Current Date: {datetime.datetime.now()}
    Output strictly in JSON format:
    {{
        "decision": {{"melchior": "agree", "balthasar": "agree", "casper": "agree"}},
        "data": {{
            "Date": "...", "Time": "...", "Event": "...", "Type": "...", "Priority": "..."
        }}
    }}
    """).replace("```json","").replace("```",""))

# ... (UI Section) ...


def listen_to_mic():
    if not VOICE_AVAILABLE:
        st.error("SpeechRecognition library not installed.")
        return None
        
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now.")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        return r.recognize_google(audio, language="ja-JP")
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        st.warning("Could not understand audio.")
        return None
    except sr.RequestError:
        st.error("Voice Recognition API Error")
        return None
    except Exception as e:
        st.error(f"Mic Error: {e} (PyAudio installed?)")
        return None

# --- MAIN APP ---
st.title("🔮 VECTIS PRECOGNITION SYSTEM")

# --- SIDEBAR: SYSTEM CONTROL ---
with st.sidebar:
    st.header("⚙ SYSTEM CONTROL")
    st.markdown("---")
    st.subheader("⌨ KEYBOARD LAYOUT")
    
    col_kb1, col_kb2 = st.columns(2)
    with col_kb1:
        if st.button("ONISHI", use_container_width=True):
            bat_path = os.path.abspath(os.path.join(BASE_DIR, "../onishi/01_大西配列を開始する.bat"))
            if os.path.exists(bat_path):
                import subprocess
                subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True)
                st.toast("✅ ONISHI LAYOUT ACTIVATED")
            else:
                st.error("Script not found")
                
    with col_kb2:
        if st.button("QWERTY", use_container_width=True):
            bat_path = os.path.abspath(os.path.join(BASE_DIR, "../onishi/02_大西配列を終了して元に戻す.bat"))
            if os.path.exists(bat_path):
                import subprocess
                subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True)
                st.toast("✅ QWERTY RESTORED")
            else:
                st.error("Script not found")
    st.markdown("---")

# Input Section
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🎙️ VOICE INPUT"):
        voice_text = listen_to_mic()
        if voice_text:
            st.session_state['input_text'] = voice_text
            st.success(f"Recognized: {voice_text}")
        elif not VOICE_AVAILABLE:
            st.warning("Install SpeechRecognition & PyAudio")

with col2:
    input_text = st.text_input("Manual Command Entry", value=st.session_state.get('input_text', ""), key="input_text_box")

    if input_text:
        # 1. First, check classification (Schedule vs Thought)
        classifier_res = None
        try:
             # Fast classify
             class_prompt = f"Classify input: '{input_text}'. Is it SCHEDULE (appointment/todo) or THOUGHT (philosophy/feeling)? JSON: {{'class': '...'}}"
             classifier_res = json.loads(llm.generate(class_prompt).replace("```json","").replace("```",""))
        except:
             classifier_res = {"class": "SCHEDULE"} # Default
             
        if classifier_res.get("class") == "THOUGHT":
            with st.spinner("MAGI: SYNCHRONIZING THOUGHT PATTERN..."):
                status = inject_thought(input_text)
                
                # Visual Feedback for Thought Injection
                st.markdown(f"""
                <div style="border: 1px solid #00FF00; background: rgba(0,255,0,0.1); padding: 15px; border-radius: 5px; margin-top:20px;">
                    <h3 style="color: #00FF00; margin:0;">🧠 THOUGHT PATTERN RECOGNIZED</h3>
                    <p style="color: #fff;">"{input_text}"</p>
                    <p style="color: #888; font-size:0.8em; text-align:right;">INTEGRATED INTO EGO KERNEL</p>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            # Traditional MAGI Analysis (Schedule)
            if st.button("⚠️ EXECUTE MAGI ANALYSIS", key="magi_btn"):
                with st.spinner("MAGI SYSTEM: PROCESSING..."):
                    result = analyze_input(input_text)
                    
                    if result:
                        decision = result.get('decision', {})
                        data = result.get('data', {})
                        
                        # MAGI HEXAGON DISPLAY
                        m_col, b_col, c_col = st.columns(3)
                        
                        # MELCHIOR
                        m_status = decision.get("melchior", "agree")
                        m_color = "#00FFFF" if m_status == "agree" else "#FF0000"
                        with m_col:
                            st.markdown(f"""
                            <div class="magi-hex" style="border-color:{m_color}; box-shadow: 0 0 15px {m_color};">
                                <div class="magi-hex-title" style="color:{m_color}; text-shadow: 0 0 10px {m_color};">MELCHIOR</div>
                                <div style="color:{m_color}; margin-top:10px;">SCIENTIST<br>STATUS: {m_status.upper()}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        # BALTHASAR
                        b_status = decision.get("balthasar", "agree")
                        b_color = "#FFA500" if b_status == "agree" else "#FF0000"
                        with b_col:
                            st.markdown(f"""
                            <div class="magi-hex" style="border-color:{b_color}; box-shadow: 0 0 15px {b_color};">
                                <div class="magi-hex-title" style="color:{b_color}; text-shadow: 0 0 10px {b_color};">BALTHASAR</div>
                                <div style="color:{b_color}; margin-top:10px;">MOTHER<br>STATUS: {b_status.upper()}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        # CASPER
                        c_status = decision.get("casper", "agree")
                        c_color = "#FF0055" if c_status == "agree" else "#FF0000"
                        with c_col:
                            st.markdown(f"""
                            <div class="magi-hex" style="border-color:{c_color}; box-shadow: 0 0 15px {c_color};">
                                <div class="magi-hex-title" style="color:{c_color}; text-shadow: 0 0 10px {c_color};">CASPER</div>
                                <div style="color:{c_color}; margin-top:10px;">WOMAN<br>STATUS: {c_status.upper()}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        # --- DECISION LOGIC ---
                        if "disagree" in [m_status, b_status, c_status]:
                            st.error("MAGI CONFLICT: PROPOSAL REJECTED.")
                        else:
                            st.success("MAGI CONSENSUS: APPROVED.")
                            
                            # Save to DF
                            new_row = {
                                "Date": data.get("Date"),
                                "Time": data.get("Time"),
                                "Event": data.get("Event"),
                                "Type": data.get("Type", "TODAY"),
                                "Priority": data.get("Priority", 3),
                                "Status": "Pending"
                            }
                            new_df = pd.DataFrame([new_row])
                            df = pd.concat([df, new_df], ignore_index=True)
                            save_data(df)
                            st.info("PROTOCOL ADDED TO DATABASE.")
                            st.rerun()

# --- DASHBOARD ---
df = load_data()
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    today = pd.to_datetime(datetime.datetime.now().date())
    
    # Filter
    today_schedule = df[df['Date'].dt.date == today.date()].sort_values(by='Time')
    future_schedule = df[df['Date'] > today].sort_values(by='Date')
    
    st.markdown("---")
    
    # TODAY LIST
    st.header(f"📅 TODAY'S PROTOCOLS: {today.strftime('%Y-%m-%d')}")
    if not today_schedule.empty:
        for idx, row in today_schedule.iterrows():
            st.markdown(f"""
            <div class="schedule-card">
                <div style="display:flex; align_items:center;">
                    <span class="schedule-time">{row['Time']}</span> 
                    <span class="schedule-event">{row['Event']}</span>
                </div>
                <div>
                    <span class="schedule-priority">PRIORITY {row['Priority']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("NO ACTIVE PROTOCOLS FOR TODAY.")

    st.markdown("---")
    st.header("🔭 LONG-TERM STRATEGY")
    if not future_schedule.empty:
        # Styled Dataframe
        st.dataframe(future_schedule[['Date', 'Time', 'Event', 'Priority', 'Type']], use_container_width=True)

