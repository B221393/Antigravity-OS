
import os
import glob
import google.genai as genai
from google.genai import types
import sys
import time
import re
from datetime import datetime

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
    # Scan for already processed files AND remove failed entries
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        for filename in all_files:
            # Only count as processed if it has actual content (not error/failed)
            if f"## File: {filename}" in content:
                # Check if it's a failure
                file_section_start = content.find(f"## File: {filename}")
                file_section_end = content.find("---", file_section_start)
                if file_section_end != -1:
                    section = content[file_section_start:file_section_end]
                    if "(Failed after retries)" not in section and "(Error extracting" not in section:
                        processed_files.add(filename)
    
    # Clear the file and rewrite header (to remove failed entries)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Mynavi Event Notes (Extracted)\n\n")
        # Re-write successfully processed entries
        content_lines = content.split("## File:")
        for section in content_lines[1:]:  # Skip header
            if section.strip():
                filename_line = section.split("\n")[0].strip()
                if filename_line in [os.path.basename(f) for f in processed_files]:
                    f.write("## File:" + section)
    
    print(f"Resuming... {len(processed_files)} already processed successfully.")

print(f"Found {len(all_files)} images, {len(all_files) - len(processed_files)} remaining.")
print("\n" + "="*60)
print("IMPORTANT: Gemini API has strict rate limits.")
print("Free tier: ~15 requests/minute, ~1000 requests/day")
print("We'll use conservative delays to avoid hitting limits.")
print("="*60 + "\n")

# More conservative approach
BASE_DELAY = 30  # Increased from 15s to 30s between successful requests
RETRY_429_DELAY = 90  # 90 seconds when hitting rate limit

for idx, f in enumerate(all_files):
    if f in processed_files:
        continue
        
    print(f"\n[{idx+1}/{len(all_files)}] Processing {f}...")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    success = False
    retry_count = 0
    max_retries = 5  # Reduced from 20 - fail faster
    
    entry_text = ""
    
    while not success and retry_count < max_retries:
        try:
            with open(f, "rb") as image_file:
                image_data = image_file.read()
            
            # Show file size for debugging
            file_size_mb = len(image_data) / (1024 * 1024)
            print(f"  File size: {file_size_mb:.2f} MB")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",  # Changed to experimental model (may have better quota)
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg" if f.endswith(".JPG") else "image/png"),
                    "この画像はマイナビのイベントで取ったノート、または関連資料です。書かれている文字を可能な限り正確に日本語で文字起こししてください。手書きの場合は文脈を補って読み取ってください。また、内容の要約も合わせてお願いします。"
                ]
            )
            
            extracted = response.text
            entry_text = f"## File: {f}\n\n{extracted}\n\n---\n\n"
            success = True
            print(f"  ✓ Success! Extracted {len(extracted)} characters")
            
            # Conservative delay after success
            print(f"  Waiting {BASE_DELAY}s before next request...")
            time.sleep(BASE_DELAY)
            
        except Exception as e:
            error_str = str(e)
            retry_count += 1
            
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                print(f"  ⚠ Rate limit hit! (Attempt {retry_count}/{max_retries})")
                print(f"  Error: {error_str[:200]}")
                
                # Extract suggested wait time or use default
                wait_time = RETRY_429_DELAY
                match = re.search(r"retry in (\d+(\.\d+)?)s", error_str)
                if match:
                    wait_time = float(match.group(1)) + 20  # Add buffer
                
                print(f"  Waiting {wait_time:.0f}s to clear rate limit...")
                time.sleep(wait_time)
                
            else:
                print(f"  ✗ Error: {e}")
                if retry_count >= max_retries:
                    entry_text = f"## File: {f}\n\n(Error after {max_retries} retries: {str(e)[:100]})\n\n---\n\n"
                else:
                    print(f"  Retrying in 10s... ({retry_count}/{max_retries})")
                    time.sleep(10)
    
    if not success:
        if retry_count >= max_retries:
            entry_text = f"## File: {f}\n\n(Failed after {max_retries} retries - likely quota exhausted)\n\n---\n\n"
            print(f"  ✗ Failed after {max_retries} attempts")
            print("\n" + "!"*60)
            print("API QUOTA MAY BE EXHAUSTED!")
            print("Consider waiting 24 hours or using a different API key.")
            print("!"*60)
            # Ask user whether to continue
            print("\nContinuing with remaining files...")

    # Append to file immediately
    with open(output_file, "a", encoding="utf-8") as out:
        out.write(entry_text)

print("\n" + "="*60)
print("Done! Saved to extracted_notes_draft.md")
print("="*60)
