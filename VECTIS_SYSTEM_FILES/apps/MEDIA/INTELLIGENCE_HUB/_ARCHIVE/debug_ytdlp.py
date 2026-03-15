
import yt_dlp
import os
import glob

VID = "qjQH4XH4PBQ"
URL = f"https://www.youtube.com/watch?v={VID}"

print(f"Testing yt-dlp for {VID}...")

# Clean up old
for f in glob.glob(f"temp_{VID}*"):
    os.remove(f)

ydl_opts = {
    'skip_download': True,
    'writeautomaticsub': True,
    'writesubtitles': True,
    'subtitleslangs': ['ja', 'en'],
    'outtmpl': f'temp_{VID}',
    'quiet': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])
        
    # Check for files
    files = glob.glob(f"temp_{VID}*")
    print(f"Files found: {files}")
    
    # Read first vtt
    vtt_file = None
    for f in files:
        if f.endswith('.vtt'):
            vtt_file = f
            break
            
    if vtt_file:
        print(f"Reading {vtt_file}...")
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("--- VTT START ---")
            print(content[:200])
            print("--- VTT END ---")
            
        # Basic VTT to Text
        lines = content.splitlines()
        text_lines = []
        for line in lines:
            if '-->' in line: continue
            if line.strip() == '': continue
            if line.startswith('WEBVTT'): continue
            if line.strip().isdigit(): continue # sequences
            # Remove tags like <c.colorCCCCCC> etc
            # Simple regex
            import re
            text = re.sub(r'<[^>]+>', '', line)
            # Duplicate check (VTT often repeats lines for karaoke effect)
            if text_lines and text_lines[-1] == text:
                continue
            text_lines.append(text)
            
        full_text = " ".join(text_lines)
        print("\n--- EXTRACTED TEXT ---")
        print(full_text[:300])
    else:
        print("No VTT file generated.")

except Exception as e:
    print(f"Error: {e}")
