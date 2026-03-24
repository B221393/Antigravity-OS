import streamlit as st
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Abstract Writer", page_icon="📝")
st.title("📝 Abstract Writer [Upper Rank 7]")

if not API_KEY:
    st.error("API Key Missing")
    st.stop()
    
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Transfer Pickup
TF = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../transfer.txt"))
default_txt = ""
if os.path.exists(TF):
    with open(TF, "r", encoding="utf-8") as f:
        default_txt = f.read()

txt = st.text_area("Input Text (or picked up from News)", default_txt, height=300)

if st.button("Generate Abstract"):
    with st.spinner("AI Processing..."):
        try:
            res = model.generate_content(f"Summarize this into a professional abstract:\n\n{txt[:8000]}")
            st.subheader("Abstract")
            st.write(res.text)
        except Exception as e:
            st.error(str(e))
