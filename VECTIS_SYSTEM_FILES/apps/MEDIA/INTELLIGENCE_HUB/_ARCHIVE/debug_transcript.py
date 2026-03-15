
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import sys
import traceback

# Pivot Video ID from previous log: qjQH4XH4PBQ (inferred from snapshot)
VID = "qjQH4XH4PBQ"

print(f"Target Video: {VID}")

try:
    print("Listing transcripts...")
    transcript_list = YouTubeTranscriptApi.list_transcripts(VID)
    
    print("Available transcripts:")
    for t in transcript_list:
        print(f" - {t.language_code} ({t.is_generated})")
        
    print("Fetching Japanese...")
    # Try fetching manual first, then generated
    try:
        t = transcript_list.find_manually_created_transcript(['ja'])
    except:
        try:
            t = transcript_list.find_generated_transcript(['ja'])
        except:
             t = transcript_list.find_generated_transcript(['en'])
             
    print(f"Selected: {t.language_code}")
    data = t.fetch()
    print("Fetch SUCCESS!")
    print(f"Length: {len(data)} items")
    print(f"First line: {data[0]['text']}")
    
except Exception as e:
    print("--- ERROR ---")
    print(type(e).__name__)
    print(e)
    traceback.print_exc()
