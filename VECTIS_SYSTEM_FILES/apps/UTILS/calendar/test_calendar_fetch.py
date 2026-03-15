import sys
import os
# Add the current directory to sys.path so we can import the client
sys.path.append(os.getcwd())

from google_calendar_client import GoogleCalendarClient

print("--- START TEST ---")
try:
    client = GoogleCalendarClient()
    print("Attempting authentication...")
    client.authenticate()
    print("Authentication successful.")
    
    print("Fetching events...")
    events = client.get_upcoming_events(max_results=5)
    print(f"Events found: {len(events)}")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"- {start}: {event['summary']}")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("--- END TEST ---")
