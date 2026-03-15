import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path

# Setup path for modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))

try:
    from modules.gemini_client import ask_gemini
except ImportError:
    def ask_gemini(prompt): return "Error: Gemini module not found."

DATA_DIR = os.path.join(BASE_DIR, "data", "shukatsu")

def load_recent_data(limit=10):
    """Load the most recent JSON files from the data directory."""
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    files.sort(key=os.path.getmtime, reverse=True)
    
    recent_items = []
    for f in files[:limit]:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                recent_items.append(data)
        except Exception:
            continue
            
    return recent_items

def generate_dialogue_briefing(items):
    """Generates a PhD & Student dialogue summary."""
    
    if not items:
        return "No recent information collected to analyze."
    
    # Format items for the prompt
    items_text = ""
    for i, item in enumerate(items):
        title = item.get('title', 'No Title')
        company = item.get('company', 'Unknown Company')
        date = item.get('deadline', 'Unknown Date')
        items_text += f"{i+1}. [{company}] {title} (Deadline: {date})\n"

    prompt = f"""
    Act as a **Physics Professor (PhD)** and an **Enthusiastic Undergraduate Assistant**.
    
    They are analyzing the "Recruitment Data" (signals) collected from the market.
    Summarize the following job/internship information in a dialogue format.
    
    **Rules:**
    1. **Metaphor**: Treat the job market as a "Physical Field" or "Ecosystem".
       - High competition = "High Entropy" or "Turbulence"
       - Good opportunity = "Resonance" or "Signal"
    2. **Analysis**: The Professor should point out the "hidden trends" or "strategic value" of these specific companies.
    3. **Conclusion**: End with the Professor giving one specific "Next Action" to the Assistant.
    4. **Language**: Japanese.
    
    **Data to Analyze:**
    {items_text}
    """
    
    print("\n🧪 Generating Dialogue Analysis (PhD & Student)...\n")
    return ask_gemini(prompt)

def main():
    print("╔════════════════════════════════════════════════════╗")
    print("║        📢 EGO INTELLIGENCE BRIEFING             ║")
    print("╚════════════════════════════════════════════════════╝")
    
    items = load_recent_data(15)
    
    if not items:
        print("\n [!] No data found in shukatsu/ directory.")
        print("     Please run the Patrol first to collect data.")
    else:
        print(f"\n✅ Loaded {len(items)} recent signals.")
        dialogue = generate_dialogue_briefing(items)
        print("\n" + "="*60)
        print(dialogue)
        print("="*60 + "\n")
        
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
