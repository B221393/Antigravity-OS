import os
from google import genai
from dotenv import load_dotenv

# Load env from root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("No API Key found in .env at " + ROOT_DIR)
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
try:
    # Note: the new SDK might have a different way to list models
    # Based on the error in the logs, it seems to use the v1beta API by default
    models = client.models.list()
    for m in models:
        print(f"Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
