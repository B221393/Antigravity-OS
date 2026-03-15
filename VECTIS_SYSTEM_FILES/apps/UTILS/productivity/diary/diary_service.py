
import os
import json
import uuid
from datetime import datetime

class DiaryService:
    def __init__(self, storage_path: str):
        self.filepath = storage_path
        self._ensure_dir()
        self.entries = self.load_entries()

    def _ensure_dir(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def load_entries(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_entries(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def get_entries(self):
        """Return all entries."""
        return self.entries

    def add_entry(self, title: str, content: str, clarity: int = 50, entry_type: str = "user_log"):
        """Add a new entry and save to disk."""
        new_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": title if title else "Untitled Log",
            "clarity": clarity,
            "content": content,
            "type": entry_type
        }
        # Insert at top (newest first)
        self.entries.insert(0, new_entry)
        self.save_entries()
        return new_entry

    def search_entries(self, keyword: str):
        """Filter entries by keyword."""
        if not keyword:
            return self.entries
        
        kw = keyword.lower()
        return [
            e for e in self.entries 
            if kw in e.get('content', '').lower() or kw in e.get('title', '').lower()
        ]
