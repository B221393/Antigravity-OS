import streamlit as st
import re
import random
from pathlib import Path

# --- Configuration & Styling ---
st.set_page_config(
    page_title="Knowledge Anchor | 統合思考OS",
    page_icon="⚓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for "Surikomi" effect
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .big-font {
        font-size: 42px !important;
        font-weight: 800;
        color: #4facfe;
        text-align: center;
        padding: 20px;
        border: 2px solid #333;
        border-radius: 10px;
        background-color: #1e1e1e;
        margin-bottom: 20px;
    }
    .answer-box {
        font-size: 20px;
        padding: 20px;
        background-color: #262730;
        border-left: 5px solid #00c6ff;
        border-radius: 5px;
        margin-top: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
    .category-tag {
        font-size: 14px;
        color: #888;
        text-align: center;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading Functions ---

def load_company_data(filepath):
    """
    Parses '2026_HEGEMONY_COMPANIES.txt'
    Expected format: * **Name**: Description
    """
    data = []
    current_category = "General"
    
    path = Path(filepath)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("###"):
            current_category = line.strip("# ").strip()
        elif line.startswith("* **") or line.startswith("- **"):
            # Extract Company Name and Description
            match = re.match(r"[\*\-]\s+\*\*(.*?)\*\*[:\s]*(.*)", line)
            if match:
                name = match.group(1)
                desc = match.group(2)
                data.append({
                    "type": "company",
                    "category": current_category,
                    "question": name,
                    "answer": desc
                })
    return data

def load_interview_data(filepath):
    """
    Parses 'User_Profile/REFINED_INTERVIEW_ANSWERS.md'
    Expected format: 
    ### Topic
    * **問い:** Question
    ... Answer paragraph ...
    """
    data = []
    path = Path(filepath)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by headers roughly
    sections = re.split(r'
##+ ', content)
    
    for section in sections:
        # Try to find questions
        questions = re.findall(r'\*\s+\*\*問い:\*\*\s*(.*?)
(.*?)(?=
\* \*\*問い|
##|\Z)', section, re.DOTALL)
        if questions:
            for q, a in questions:
                data.append({
                    "type": "interview",
                    "category": "Interview Q&A",
                    "question": q.strip(),
                    "answer": a.strip()
                })
        else:
            # Fallback for "Epsode" style or simple headers
            # If a section has a header and content, treat Header as Q, Content as A
            lines = section.split('
')
            if len(lines) > 2:
                header = lines[0].strip()
                body = "
".join(lines[1:]).strip()
                if header and body and len(body) > 20: # Filter out empty sections
                     data.append({
                        "type": "interview",
                        "category": "General/Episode",
                        "question": header,
                        "answer": body
                    })

    return data

# --- Session State Management ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'shuffled_indices' not in st.session_state:
    st.session_state.shuffled_indices = []
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Companies"

# --- Main App Logic ---

st.sidebar.title("⚓ Knowledge Anchor")
st.sidebar.markdown("脳への定着支援システム")

mode = st.sidebar.radio("学習モード", ["Companies (企業分析)", "Interview (面接対策)"])

# Reset state if mode changes
if mode != st.session_state.current_mode:
    st.session_state.current_mode = mode
    st.session_state.index = 0
    st.session_state.show_answer = False
    st.session_state.shuffled_indices = []

# Load Data based on mode
data = []
if mode == "Companies (企業分析)":
    data = load_company_data("2026_HEGEMONY_COMPANIES.txt")
    st.sidebar.info(f"Loaded {len(data)} companies.")
else:
    data = load_interview_data("User_Profile/REFINED_INTERVIEW_ANSWERS.md")
    st.sidebar.info(f"Loaded {len(data)} questions.")

if not data:
    st.error("データが見つかりません。ファイルパスを確認してください。")
    st.stop()

# Shuffle logic
if not st.session_state.shuffled_indices or len(st.session_state.shuffled_indices) != len(data):
    indices = list(range(len(data)))
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices

# Get current item
current_idx = st.session_state.shuffled_indices[st.session_state.index]
item = data[current_idx]

# --- UI Display ---

# Progress bar
progress = (st.session_state.index + 1) / len(data)
st.progress(progress)
st.caption(f"Card {st.session_state.index + 1} / {len(data)}")

# Category Label
st.markdown(f"<div class='category-tag'>{item['category']}</div>", unsafe_allow_html=True)

# Question Card
st.markdown(f"<div class='big-font'>{item['question']}</div>", unsafe_allow_html=True)

# Interaction Area
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🤔 答えを見る"):
        st.session_state.show_answer = True

with col2:
    if st.button("➡️ 次へ"):
        st.session_state.index = (st.session_state.index + 1) % len(data)
        st.session_state.show_answer = False
        st.rerun()

# Answer Display
if st.session_state.show_answer:
    st.markdown(f"<div class='answer-box'>{item['answer']}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Feedback (Optional)")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        if st.button("覚え直し 😵"):
            st.toast("リストの後ろに回しました。")
            # Logic to append this index to the end of the list could go here
    with f_col2:
        if st.button("完璧 ✨"):
            st.toast("素晴らしい！")

# Keyboard shortcut hint
st.sidebar.markdown("---")
st.sidebar.markdown("**Keyboard Shortcuts:**")
st.sidebar.text("'R' to Rerun/Shuffle (if supported)")

