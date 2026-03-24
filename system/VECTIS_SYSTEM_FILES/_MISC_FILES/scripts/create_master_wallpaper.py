from PIL import Image, ImageDraw, ImageFont
import os

# Ultra-Wide / 4K Design Parameters
width, height = 3840, 2160
bg_color = (15, 15, 20)  # Deep midnight blue
accent_color = (0, 255, 190)  # Cyan-green glow
text_color = (255, 255, 255)
sub_text_color = (150, 150, 160)

image = Image.new('RGB', (width, height), color=bg_color)
draw = ImageDraw.Draw(image)

# Define official o24 Layout (Verified from karabiner.json)
# Logical Layout:
# Q L U , .  F W R Y P
# E I A O -  K T N S H
# Z X C V ;  G D M J B
layout = [
    ["Q", "L", "U", ",", ".", "F", "W", "R", "Y", "P"],
    ["E", "I", "A", "O", "-", "K", "T", "N", "S", "H"],
    ["Z", "X", "C", "V", ";", "G", "D", "M", "J", "B"]
]

# Physical labels (QWERTY) to help learning
qwerty_labels = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
]

try:
    font_main = ImageFont.truetype("arialbd.ttf", 140)
    font_sub = ImageFont.truetype("arial.ttf", 40)
    font_title = ImageFont.truetype("arialbd.ttf", 80)
except:
    font_main = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_title = ImageFont.load_default()

# Background Micro-patterns (Cyberpunk style)
for i in range(0, width, 100):
    draw.line([i, 0, i, height], fill=(20, 25, 35), width=1)
for i in range(0, height, 100):
    draw.line([0, i, width, i], fill=(20, 25, 35), width=1)

# Title
draw.text((width//2, 200), "VECTIS TYPE: ONISHI o24", fill=accent_color, font=font_title, anchor="mm")
draw.text((width//2, 300), "Mastering the Japanese Optimized Layout", fill=sub_text_color, font=font_sub, anchor="mm")

# Key styling
key_w, key_h = 240, 240
margin = 40
start_x = (width - (10 * (key_w + margin))) // 2
start_y = 600

for row_idx, row in enumerate(layout):
    for col_idx, key in enumerate(row):
        # Calculate staggering like a real keyboard
        stagger = 0
        if row_idx == 1: stagger = 40
        if row_idx == 2: stagger = 100
        
        x = start_x + col_idx * (key_w + margin) + stagger
        y = start_y + row_idx * (key_h + margin)
        
        # Glow Effect
        draw.rectangle([x-5, y-5, x+key_w+5, y+key_h+5], outline=accent_color, width=2)
        draw.rectangle([x, y, x+key_w, y+key_h], fill=(30, 35, 45), outline=(100, 100, 120), width=3)
        
        # Main Character
        draw.text((x + key_w//2, y + key_h//2 - 20), key, fill=text_color, font=font_main, anchor="mm")
        
        # Physical QWERTY hint
        hint = f"({qwerty_labels[row_idx][col_idx]})"
        draw.text((x + key_w//2, y + key_h - 40), hint, fill=sub_text_color, font=font_sub, anchor="mm")

# Footer Information
footer_text = "Toggle: [Ctrl + Alt + S] | Vectis OS Integration"
draw.text((width//2, height - 200), footer_text, fill=accent_color, font=font_sub, anchor="mm")

# Save and Apply
output_path = r"c:\Users\Yuto\Downloads\app\outputs\assets\onishi_master.png"
if not os.path.exists(os.path.dirname(output_path)): os.makedirs(os.path.dirname(output_path))
image.save(output_path)
print(f"Master Wallpaper saved: {output_path}")
