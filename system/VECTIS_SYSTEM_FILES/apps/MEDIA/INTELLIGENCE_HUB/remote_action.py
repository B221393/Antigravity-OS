import os
import json
import argparse
from datetime import datetime

# --- Configuration ---
# C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\youtube_channel\status_reporter.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Data is at C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../data"))
CALENDAR_FILE = os.path.join(DATA_DIR, "precog_schedules.json")
INBOX_FILE = os.path.join(DATA_DIR, "task_inbox.json")

def add_calendar(event, date=None, time="All Day"):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    entry = {
        "Date": date,
        "Time": time,
        "Event": event,
        "Type": "REMOTE_ENTRY",
        "Priority": 5,
        "Status": "Pending",
        "Link": ""
    }
    
    data = []
    if os.path.exists(CALENDAR_FILE):
        try:
            with open(CALENDAR_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: pass
    
    data.append(entry)
    
    os.makedirs(os.path.dirname(CALENDAR_FILE), exist_ok=True)
    with open(CALENDAR_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Calendar updated: [{date}] {event}")

def add_inbox(content):
    task = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "type": "remote_memo",
        "title": content[:50],
        "description": content,
        "priority": "medium",
        "status": "unread",
        "created_at": datetime.now().isoformat()
    }
    
    data = {"inbox": []}
    if os.path.exists(INBOX_FILE):
        try:
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: pass
        if "inbox" not in data: data["inbox"] = []
    
    data["inbox"].insert(0, task) # Add to top
    
    os.makedirs(os.path.dirname(INBOX_FILE), exist_ok=True)
    with open(INBOX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Inbox updated: {content[:30]}...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["calendar", "inbox"], help="Action to perform")
    parser.add_argument("--content", help="Content for inbox or Event title for calendar", required=True)
    parser.add_argument("--date", help="Date for calendar (YYYY-MM-DD)", default=None)
    
    args = parser.parse_args()
    
    if args.action == "calendar":
        add_calendar(args.content, args.date)
    elif args.action == "inbox":
        add_inbox(args.content)
