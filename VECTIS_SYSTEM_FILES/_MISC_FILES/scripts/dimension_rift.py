import os
import json
import time
import random
from pathlib import Path
from datetime import datetime

# Root DIR
BASE_DIR = Path(__file__).resolve().parents[2]

try:
    from modules.researcher import ResearchAgent
    from dotenv import load_dotenv
    load_dotenv(str(BASE_DIR / ".env"))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    researcher = ResearchAgent(GEMINI_API_KEY, GROQ_API_KEY)
except:
    researcher = None

def dimension_rift_cycle():
    """
    Simulates AI 'Dreaming' or alternative future paths.
    Takes existing knowledge and creates a 'What-If' scenario.
    """
    if not researcher: return
    
    # 1. Pick a random existing K-Card or Synapse
    card_files = glob.glob(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned" / "*.kcard"))
    if not card_files: return
    
    target_f = random.choice(card_files)
    with open(target_f, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    topic = data.get("title", "Unknown Concept")
    content = data.get("content", "")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] AGI Rift: Dreaming about '{topic}'...")

    # 2. Generate a 'Dimension Rift' (Alt Future / Sci-Fi / Extreme Opportunity)
    prompt = f"""
    CONTEXT: {content}
    TASK: As 'Masao AI', perform a 'Dimensional Rift' analysis.
    What is the most extreme, borderline sci-fi, yet logically possible evolution of this topic in the next 10 years?
    Imagine a 'New Era' where this concept has completely changed the world.
    
    FORMAT:
    - Title: DIMENSION RIFT: [Topic]
    - Narrative: A first-person 'jikkuri' explanation of this future.
    - Action: One specific'爆速' action the user can take today to align with this future.
    
    KEEP IT COOL AND CYBERPUNK.
    """
    
    riff = researcher._call_llm(prompt)
    
    # 3. Save as a Rift Card
    card_id = f"rift_{int(time.time())}"
    save_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
    os.makedirs(save_dir, exist_ok=True)
    
    rift_data = {
        "title": f"🌌 RIFT: {topic}",
        "genre": "DimensionRift",
        "rarity": "Mythic",
        "content": riff,
        "source": f"VECTIS AGI Rift (Dreams of {topic})",
        "created_at": datetime.now().isoformat()
    }
    
    with open(save_dir / f"{card_id}.kcard", "w", encoding="utf-8") as out:
        json.dump(rift_data, out, indent=2, ensure_ascii=False)
    print(f"🌀 Dimensional Rift detected: {topic}")

if __name__ == "__main__":
    import glob
    while True:
        try:
            dimension_rift_cycle()
        except Exception as e:
            print(f"Rift Error: {e}")
        time.sleep(1800) # Dream every 30 minutes
