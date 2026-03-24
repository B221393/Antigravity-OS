
import os
import sys

# Add path to find google_calendar_client
sys.path.append(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\UTILS\calendar")

try:
    from google_calendar_client import GoogleCalendarClient
    print("Imported GoogleCalendarClient")
except ImportError:
    print("Failed to import GoogleCalendarClient")
    sys.exit(1)

def debug_calendars():
    try:
        client = GoogleCalendarClient()
        # Explicitly authenticate to initialize service
        client.authenticate()
        service = client.service
        
        # 1. List all calendars
        print("\n--- Listing Calendars ---")
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                print(f"ID: {calendar_list_entry['id']}, Summary: {calendar_list_entry['summary']}")
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        # 2. List events from 'primary'
        print("\n--- Events in Primary Calendar (Next 10) ---")
        events = client.get_upcoming_events(max_results=10)
        if not events:
            print("No upcoming events found in primary calendar.")
        for event in events:
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
            print(f"{start} - {event.get('summary', 'No Title')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_calendars()
