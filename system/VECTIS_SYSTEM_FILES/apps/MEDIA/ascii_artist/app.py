import streamlit as st
from PIL import Image
import numpy as np

st.set_page_config(page_title="ASCII Artist", page_icon="🎨")
st.title("🎨 ASCII Artist")

ascii_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width / 1.65
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ascii_chars[pixel//25] for pixel in pixels])
    return characters

def generate_ascii(image, new_width=100):
    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width)))
    
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])
    return ascii_image

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original", width=300)
    
    width = st.slider("Width (Complexity)", 50, 200, 100)
    
    if st.button("Convert"):
        ascii_art = generate_ascii(image, width)
        st.code(ascii_art, language="text")
