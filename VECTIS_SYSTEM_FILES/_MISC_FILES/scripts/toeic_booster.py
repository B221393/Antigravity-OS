import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Setup Path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "VECTIS_SYSTEM_FILES"))

try:
    from modules.researcher import ResearchAgent
    from modules.persona import PersonaAgent
    from modules.blogger import BloggerAgent
    # Try importing rust core but fallback if not compiled yet
    try:
        import vectis_core
        RUST_ENABLED = True
    except:
        RUST_ENABLED = False
        
    from dotenv import load_dotenv
    load_dotenv(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / ".env"))
    
    researcher = ResearchAgent(os.getenv("GEMINI_API_KEY"), os.getenv("GROQ_API_KEY"))
    persona_agent = PersonaAgent()
    blogger = BloggerAgent()
except Exception as e:
    print(f"Agent Init Error: {e}")
    sys.exit(1)

KODANSHA_DEADLINE = datetime(2026, 1, 13, 12, 0)

def run_toeic_booster():
    """
    VECTIS TOEIC BOOSTER (aka Jiritsu-chan):
    Efficiently scans for business/academic knowledge relevant to TOEIC 
    while keeping the Kodansha deadline in mind.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 TOEIC BOOSTER: MODE ACTIVE")
    
    # 1. Deadline Check
    now = datetime.now()
    delta = KODANSHA_DEADLINE - now
    days = delta.days
    hours = delta.seconds // 3600
    print(f"🚨 KODANSHA DEADLINE ALERT: {days} days {hours} hours remaining.")

    # 2. Strategic Research for 'High Yield' TOEIC Knowledge
    # We focus on Business scenarios since they help both TOEIC and Kodansha.
    query = "TOEIC頻出ビジネス英語 特殊表現 2025-2026トレンド, 出版業界で使われる英語ビジネス用語"
    print(f"📚 Gathering strategic knowledge: {query}")
    raw_intel = researcher.deep_research(query)
    
    # 3. Knowledge Filtering (Rust-powered concept)
    # If rust is enabled, we score the importance.
    importance_score = 0
    if RUST_ENABLED:
        try:
            importance_score = vectis_core.calculate_toeic_relevance(raw_intel)
            print(f"⚡ Rust Core Analysis: TOEIC Relevance Score = {importance_score:.1f}")
        except: pass

    # 4. Generate 'Drill' Cards
    parsing_prompt = f"""
    Based on the intel:
    {raw_intel}
    
    Create 5 'TOEIC High-Speed Drill' Knowledge Cards.
    Focus on Vocabulary or Grammar patterns that are frequent in TOEIC and useful for a Global Publisher (Kodansha).
    
    Return as JSON list:
    [
      {{
        "title": "TOEIC x Kodansha: [Word/Pattern]",
        "genre": "TOEIC_Advanced",
        "rarity": "Epic",
        "content": "Word meaning, usage in business context, and a sample sentence reflecting Yuto's persona.",
        "action": "Memorize burst"
      }}
    ]
    RETURN ONLY RAW JSON.
    """
    
    try:
        json_res = researcher._call_llm(parsing_prompt)
        import re
        json_match = re.search(r'\[.*\]', json_res, re.DOTALL)
        if json_match:
            cards = json.loads(json_match.group(0))
            
            kcard_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
            os.makedirs(kcard_dir, exist_ok=True)
            
            for c in cards:
                c_title = c.get('title', 'TOEIC Drill')
                save_path = kcard_dir / f"toeic_drill_{int(time.time())}_{cards.index(c)}.kcard"
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "title": f"🎯 {c_title}",
                        "genre": c.get('genre'),
                        "rarity": c.get('rarity'),
                        "content": c.get('content'),
                        "source": "VECTIS TOEIC BOOSTER (Jiritsu-chan)",
                        "importance": importance_score,
                        "created_at": datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)
            print(f"✅ Generated {len(cards)} TOEIC strategic drill cards.")
    except Exception as e:
        print(f"Card generation error: {e}")

    # 5. Log & Reflect
    reflection = f"Kodansha deadline approach: focus on semi-business English. TOEIC preparation is optimized for publishing context."
    blogger.log_entry(
        user_instruction="TOEIC効率化 + 講談社締め切り意識",
        research_process=[query],
        actions=[f"Deadline Alert: {days}d left", "Rust Score Analysis", "Drill Card Generation"],
        output=f"Synced TOEIC cards to Mandala. Reminder: Jan 13 Deadline.",
        reflection=reflection
    )

if __name__ == "__main__":
    run_toeic_booster()
