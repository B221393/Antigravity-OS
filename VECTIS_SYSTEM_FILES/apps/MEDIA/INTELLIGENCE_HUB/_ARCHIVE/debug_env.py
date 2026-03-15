
import sys
import os
try:
    import youtube_transcript_api
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("ImportError!")
    sys.exit(1)

print(f"Python: {sys.executable}")
print(f"Library File: {youtube_transcript_api.__file__}")
print(f"Version (if avail): {getattr(youtube_transcript_api, '__version__', 'N/A')}")
print(f"Available attributes: {dir(YouTubeTranscriptApi)}")

# Check for shadowing
print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
    print("list_transcripts EXISTS")
else:
    print("list_transcripts MISSING")
