import streamlit as st

st.set_page_config(page_title="Base Master", page_icon="🔢")
st.title("🔢 Base Master (Radix Converter)")

mode = st.radio("Input Format", ["Decimal (10)", "Hexadecimal (16)", "Binary (2)", "Octal (8)"])
user_input = st.text_input("Enter Number")

try:
    val = 0
    if not user_input:
        st.stop()
        
    if mode.startswith("Decimal"):
        val = int(user_input)
    elif mode.startswith("Hex"):
        val = int(user_input, 16)
    elif mode.startswith("Binary"):
        val = int(user_input, 2)
    elif mode.startswith("Octal"):
        val = int(user_input, 8)
    
    st.divider()
    st.markdown("### Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DEC (10)", f"{val}")
    c2.metric("HEX (16)", f"{val:X}")
    c3.metric("BIN (2)", f"{val:b}")
    c4.metric("OCT (8)", f"{val:o}")
    
except ValueError:
    st.error("Invalid input for selected base.")
