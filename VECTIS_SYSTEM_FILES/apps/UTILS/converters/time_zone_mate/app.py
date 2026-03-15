import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Time Zone Mate", page_icon="🌐")
st.title("🌐 Time Zone Mate")

zones = st.multiselect("Select Time Zones", pytz.all_timezones, default=["Asia/Tokyo", "America/New_York", "Europe/London"])

base_date = st.date_input("Date", datetime.now())
base_hour = st.slider("Base Time (Hour in 1st Zone)", 0, 23, 9)

if zones:
    base_tz = pytz.timezone(zones[0])
    # Create timezone aware datetime
    dt = datetime.combine(base_date, datetime.min.time())
    dt = dt.replace(hour=base_hour)
    local_dt = base_tz.localize(dt)
    
    st.divider()
    
    for z in zones:
        tz = pytz.timezone(z)
        target_dt = local_dt.astimezone(tz)
        
        fmt_time = target_dt.strftime("%H:%M")
        fmt_date = target_dt.strftime("%Y-%m-%d")
        
        # Color coding for business hours (9-18)
        hour = target_dt.hour
        color = "#00FF00" if 9 <= hour < 18 else "#555"
        
        st.markdown(f"""
        <div style="padding:10px; border:1px solid #333; margin-bottom:5px; border-left: 5px solid {color}">
            <h3 style="margin:0">{z}</h3>
            <span style="font-size:2em">{fmt_time}</span> <span style="color:#888">{fmt_date}</span>
        </div>
        """, unsafe_allow_html=True)
