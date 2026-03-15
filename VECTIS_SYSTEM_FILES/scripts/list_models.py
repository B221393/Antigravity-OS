import os
import google.genai as genai
import sys

# Setup key (simplified)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "GEMINI_API_KEY" in line:
                    api_key = line.split("=")[1].strip().strip('"')

client = genai.Client(api_key=api_key)

try:
    with open("available_models.txt", "w") as f:
        for m in client.models.list():
            f.write(f"{m.name}\n")
    print("Saved to available_models.txt")
except Exception as e:
    print(f"Error: {e}")
