
import os
import json
import sys
from datetime import datetime

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../data/ai_feedback_loop.json"))

def add_feedback(critique, instruction, priority="medium"):
    feedback = {
        "target_topic": "Manual Injection",
        "critique": critique,
        "instruction": instruction,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    existing_feedback = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                existing_feedback = json.load(f)
        except: pass
    
    existing_feedback.insert(0, feedback)
    existing_feedback = existing_feedback[:20] # Keep recent
    
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing_feedback, f, indent=2, ensure_ascii=False)
    
    print(f"📥 Feedback registered: {instruction}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python vectis_feedback.py \"Problem\" \"Correction Instruction\"")
        sys.exit(1)
    
    critique = sys.argv[1]
    instruction = sys.argv[2]
    priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
    
    add_feedback(critique, instruction, priority)
