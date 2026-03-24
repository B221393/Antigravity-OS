import os
import sys
import json
import uuid
import datetime

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.abspath(os.path.join(current_dir, "../../UTILS/calendar"))
sys.path.append(utils_dir)

try:
    from google_calendar_client import GoogleCalendarClient
except ImportError:
    print("Cannot import GoogleCalendarClient")
    sys.exit(1)

# Paths
events_json = os.path.join(utils_dir, "events.json")
# OS export script
sys.path.append(os.path.join(current_dir, "."))
from export_calendar_for_os import export_calendar

def force_sync():
    print("🔄 Starting Force Sync...")
    
    # 1. Fetch from Google
    try:
        client = GoogleCalendarClient(
            credentials_path=os.path.join(utils_dir, "credentials.json"),
            token_path=os.path.join(utils_dir, "token.pickle")
        )
        g_events = client.get_upcoming_events(max_results=20)
        print(f"📥 Fetched {len(g_events)} events from Google Calendar")
    except Exception as e:
        print(f"❌ Google Sync Failed: {e}")
        return

    # 2. Update events.json
    local_events = []
    if os.path.exists(events_json):
        try:
            with open(events_json, 'r', encoding='utf-8') as f:
                local_events = json.load(f)
        except:
            local_events = []
            
    existing_keys = set()
    for e in local_events:
        key = f"{e['date']}_{e['title']}"
        existing_keys.add(key)
        
    added_count = 0
    for ge in g_events:
        start = ge['start'].get('dateTime', ge['start'].get('date'))
        title = ge.get('summary', 'No Title')
        
        # Parse date
        date_str = start[:10] # YYYY-MM-DD
        time_str = ""
        if 'T' in start:
            time_str = start[11:16] # HH:MM
        
        key = f"{date_str}_{title}"
        
        if key not in existing_keys:
            new_event = {
                "id": str(uuid.uuid4()),
                "title": title,
                "date": date_str,
                "time": time_str,
                "category": "☁️ Google", 
                "memo": ge.get('description', '') + f"\n(Location: {ge.get('location', '')})",
                "created": datetime.datetime.now().isoformat(),
                "source": "google_calendar",
                "gcal_id": ge['id']
            }
            local_events.append(new_event)
            existing_keys.add(key)
            added_count += 1
            
    if added_count > 0 or len(local_events) > 0:
        with open(events_json, 'w', encoding='utf-8') as f:
            json.dump(local_events, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(local_events)} events to events.json (+{added_count} new)")
    
    # 3. Export to OS
    print("📤 Exporting to OS Desktop...")
    export_calendar()
    print("✅ Force Sync Complete!")

if __name__ == "__main__":
    force_sync()
