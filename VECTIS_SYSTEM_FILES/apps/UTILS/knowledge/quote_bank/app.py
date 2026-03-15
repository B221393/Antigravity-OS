import streamlit as st
import json
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import random
# Using HTML5 Speech Synthesis for browser-side TTS (no backend dependency)

st.set_page_config(page_title="Quote Bank", page_icon="💬")
st.title("💬 Quote Bank [Rank 19]")

DB = "quotes.json"
if not os.path.exists(DB):
    with open(DB, "w") as f: json.dump([], f)

with open(DB, "r") as f: quotes = json.load(f)

# Input
with st.expander("Add Quote"):
    q_text = st.text_area("Quote")
    q_author = st.text_input("Source")
    if st.button("Save"):
        quotes.append({"Quote": q_text, "Source": q_author})
        with open(DB, "w") as f: json.dump(quotes, f)
        st.success("Saved!")

st.divider()

if quotes:
    if st.button("🎲 Inspire Me (Audio)"):
        pick = random.choice(quotes)
        text = pick['Quote']
        src = pick['Source']
        
        st.markdown(f"> **{text}**")
        st.caption(f"— {src}")
        
        # Audio
        # HTML5 TTS Javascript Injection
        js = f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{text} by {src}");
            msg.lang = 'en-US'; // Default to English, or detect
            window.speechSynthesis.speak(msg);
        </script>
        <p>🔊 Playing audio...</p>
        """
        st.components.v1.html(js, height=50)

    st.subheader("Archive")
    for q in reversed(quotes[-10:]):
        st.text(f"{q['Quote']} -- {q['Source']}")
