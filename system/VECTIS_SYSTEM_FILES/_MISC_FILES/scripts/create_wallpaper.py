from PIL import Image, ImageDraw, ImageFont
import os

# Create a dark background image (4K)
width, height = 3840, 2160
image = Image.new('RGB', (width, height), color=(20, 20, 25))
draw = ImageDraw.Draw(image)

# Define the layout
layout = [
    ["Q", "L", "D", "C", "V", "J", "F", "U", "O", ","],
    ["A", "N", "I", "T", "G", "K", "Y", "E", "S", "R"],
    ["Z", "X", "M", "W", "P", "V", "H", ".", ";", "-"]
]

# Set up fonts (assuming standard Windows fonts)
try:
    font_large = ImageFont.truetype("arialbd.ttf", 120)
    font_small = ImageFont.truetype("arial.ttf", 40)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Title
draw.text((width//2, 300), "Onishi Layout (o24)", fill=(200, 200, 200), font=font_large, anchor="mm")

# Draw the keys
start_x = 600
start_y = 800
key_w = 250
key_h = 250
margin = 50

for row_idx, row in enumerate(layout):
    for col_idx, key in enumerate(row):
        x = start_x + col_idx * (key_w + margin)
        y = start_y + row_idx * (key_h + margin)
        
        # Center the keys slightly for the middle and bottom rows (standard staggered)
        if row_idx == 1: x += 50
        if row_idx == 2: x += 100
        
        # Draw key box
        draw.rectangle([x, y, x+key_w, y+key_h], outline=(100, 100, 120), width=3)
        # Draw key text
        draw.text((x + key_w//2, y + key_h//2), key, fill=(255, 255, 255), font=font_large, anchor="mm")

# Save the image
output_path = r"c:\Users\Yuto\Downloads\app\onishi_wallpaper.png"
image.save(output_path)
print(f"Wallpaper saved to: {output_path}")
