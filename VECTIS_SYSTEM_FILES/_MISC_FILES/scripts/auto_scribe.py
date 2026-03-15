import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Add root to path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

try:
    from modules.researcher import ResearchAgent
    from dotenv import load_dotenv
    load_dotenv(str(BASE_DIR / ".env"))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    researcher = ResearchAgent(GEMINI_API_KEY, GROQ_API_KEY)
except ImportError:
    researcher = None

def auto_scribe_activity():
    """
    Reads activity_log.md and converts recent logs into Knowledge Cards (K-Cards).
    """
    log_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs" / "activity_log.md"
    if not log_path.exists():
        print("Log not found.")
        return

    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by entries
    entries = content.split("---")
    # Take last 10 entries
    recent_entries = entries[-10:]

    for entry in recent_entries:
        if "### INPUT" not in entry: continue
        
        # Extract title/summary using LLM if possible
        if researcher:
            prompt = f"""
            TASK: Convert the following activity log entry into a Knowledge Card.
            STYLE: Masao AI (Thorough, Logical, Personal Developer context).
            
            ENTRY:
            {entry[:2000]}
            
            FORMAT (JSON):
            {{
                "title": "Clear, informative title",
                "genre": "AgentLog",
                "rarity": "Uncommon",
                "content": "Thorough explanation of what was achieved and why it matters (Masao AI style).",
                "source": "VECTIS Activity Log",
                "visual_seed": "Cybernetic brain connection"
            }}
            RETURN ONLY JSON.
            """
            card_json = researcher.generate_card_data("Activity Scribe", entry)
            if card_json:
                # Save to knowledge cards
                save_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
                os.makedirs(save_dir, exist_ok=True)
                
                filename = f"agent_log_{int(datetime.now().timestamp())}_{os.urandom(4).hex()}.kcard"
                with open(save_dir / filename, "w", encoding="utf-8") as out:
                    # Ingest Masao-style if possible
                    # We modify the content to be more "jikkuri"
                    json.dump(card_json, out, indent=2, ensure_ascii=False)
                print(f"Scribed: {card_json['title']}")

if __name__ == "__main__":
    auto_scribe_activity()
