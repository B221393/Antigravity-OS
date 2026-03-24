import os
import datetime
import pickle
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    def __init__(self, credentials_path="credentials.json", token_path="token.pickle"):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.credentials_path = os.path.join(self.base_path, credentials_path)
        self.token_path = os.path.join(self.base_path, token_path)
        self.service = None

    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        # Load token if exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or login if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Missing credentials.json at {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        print("[OK] Google Calendar Authenticated")

    def add_event(self, title, start_dt, end_dt=None, description="", location=""):
        """Add an event to the primary calendar"""
        if not self.service:
            self.authenticate()

        # Check if already isoformat, otherwise ensure it is
        if isinstance(start_dt, str):
            # Assume local time if just YYYY-MM-DD
            if len(start_dt) == 10:
                start_dt = f"{start_dt}T09:00:00+09:00" # Default 9AM JST
            # If datetime string, ensure ISO
        elif isinstance(start_dt, datetime.datetime):
             start_dt = start_dt.isoformat()

        if end_dt:
             if isinstance(end_dt, datetime.datetime):
                 end_dt = end_dt.isoformat()
        else:
             # Default to 1 hour
             try:
                 dt = datetime.datetime.fromisoformat(start_dt)
                 end_dt = (dt + datetime.timedelta(hours=1)).isoformat()
             except:
                 # usage of datetime.now() if parsing fails is risky, better ensure input is valid
                 pass
        
        # Ensure timezone offset if missing (simple fix for common errors)
        if "T" in start_dt and "+" not in start_dt and "Z" not in start_dt:
             start_dt += "+09:00"
        if end_dt and "T" in end_dt and "+" not in end_dt and "Z" not in end_dt:
             end_dt += "+09:00"

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt,
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_dt, # API handles null end by using default or erroring? better be safe
                'timeZone': 'Asia/Tokyo',
            },
            'location': location
        }

        # Handle case where end_dt might still be None/Invalid if parsing failed
        if not event['end']['dateTime']:
             # If we simply can't determine end, make it a 1 hour event from start
             try:
                 start_obj = datetime.datetime.fromisoformat(start_dt)
                 event['end']['dateTime'] = (start_obj + datetime.timedelta(hours=1)).isoformat()
             except:
                 pass

        try:
            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event_result.get('htmlLink')}")
            return event_result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_upcoming_events(self, max_results=30):
        """Fetch upcoming events"""
        if not self.service:
            self.authenticate()
            
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        
        try:
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            return events
        except Exception as e:
            print(f"Fetch failed: {e}")
            return []

if __name__ == "__main__":
    client = GoogleCalendarClient()
    try:
        client.authenticate()
        print("[OK] Authentication successful")
        
        events = client.get_upcoming_events(max_results=50)
        
        output_file_path = os.path.join(client.base_path, "events_output.txt")
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            if not events:
                f.write('No upcoming events found.\n')
                print('No upcoming events found.')
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary_line = f"{start} - {event['summary']}"
                    f.write(summary_line + '\n')
                    print(summary_line) # Also print to console for immediate feedback

        print(f"[OK] Events written to: {output_file_path}")

    except Exception as e:
        print(f"[ERROR] Auth or event fetch failed: {e}")
