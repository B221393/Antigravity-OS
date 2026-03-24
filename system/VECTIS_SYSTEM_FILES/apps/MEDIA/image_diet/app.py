import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Image Diet", page_icon="📉")
st.title("📉 Image Diet (Compressor)")

files = st.file_uploader("Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
quality = st.slider("Compression Quality (1-95)", 10, 95, 60)
max_width = st.number_input("Max Width (px, 0=No Resize)", 0, 4000, 1080)

if files:
    for f in files:
        img = Image.open(f)
        
        # Resize
        if max_width > 0 and img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Compress
        out = BytesIO()
        fmt = f.name.split('.')[-1].upper()
        if fmt == 'JPG': fmt = 'JPEG'
        
        try:
            img.save(out, format=fmt, quality=quality, optimize=True)
            size_kb = out.tell() / 1024
            
            st.write(f"**{f.name}** -> {size_kb:.1f} KB")
            st.download_button(f"Download {f.name}", out.getvalue(), f.name)
        except:
            # Fallback for PNG which doesn't support 'quality' param same way
            img.save(out, format=fmt, optimize=True)
            st.download_button(f"Download {f.name}", out.getvalue(), f.name)
