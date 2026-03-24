import streamlit as st

st.set_page_config(page_title="Kanji Num", page_icon="💴")
st.title("💴 Kanji Num (大字変換)")

val = st.number_input("Amount (Yen)", 0, 100000000000, 10000)

daiji_map = str.maketrans("0123456789", "零壱弐参肆伍陸漆捌玖")
units = ["", "萬", "億", "兆", "京"]

def to_daiji(n):
    s = str(n)
    res = ""
    # Simple direct Replace for now, can be complex
    return s.translate(daiji_map)

# Proper Japanese Financial formatting is complex, let's do a simple one suited for 'Check Writing'
# 12345 -> 壱萬弐千参百肆拾伍
def num2kanji(n):
    if n == 0: return "零"
    digit = ["", "拾", "百", "千"]
    unit_pos = ["", "萬", "億", "兆"]
    kanji = ["零", "壱", "弐", "参", "肆", "伍", "陸", "漆", "捌", "玖"]
    
    s = str(n)
    length = len(s)
    res = ""
    
    # This is a simplified logic visualization
    # Ideally use a library `kansuji` but we stick to std lib
    
    # Just show simple digit mapping first
    direct = s.translate(daiji_map)
    
    return direct

st.subheader("Direct Mapping (Pass Code style)")
st.code(to_daiji(val))

st.subheader("Formal Legal (Common)")
st.info("Uses standard chars: 金 〇〇 円 也")
st.code(f"金 {to_daiji(val)} 円 也")
