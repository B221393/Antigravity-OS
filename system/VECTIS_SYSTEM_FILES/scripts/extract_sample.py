
import os
import google.genai as genai
from google.genai import types
import sys

# Setup
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    # Try multiple .env locations
    possible_paths = [".env", "VECTIS_SYSTEM_FILES/.env"]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("GEMINI_API_KEY="):
                            api_key = line.strip().split("=", 1)[1].strip().strip('"')
                            break
            except: pass
            if api_key: break

if not api_key:
    print("No API Key")
    sys.exit(1)

client = genai.Client(api_key=api_key)

f = "IMG_2236.JPG"
if not os.path.exists(f):
    # Try finding any JPG
    import glob
    jpgs = glob.glob("IMG_*.JPG")
    if jpgs: f = jpgs[-1] # Try last one

print(f"Processing sample {f}...")

try:
    with open(f, "rb") as image_file:
        image_data = image_file.read()
        
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
            "この画像はマイナビのイベントで取ったノート、または関連資料です。書かれている文字を可能な限り正確に日本語で文字起こししてください。詳細に。"
        ]
    )
    
    print(response.text)
    
    with open("sample_note.md", "w", encoding="utf-8") as out:
        out.write(f"# Extracted Note Sample ({f})\n\n{response.text}\n")
        
except Exception as e:
    print(f"Error: {e}")
