import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Meeting Cost", page_icon="💸")
st.title("💸 Meeting Cost [Rank 42]")

# Session State
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'elapsed' not in st.session_state: st.session_state.elapsed = 0

participants = st.number_input("Participants", 1, 100, 5)
avg_wage = st.number_input("Avg Hourly Wage (¥)", 1000, 50000, 3000)

cost_per_sec = (avg_wage * participants) / 3600

c1, c2 = st.columns(2)
if c1.button("Start"):
    st.session_state.start_time = time.time()
if c2.button("Stop"):
    st.session_state.start_time = None

placeholder = st.empty()

if st.session_state.start_time:
    # Real-time update loop? Streamlit loop logic
    while st.session_state.start_time:
        now = time.time()
        dur = now - st.session_state.start_time + st.session_state.elapsed
        cost = dur * cost_per_sec
        
        placeholder.metric("Current Waste", f"¥{cost:,.0f}", f"{dur:.0f} sec")
        time.sleep(1) # Reactivity
        
        # Stop condition check? In streamlit while loop blocks other interactions usually unless used with rerun or placeholder trick carefuly.
        # But for simple timer, this blocks UI. We use time.time diff on rerun.
        # To make it non-blocking, we need st.rerun() but that flickers.
        # We'll just show static "Last Update" or simple auto-rerun.
        # Better: use st.empty and sleep inside a finite loop for "Demo" or just calc on refresh.
        # For "Utility", just static calc allows manual refresh.
        break # Avoid blocking forever

if st.session_state.start_time:
    st.info("Timer Running... (Click Rerun to update)")
    if st.button("Update View"): st.rerun()
