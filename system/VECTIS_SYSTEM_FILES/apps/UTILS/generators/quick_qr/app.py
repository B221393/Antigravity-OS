import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Quick QR", page_icon="📱")
st.title("📱 Quick QR Generator")

data = st.text_input("Enter URL or Text", "https://www.example.com")
fill_color = st.color_picker("Fill Color", "#000000")
back_color = st.color_picker("Background Color", "#FFFFFF")

if st.button("Generate QR"):
    if data:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Convert to bytes for download
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.image(byte_im, caption="Generated QR Code")
        
        st.download_button(
            label="Download PNG",
            data=byte_im,
            file_name="qrcode.png",
            mime="image/png"
        )
    else:
        st.warning("Please enter some text.")
