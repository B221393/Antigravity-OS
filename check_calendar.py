import datetime
import os
import pickle
import json
from googleapiclient.discovery import build

def get_calendar_events():
    # Base path configuration
    base_dir = r"C:\Users\Yuto\Desktop\app"
    token_path = os.path.join(base_dir, 'python_scripts', 'token.pickle')
    output_path = os.path.join(base_dir, 'calendar_events.json')
    
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    else:
        print(f'Critical Error: {token_path} not found.')
        return

    if not creds or not creds.valid:
        print('Error: Invalid credentials.')
        return

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Get events for the next 14 days
        now = datetime.datetime.utcnow().isoformat() + 'Z'  
        time_max = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).isoformat() + 'Z'

        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Fetching Google Calendar events...')
        
        events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=time_max,
                                              maxResults=50, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        formatted_events = []
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            
            # Categorization Logic (Autonomous Analysis)
            category = "General"
            priority = 3
            
            shukatsu_keywords = ["面接", "ES", "選考", "締切", "説明会", "パナソニック", "AVC", "重工"]
            dev_keywords = ["Dev", "Code", "GitHub", "App", "Sync", "Antigravity"]
            
            if any(k in summary for k in shukatsu_keywords):
                category = "Shukatsu"
                priority = 1
            elif any(k in summary for k in dev_keywords):
                category = "Development"
                priority = 2

            # Time formatting
            if 'T' in start:
                dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                dt_jst = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                start_str = dt_jst.strftime('%Y-%m-%d %H:%M')
            else:
                start_str = start

            formatted_events.append({
                "start": start_str,
                "summary": summary,
                "category": category,
                "priority": priority
            })

        # Output to JSON for Dashboard Integration
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_events, f, ensure_ascii=False, indent=4)
        
        print(f'Successfully synced {len(formatted_events)} events to {output_path}')

    except Exception as e:
        print(f'Calendar Sync Error: {e}')

if __name__ == "__main__":
    get_calendar_events()
