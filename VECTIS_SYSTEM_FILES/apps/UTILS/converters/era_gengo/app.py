import streamlit as st
import datetime

st.set_page_config(page_title="Gengo Conv", page_icon="📅")
st.title("📅 元号西暦変換表 (Era Converter)")

eras = {
    "Reiwa (令和)": 2018,
    "Heisei (平成)": 1988,
    "Showa (昭和)": 1925,
    "Taisho (大正)": 1911,
    "Meiji (明治)": 1867
}

mode = st.radio("Mode", ["西暦 -> 元号", "元号 -> 西暦"])

if mode == "西暦 -> 元号":
    y = st.number_input("Year (AD)", 1900, 2100, 2026)
    found = False
    for era, start in eras.items():
        if y > start:
            ey = y - start
            st.success(f"{y} is {era.split(' ')[1]} {ey} 年 ({era})")
            found = True
            break
    if not found: st.error("Too old")
else:
    e_name = st.selectbox("Era", list(eras.keys()))
    e_year = st.number_input("Year", 1, 100, 1)
    
    ad = eras[e_name] + e_year
    st.success(f"{e_name.split(' ')[1]} {e_year} is {ad} (AD)")
    
    today = datetime.date.today().year
    age = today - ad
    st.info(f"Age (in {today}): {age} years old")
