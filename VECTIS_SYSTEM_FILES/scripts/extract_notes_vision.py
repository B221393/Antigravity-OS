
import os
import glob
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
            print(f"Found .env at {p}")
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("GEMINI_API_KEY="):
                            api_key = line.strip().split("=", 1)[1].strip().strip('"')
                            break
            except Exception as e:
                print(f"Error reading {p}: {e}")
            if api_key: break
        else:
            print(f"No .env at {p}")

if not api_key:
    # Last ditch: Try importing unified_llm_client config if in path
    try:
        sys.path.append(os.path.join(os.getcwd(), "VECTIS_SYSTEM_FILES", "modules"))
        from unified_llm_client import GEMINI_API_KEY
        if GEMINI_API_KEY: 
            api_key = GEMINI_API_KEY
            print("Loaded key from unified_llm_client")
    except Exception as e:
        print(f"Failed to load from module: {e}")

if not api_key:
    print("FATAL: No API Key found in env or .env files.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

import time
import re

# Files to process
all_files = glob.glob("IMG_*.JPG") + glob.glob("IMG_*.PNG")
all_files.sort()

output_file = "extracted_notes_draft.md"
processed_files = set()

# Initialize or load existing
if not os.path.exists(output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Mynavi Event Notes (Extracted)\n\n")
else:
    # Scan for already processed files
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        for filename in all_files:
            if f"## File: {filename}" in content:
                processed_files.add(filename)
    print(f"Resuming... {len(processed_files)} already processed.")

print(f"Found {len(all_files)} images, {len(all_files) - len(processed_files)} remaining.")

for f in all_files:
    if f in processed_files:
        continue
        
    print(f"Processing {f}...")
    success = False
    retry_count = 0
    max_retries = 20 # Increased retries
    
    entry_text = ""
    
    while not success and retry_count < max_retries:
        try:
            with open(f, "rb") as image_file:
                image_data = image_file.read()
            
            # Use specific available model from list
            selected_model = "models/gemini-2.5-flash"

            response = client.models.generate_content(
                model=selected_model,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg" if f.lower().endswith(".jpg") else "image/png"),
                    "この画像はマイナビのイベントで取ったノート、または関連資料です。書かれている文字を可能な限り正確に日本語で文字起こししてください。手書きの場合は文脈を補って読み取ってください。また、内容の要約も合わせてお願いします。"
                ]
            )
            
            extracted = response.text
            entry_text = f"## File: {f}\n\n{extracted}\n\n---\n\n"
            success = True
            print(f"Success processing {f}")
            time.sleep(15) # Increased politeness delay
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                # Do not increment retry_count for simple rate limits to keep trying indefinitely if needed
                # Or just increment it slowly. Let's effectively retry forever on 429s by not counting them strictly or high limit.
                # Actually, simply waiting longer is key.
                retry_count += 0.5 # Count 429s as "half" a failure to be patient
                
                wait_time = 70 # Wait over a minute to clear the sliding window
                match = re.search(r"retry in (\d+(\.\d+)?)s", error_str)
                if match:
                    wait_time = float(match.group(1)) + 10
                
                print(f"Rate limited on {f}. Retrying in {wait_time:.1f}s... (Standing by...)")
                time.sleep(wait_time)
            else:
                retry_count += 1
                print(f"Error processing {f}: {e}")
                if retry_count >= max_retries:
                    entry_text = f"## File: {f}\n\n(Error extracting text: {e})\n\n---\n\n"
    
    if not success and retry_count >= max_retries:
         entry_text = f"## File: {f}\n\n(Failed after retries)\n\n---\n\n"

    # Append to file immediately
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(entry_text)

print("Done! Saved to extracted_notes_draft.md")
