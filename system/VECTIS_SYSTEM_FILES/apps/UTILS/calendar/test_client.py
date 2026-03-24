
import sys
import os

# Add the directory to sys.path to import the module
utils_path = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\UTILS\calendar"
sys.path.append(utils_path)

try:
    from google_calendar_client import GoogleCalendarClient
    print("Import successful")
    
    client = GoogleCalendarClient()
    print("Client initialized")
    
    # Try fetching events
    events = client.get_upcoming_events(max_results=5)
    print(f"Successfully fetched {len(events)} events")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"- {event['summary']} ({start})")

except Exception as e:
    print(f"Error: {e}")
