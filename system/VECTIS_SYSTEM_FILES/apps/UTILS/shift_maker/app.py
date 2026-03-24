import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Shift Maker", page_icon="📅")
st.title("📅 Shift / Roster Maker")

members_txt = st.text_area("Members (one per line)", "Alice\nBob\nCharlie\nDave")
members = [m.strip() for m in members_txt.split('\n') if m.strip()]

days = st.number_input("Days to schedule", 7, 31, 7)
shifts_per_day = st.number_input("Staff per day", 1, 10, 2)

if st.button("Generate Roster"):
    data = []
    
    # Simple fair distribution logic (Round Robin)
    pool = members.copy()
    random.shuffle(pool)
    
    idx = 0
    for d in range(1, days + 1):
        daily_staff = []
        for _ in range(shifts_per_day):
            daily_staff.append(pool[idx % len(pool)])
            idx += 1
        
        data.append({
            "Day": f"Day {d}",
            "Staff": ", ".join(daily_staff)
        })
        
    df = pd.DataFrame(data)
    st.table(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "shift_roster.csv", "text/csv")
