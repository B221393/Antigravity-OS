import streamlit as st
import random
import string

st.set_page_config(page_title="Password Forge", page_icon="🔐")

st.title("🔐 Password Forge")
st.write("Generate strong, secure passwords instantly.")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Settings")
length = st.sidebar.slider("Length", min_value=8, max_value=64, value=16)

use_upper = st.sidebar.checkbox("A-Z Uppercase", value=True)
use_lower = st.sidebar.checkbox("a-z Lowercase", value=True)
use_digits = st.sidebar.checkbox("0-9 Digits", value=True)
use_symbols = st.sidebar.checkbox("!@#$ Symbols", value=True)

# --- LOGIC ---
def generate_password():
    chars = ""
    if use_upper: chars += string.ascii_uppercase
    if use_lower: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_symbols: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not chars:
        return "Error: Select at least one character type."
        
    return "".join(random.choice(chars) for _ in range(length))

# --- MAIN ---
if st.button("🔨 Forge Password", type="primary"):
    password = generate_password()
    st.session_state.password = password

if 'password' in st.session_state:
    st.markdown("### Generated Password:")
    st.code(st.session_state.password, language="text")
    st.write(f"Length: {len(st.session_state.password)} chars")

    # Strength Estimation (visual only)
    if len(st.session_state.password) < 12:
        st.warning("Strength: Weak (Too short)")
    elif len(st.session_state.password) < 16:
        st.info("Strength: Good")
    else:
        st.success("Strength: Excellent (Strong)")

st.divider()
st.markdown("""
**Security Note**: 
Passwords are generated locally on your machine. 
No data is sent to any server.
""")
