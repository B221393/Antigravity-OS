import os
import json
import glob
from datetime import datetime

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHUKATSU_DIR = os.path.join(BASE_DIR, "data", "shukatsu")
INBOX_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../data/task_inbox.json"))
RESEARCH_NOTES_FILE = r"C:\Users\Yuto\clawd\research_notes.md"

def get_today_stats():
    today_str = datetime.now().strftime("%Y%m%d")
    count = 0
    kddi_count = 0
    liberal_arts_count = 0
    overclock_mode = False
    
    # Files
    if os.path.exists(SHUKATSU_DIR):
        files = glob.glob(os.path.join(SHUKATSU_DIR, f"SHUKATSU_{today_str}_*.json"))
        count = len(files)
        
        # Deep Analysis Check
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as j:
                    data = json.load(j)
                    title = data.get('title', '')
                    if "KDDI" in title or "トヨタ" in title or "ソニー" in title:
                        kddi_count += 1
                    analysis = data.get('ai_analysis', {})
                    if "academic_deep_dive" in analysis:
                        liberal_arts_count += 1
            except: pass

    # Research Notes Size
    notes_size = 0
    last_update = "Unknown"
    if os.path.exists(RESEARCH_NOTES_FILE):
        notes_size = os.path.getsize(RESEARCH_NOTES_FILE)
        mtime = os.path.getmtime(RESEARCH_NOTES_FILE)
        last_update = datetime.fromtimestamp(mtime).strftime("%H:%M")

    # Inbox Check
    unread_tasks = 0
    if os.path.exists(INBOX_FILE):
        try:
            with open(INBOX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                unread_tasks = sum(1 for t in data.get('inbox', []) if t.get('status') == 'unread')
        except: pass

    return {
        "date": datetime.now().strftime("%Y/%m/%d"),
        "time": datetime.now().strftime("%H:%M"),
        "total_files_today": count,
        "deep_dive_hits": kddi_count,
        "liberal_arts_hits": liberal_arts_count,
        "notes_size_kb": round(notes_size / 1024, 1),
        "notes_last_update": last_update,
        "unread_tasks": unread_tasks
    }

if __name__ == "__main__":
    stats = get_today_stats()
    
    print("-" * 30)
    print(f"📊 VECTIS STATUS REPORT ({stats['time']})")
    print("-" * 30)
    print(f"📅 Date: {stats['date']}")
    print(f"📥 Today's Intel: {stats['total_files_today']} files")
    print(f"   - 🏢 Deep Dive (KDDI etc): {stats['deep_dive_hits']}")
    print(f"   - 🏛️ Liberal Arts: {stats['liberal_arts_hits']}")
    print(f"📓 JibunPedia: {stats['notes_size_kb']} KB (Last: {stats['notes_last_update']})")
    print(f"📫 Task Inbox: {stats['unread_tasks']} unread")
    print("-" * 30)
    print("✅ System: Overclock Mode Active")
    print("-" * 30)
