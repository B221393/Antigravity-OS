
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env from EGO root
EGO_ROOT = Path(r"C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES")
load_dotenv(EGO_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print("Listing models (Legacy SDK)...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
    print("\nTesting Generation with gemini-1.5-flash...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    resp = model.generate_content("Hello")
    print(f"Response: {resp.text}")

except Exception as e:
    print(f"Legacy SDK Error: {e}")
