import streamlit as st
import random

st.set_page_config(page_title="World Capitals", page_icon="🌍")
st.title("🌍 World Capital Quiz")

DATA = {
    "Japan": "Tokyo",
    "USA": "Washington D.C.",
    "UK": "London",
    "France": "Paris",
    "Germany": "Berlin",
    "China": "Beijing",
    "India": "New Delhi",
    "Brazil": "Brasilia",
    "Canada": "Ottawa",
    "Australia": "Canberra",
    "Italy": "Rome",
    "Spain": "Madrid",
    "Russia": "Moscow",
    "South Korea": "Seoul",
    "Egypt": "Cairo",
    "Thailand": "Bangkok",
    "Vietnam": "Hanoi",
    "Turkey": "Ankara"
}

if 'q_country' not in st.session_state:
    st.session_state.q_country = random.choice(list(DATA.keys()))
    st.session_state.score = 0
    st.session_state.total = 0

st.write(f"### Score: {st.session_state.score} / {st.session_state.total}")
st.header(f"Question: Capital of {st.session_state.q_country}?")

ans = st.text_input("Your Answer")

if st.button("Submit"):
    correct = DATA[st.session_state.q_country]
    if ans.lower().strip() == correct.lower():
        st.success(f"Correct! It is {correct}.")
        st.session_state.score += 1
    else:
        st.error(f"Wrong. It is {correct}.")
    
    st.session_state.total += 1
    st.session_state.q_country = random.choice(list(DATA.keys()))
    if st.button("Next"): st.rerun()
