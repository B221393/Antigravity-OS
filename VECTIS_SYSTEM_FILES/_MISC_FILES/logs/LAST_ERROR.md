# 🚨 VECTIS System Error Report

**Application**: `YouTube_CLI`
**Timestamp**: `2026-01-12 21:04:46`
**Error Type**: `AttributeError`
**Message**: `type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'`
**Context**: get_transcript (API method failed) video_id=FE-hM1kRK4Y

## Stack Trace

```python
Traceback (most recent call last):
  File "C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\youtube_channel\run_cli.py", line 409, in get_transcript
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'

```
