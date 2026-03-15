
import sys
import os
import argparse
import time
import json
from pathlib import Path

# EGO Core Integration
EGO_ROOT = Path(r"C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES")
sys.path.append(str(EGO_ROOT))

# Configuration
LIBERAL_ARTS_FILE = EGO_ROOT / "LIBERAL_ARTS_NEXUS.md"
IDEAS_LOG = EGO_ROOT / "IDEAS_LOG.md"

try:
    from modules.gemini_client import GenerativeModel
except ImportError:
    GenerativeModel = None

class IdeationEngine:
    def __init__(self):
        self.model = GenerativeModel() if GenerativeModel else None
        self.nexus_content = self._load_file(LIBERAL_ARTS_FILE)

    def _load_file(self, path):
        if path.exists():
            return path.read_text(encoding='utf-8')
        return "No Liberal Arts data found."

    def generate_idea(self, mode="project"):
        print(f"🧠 [Ideation] Spinning up neural engine... Mode: {mode}")
        
        if not self.model:
            print("❌ No AI Model available.")
            return

        prompt = f"""
You are the EGO Ideation Engine.
Your goal is to generate radical, "Blue Ocean" ideas by cross-pollinating the user's Intellectual Arsenal with modern trends.

# User's Intellectual Arsenal (Source Material)
{self.nexus_content}

# Task
Generate 3 distinct ideas for: {mode.upper()}
1. **The Concept**: A short, punchy title.
2. **The Equation**: How it combines User's Strength (e.g., Chaos Structuring) + Market Need.
3. **The 'Crazy' Factor**: Why this is unique/weird but valuable.

# Constraints
- Be bold. Avoid generic "ToDo apps".
- Use the user's "Uri" (Selling Points) explicitly.
- Format as Markdown.
"""
        try:
            response_obj = self.model.generate_content(prompt)
            idea_text = response_obj.text
            
            self._save_idea(mode, idea_text)
            print("\n" + "="*40)
            print(idea_text)
            print("="*40 + "\n")
            print(f"✅ Saved to {IDEAS_LOG}")
            
        except Exception as e:
            print(f"❌ Ideation failed: {e}")
            print("⚠️ Engaging Emergency Creativity Protocol...")
            
            fallback_idea = """
# 💡 Project Idea (Emergency Fallback)

## 1. The Concept: "EGO OMNI-STREAM" (Universal Timeline)
## 2. The Equation
**Chaos Structuring** + **Daily Logging** = **One Infinite Stream**

Instead of separate apps for Journal, Todo, and News, create **ONE** timeline.
-   Past: Your journal logs.
-   Present: Your active todo tasks.
-   Future: Your calendar events + Probabilistic goal completion dates.

## 3. The 'Crazy' Factor
It treats your life like a **git log**.
You can 'commit' your day, 'branch' into a new hobby, and 'merge' learned skills back into your Identity Core.
It uses **Vector Search** (RAG) to find relevant past logs when you are typing a new one.
"""
            self._save_idea(mode, fallback_idea)
            print(fallback_idea)

    def _save_idea(self, mode, text):
        timestamp = time.strftime('%Y-%m-%d %H:%M')
        entry = f"\n\n## 💡 {mode.title()} Idea ({timestamp})\n\n{text}\n\n---"
        
        mode = "a" if IDEAS_LOG.exists() else "w"
        with open(IDEAS_LOG, mode, encoding='utf-8') as f:
            f.write(entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="project", choices=["project", "career", "writing"], help="Type of idea to generate")
    args = parser.parse_args()
    
    engine = IdeationEngine()
    engine.generate_idea(mode=args.mode)
