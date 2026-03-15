import os
import google.genai as genai
from google.genai import types
import sys

# Try to look for .env
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    possible_paths = [".env", "VECTIS_SYSTEM_FILES/.env"]
    for p in possible_paths:
        if os.path.exists(p):
            print(f"Found .env at {p}")
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip().strip('"')
                        print(f"Loaded key ending in ...{api_key[-4:] if api_key else 'None'}")
                        break
        if api_key: break

if not api_key:
    # Try importing unified_llm_client config if in path
    try:
        sys.path.append(os.path.join(os.getcwd(), "VECTIS_SYSTEM_FILES", "modules"))
        from unified_llm_client import GEMINI_API_KEY
        if GEMINI_API_KEY: 
            api_key = GEMINI_API_KEY
            print(f"Loaded key from unified_llm_client ending in ...{api_key[-4:] if api_key else 'None'}")
    except Exception as e:
        print(f"Failed to load from module: {e}")

if not api_key:
    print("FATAL: No API Key found.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Test File
test_file = "IMG_2218.JPG" # Pick one that exists
if not os.path.exists(test_file):
    # Fallback to any IMG file
    import glob
    files = glob.glob("IMG_*.JPG") + glob.glob("IMG_*.PNG")
    if files:
        test_file = files[0]
    else:
        print("No IMG files found to test.")
        sys.exit(1)

print(f"Testing with file: {test_file}")

try:
    with open(test_file, "rb") as image_file:
        image_data = image_file.read()
    
    print("Listing models...")
    for m in client.models.list():
        print(f"Found model: {m.name}")
        if "flash" in m.name or "pro" in m.name:
            print(f" - Candidate: {m.name}")

    # Fallback to test if we found one
    # But for now just exit to see output
    import sys
    sys.exit(0)

    print("Sending request to Gemini...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/jpeg" if test_file.lower().endswith(".jpg") else "image/png"),
            "Test extraction. Describe this image briefly."
        ]
    )
    print("Success!")
    print(response.text[:100] + "...")
except Exception as e:
    print("FAILED with Exception!")
    print(f"Type: {type(e)}")
    print(f"Error: {e}")
    # Print detailed attributes if available
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
