import sys
import os
import json
from datetime import datetime

# Path to stats file
STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../apps/usage_stats.json")

def track(app_name):
    data = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}
    
    # Update count
    if app_name not in data:
        data[app_name] = {"count": 0, "last_used": ""}
    
    data[app_name]["count"] += 1
    data[app_name]["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Write back
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # print(f"[USAGE TRACKED] {app_name}: {data[app_name]['count']}")
    except Exception as e:
        print(f"Tracking Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        track(sys.argv[1])
