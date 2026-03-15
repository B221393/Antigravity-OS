
import json
import os
from datetime import datetime

# Path
json_path = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\UTILS\calendar\events.json"

# Load
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        events = json.load(f)
else:
    events = []

# Filter out "Library" event (User said "delete the trial one")
events = [e for e in events if "図書館" not in e['title']]

# Check if Meitec exists
meitec_exists = any("メイテック" in e['title'] for e in events)

if not meitec_exists:
    # Add Meitec (Tomorrow: 2026-02-09)
    events.append({
        "id": "meitec_event_001",
        "title": "メイテック (面接/説明会)",
        "date": "2026-02-09",
        "time": "10:00", # Placeholder time
        "category": "💼 就活",
        "memo": "User requested update.",
        "created": datetime.now().isoformat()
    })

# Add Civil Service Exam (Today: 2026-02-08)
civil_exists = any("公務員試験" in e['title'] for e in events)
if not civil_exists:
    events.append({
        "id": "civil_service_001",
        "title": "公務員試験 応募",
        "date": "2026-02-08",
        "time": "",
        "category": "💼 就活",
        "memo": "Preparation/Application",
        "created": datetime.now().isoformat()
    })

# Save
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(events, f, indent=2, ensure_ascii=False)

print(f"Updated events.json with {len(events)} items.")
