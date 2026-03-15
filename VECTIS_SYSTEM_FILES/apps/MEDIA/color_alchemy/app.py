import streamlit as st
import colorsys

st.set_page_config(page_title="Color Alchemy", page_icon="🎨", layout="wide")

st.title("🎨 Color Alchemy")
st.write("Generate harmonious color schemes from a single base color.")

# --- UTILS ---
def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def hue_shift(hex_code, degree):
    r, g, b = hex_to_rgb(hex_code)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    
    h = (h + degree/360.0) % 1.0
    
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r*255, g*255, b*255))

# --- SIDEBAR ---
base_color = st.sidebar.color_picker("Pick a Base Color", "#00A8E8")

# --- GENERATION ---
schemes = {
    "Complementary (補色)": [0, 180],
    "Analogous (類似色)": [0, -30, 30],
    "Triadic (トライアド)": [0, 120, 240],
    "Split Complementary (分裂補色)": [0, 150, 210],
    "Square (スクエア)": [0, 90, 180, 270]
}

# --- DISPLAY ---
st.subheader("🧪 Transmuted Palettes")

for name, shifts in schemes.items():
    st.markdown(f"#### {name}")
    cols = st.columns(len(shifts))
    
    for idx, shift in enumerate(shifts):
        color = hue_shift(base_color, shift)
        
        # Text color based on brightness
        r, g, b = hex_to_rgb(color)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        text_color = "black" if brightness > 125 else "white"
        
        with cols[idx]:
            st.markdown(f"""
            <div style="background-color: {color}; height: 100px; border-radius: 10px; display: flex; align_items: center; justify_content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <span style="color: {text_color}; font-weight: bold; font-family: monospace;">{color.upper()}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

st.sidebar.markdown("### Export")
if st.sidebar.button("Copy CSS Variables"):
    css = ":root {\n"
    for name, shifts in schemes.items():
        for i, shift in enumerate(shifts):
            c = hue_shift(base_color, shift)
            safe_name = name.split()[0].lower()
            css += f"  --color-{safe_name}-{i+1}: {c};\n"
    css += "}"
    st.sidebar.code(css, language="css")
