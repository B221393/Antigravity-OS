import os
import json
import time
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

def oracle_cycle():
    """
    Autonomous Trend Fetcher and Card Dropper.
    Searches for information that "Yuto" should know.
    """
    if not researcher: return
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Oracle scanning the horizon...")
    
    # Target Topics
    topics = ["最新のAIエージェント開発トレンド", "IT業界の就活ニュース", "GitHubのトレンドリポジトリ"]
    
    for topic in topics:
        summary = researcher.deep_research(f"{topic} について、Yutoさんの開発の刺激になるような最新情報を5つ教えて。")
        
        # Save as an Oracle Card
        card_id = f"oracle_{int(time.time())}_{topic[:10].replace(' ', '_')}"
        save_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
        os.makedirs(save_dir, exist_ok=True)
        
        card_data = {
            "title": f"🔭 Oracle: {topic}",
            "genre": "WorldTrend",
            "rarity": "Rare",
            "content": summary,
            "source": "VECTIS Oracle (Deep Research)",
            "created_at": datetime.now().isoformat()
        }
        
        with open(save_dir / f"{card_id}.kcard", "w", encoding="utf-8") as out:
            json.dump(card_data, out, indent=2, ensure_ascii=False)
        print(f"🔮 Oracle dropped knowledge: {topic}")

if __name__ == "__main__":
    while True:
        try:
            oracle_cycle()
        except Exception as e:
            print(f"Oracle Error: {e}")
        time.sleep(3600) # Run every hour
