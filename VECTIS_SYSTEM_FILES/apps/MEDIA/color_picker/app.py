import streamlit as st

st.set_page_config(page_title="Color Picker", page_icon="🎨")
st.title("🎨 Color Picker (色彩採取)")

c = st.color_picker("Pick", "#00A8E8")
st.code(c)

# RGB
c = c.lstrip('#')
rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
st.write(f"RGB: {rgb}")
st.write(f"CSS: `rgb{rgb}`")
