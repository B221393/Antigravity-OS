import json
import os
import sys
from datetime import datetime

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
apps_root = os.path.abspath(os.path.join(current_dir, "../.."))
calendar_json = os.path.join(apps_root, "UTILS", "calendar", "events.json")

# Import Google Calendar Client
calendar_utils_path = os.path.join(apps_root, "UTILS", "calendar")
if calendar_utils_path not in sys.path:
    sys.path.append(calendar_utils_path)

try:
    from google_calendar_client import GoogleCalendarClient
except ImportError:
    GoogleCalendarClient = None
    print("Warning: Could not import GoogleCalendarClient")

# OS Data Dir
os_root = os.path.abspath(os.path.join(current_dir, "../../../OS"))
os_data_dir = os.path.join(os_root, "data")
output_js = os.path.join(os_data_dir, "calendar_data.js")

os.makedirs(os_data_dir, exist_ok=True)

def export_calendar():
    """Export events.json AND Google Calendar events to calendar_data.js"""
    
    # 1. Load Local Events
    if not os.path.exists(calendar_json):
        print(f"No events file found at {calendar_json}")
        local_events = []
    else:
        try:
            with open(calendar_json, "r", encoding="utf-8") as f:
                local_events = json.load(f)
        except Exception as e:
            print(f"Error reading local events: {e}")
            local_events = []

    # 2. Fetch Google Calendar Events
    gcal_events = []
    if GoogleCalendarClient:
        try:
            print("Fetching Google Calendar events...")
            client = GoogleCalendarClient()
            # Fetch for next 30 days roughly
            api_events = client.get_upcoming_events(max_results=20)
            
            for ev in api_events:
                # Parse GCal event to VECTIS format
                start = ev.get('start', {})
                dt_str = start.get('dateTime', start.get('date')) # 2023-10-27T10:00:00+09:00 or 2023-10-27
                
                # Simple parsing logic
                is_all_day = 'T' not in dt_str
                date_part = dt_str.split('T')[0]
                time_part = dt_str.split('T')[1][:5] if not is_all_day else ""
                
                # Category logic (simple keyword based)
                summary = ev.get('summary', 'No Title')
                category = "📅 予定"
                if "ミーティング" in summary or "会議" in summary: category = "💼 仕事"
                elif "誕生日" in summary: category = "🎂 記念日"
                
                gcal_events.append({
                    "id": ev.get('id'),
                    "title": summary,
                    "date": date_part,
                    "time": time_part,
                    "category": category,
                    "memo": ev.get('description', ''),
                    "source": "google"
                })
            print(f"Fetched {len(gcal_events)} events from Google Calendar")
            
        except Exception as e:
            print(f"Failed to fetch Google Calendar events: {e}")

    # 3. Merge Events (Combine lists)
    # We could implement deduping here if needed, but for now just concat
    all_events = local_events + gcal_events

    # 4. Filter for upcoming
    now = datetime.now()
    upcoming = []
    
    for e in all_events:
        try:
            e_date_str = e.get("date")
            e_time_str = e.get("time", "")
            
            if e_time_str:
                dt_str = f"{e_date_str} {e_time_str}"
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            else:
                dt_str = f"{e_date_str} 23:59"
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                
            if dt.date() >= now.date():
                upcoming.append(e)
        except:
            continue

    # 5. Sort by date
    upcoming.sort(key=lambda x: x["date"] + (x.get("time") or "00:00"))

    # 6. Create JS content
    js_content = f"""
// VECTIS Calendar Data Export
// Generated: {now.isoformat()}
window.CALENDAR_DATA = {json.dumps(upcoming, ensure_ascii=False, indent=2)};
"""

    with open(output_js, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"[OK] Exported {len(upcoming)} events to {output_js}")

if __name__ == "__main__":
    export_calendar()
