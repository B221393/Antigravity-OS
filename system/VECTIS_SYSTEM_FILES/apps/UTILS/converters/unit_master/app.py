import streamlit as st

st.set_page_config(page_title="Unit Master", page_icon="📏")
st.title("📏 Unit Master")

cat = st.selectbox("Category", ["Length", "Area", "Weight", "Temp"])

if cat == "Length":
    val = st.number_input("Value")
    u_from = st.selectbox("From", ["meter", "inch", "feet", "shaku (尺)"])
    if st.button("Convert"):
        # to meter
        m = 0
        if u_from == "meter": m = val
        elif u_from == "inch": m = val * 0.0254
        elif u_from == "feet": m = val * 0.3048
        elif u_from == "shaku (尺)": m = val * 0.30303
        
        st.write(f"Meter: {m:.4f} m")
        st.write(f"Inch: {m/0.0254:.4f}")
        st.write(f"Feet: {m/0.3048:.4f}")

elif cat == "Area":
    val = st.number_input("Value")
    u_from = st.selectbox("From", ["sq_meter", "tsubo (坪)", "tatami (畳)"])
    if st.button("Convert"):
        sm = 0
        if u_from == "sq_meter": sm = val
        elif u_from == "tsubo (坪)": sm = val * 3.30578
        elif u_from == "tatami (畳)": sm = val * 1.62
        
        st.write(f"Sq Meter: {sm:.2f} m²")
        st.write(f"Tsubo: {sm/3.30578:.2f} 坪")
        st.write(f"Tatami: {sm/1.62:.2f} 畳")
        
# Add more logic as needed for speed
