import os
import sys
import json
from datetime import datetime
import uuid

# Ensure we can import modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from apps.diary.diary_service import DiaryService
except ImportError:
    # Fallback/Mock for standalone testing if needed, but in TDD we rely on project structure
    DiaryService = None

class DiscordLogic:
    def __init__(self, diary_path=None, memo_path=None):
        self.project_root = PROJECT_ROOT
        
        # Determine actual paths if not provided (Production mode)
        if not diary_path:
            self.diary_path = os.path.join(self.project_root, "apps", "diary", "data", "entries.json")
        else:
            self.diary_path = diary_path
            
        if not memo_path:
            self.memo_path = os.path.join(self.project_root, "apps", "job_hunting", "memo_data.json")
        else:
            self.memo_path = memo_path

    def add_diary_entry(self, content: str) -> dict:
        """Add entry to Neural Log via DiaryService."""
        try:
            # We instantiate DiaryService manually to ensure we point to the right file
            # Ideally DiaryService should handle file creation
            
            # Simple direct JSON manipulation or Service usage?
            # Let's use Service logic to be consistent with the Schema.
            
            # 1. Ensure dir exists
            os.makedirs(os.path.dirname(self.diary_path), exist_ok=True)
            
            # 2. Load existing
            entries = []
            if os.path.exists(self.diary_path):
                with open(self.diary_path, "r", encoding="utf-8") as f:
                    try:
                        entries = json.load(f)
                    except:
                        entries = []
            
            # 3. Create Entry
            new_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "title": "Mobile Entry",
                "clarity": 50,
                "content": content,
                "type": "discord_log"
            }
            
            # 4. Save
            entries.insert(0, new_entry)
            with open(self.diary_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
                
            return {"success": True, "entry": new_entry}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_task(self, content: str) -> dict:
        """Add task to Manager Memo JSON."""
        try:
            os.makedirs(os.path.dirname(self.memo_path), exist_ok=True)
            
            data = {"done_list": [], "free_memo": ""}
            if os.path.exists(self.memo_path):
                with open(self.memo_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except:
                        pass
            
            data["done_list"].append({"item": content, "status": "todo"})
            
            with open(self.memo_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            return {"success": True, "count": len(data["done_list"])}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
