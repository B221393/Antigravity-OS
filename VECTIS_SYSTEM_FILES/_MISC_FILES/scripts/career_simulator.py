import os
import json
import sys
import time
import re
from pathlib import Path
from datetime import datetime

# Setup Path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "VECTIS_SYSTEM_FILES"))

try:
    from modules.researcher import ResearchAgent
    from modules.persona import PersonaAgent
    from dotenv import load_dotenv
    load_dotenv(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / ".env"))
    
    researcher = ResearchAgent(os.getenv("GEMINI_API_KEY"), os.getenv("GROQ_API_KEY"))
    persona_agent = PersonaAgent()
except Exception as e:
    print(f"Agent Init Error: {e}")
    sys.exit(1)

def run_deep_fit_simulation():
    """
    VECTIS CAREER SIMULATOR:
    Compiles all gathered drafts and research to simulate 'Life in 10 Years' for each path.
    Then provides a 'Fit Score' based on Yuto's persona.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 INITIALIZING CAREER SIMULATION...")
    
    # 1. Load context
    persona_prompt = persona_agent.get_persona_prompt()
    draft_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "es_assistant" / "drafts_targeted"
    
    if not draft_dir.exists():
        print("No targeted drafts found. Run target_operator first.")
        return

    draft_files = list(draft_dir.glob("*.md"))
    
    # 2. Simulation Prompt
    sim_prompt = f"""
    {persona_prompt}
    
    TASK: あなたの「分身」として、以下の3つのキャリアパスをシミュレーションし、徹底比較してください。
    
    【パス1: 出版・メディア】（講談社・集英社など）
    【パス2: 関西地元・優良企業】（兵庫・大阪の有力企業）
    【パス3: 国家官僚】（省庁・公共機関）
    
    各パスについて、以下の項目で「まさおAIじっくり解説」スタイルで答えてください：
    1. 10年後のあなた（どんなプロダクトを作り、どんな影響を社会に与えているか）
    2. VECTIS OSとの親和性（その環境でVECTIS哲学は生き残れるか）
    3. ガチの「合格可能性」と、今足りない「爆速」アクション
    4. フィットスコア（0-100%）
    
    最後に、すべてのデータを総合して「究極の選択」を一つだけ奨励してください。
    """
    
    print("🔮 Simulating future timelines...")
    simulation_result = researcher._call_llm(sim_prompt)
    
    # 3. Save as a special 'Judgment Card'
    report_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned" / "career_judgment_report.kcard"
    
    report_data = {
      "title": "🌌 Career Fit Simulation: 究極の選択",
      "genre": "StrategicSimulation",
      "rarity": "Legendary",
      "content": simulation_result,
      "source": "VECTIS AGI Career Simulator",
      "created_at": datetime.now().isoformat()
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        
    print("✅ Simulation Report Generated.")
    
    # 4. Deep Scraper for 'Missing' Info
    print("🔍 [DEEP SCRAPER] Hunting for hidden culture data...")
    extra_query = "出版社 編集者の本音座談会, 兵庫県優良企業 離職率 福利厚生 実態, 官公庁 インターン 参加者の感想 2ch まとめ 2025"
    deep_notes = researcher.deep_research(extra_query)
    
    with open(BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned" / "hidden_culture_intel.kcard", "w", encoding="utf-8") as f:
        json.dump({
            "title": "🕵️ Hidden Culture Intel: 業界の裏側",
            "genre": "Intelligence",
            "rarity": "Epic",
            "content": deep_notes,
            "source": "VECTIS Underground Scraper",
            "created_at": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    # Log Entry
    log_entry = f"\n---\n\n## [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n\n### DEEP FIT SIMULATION & EXTRA SCRAPING\n- **Simulation**: Projected 10-year timelines for Publishing, Local, and Bureaucracy.\n- **Intelligence**: Scanned 'hidden' data (underground culture, real-world sentiment).\n- **Conclusion**: Generated 'Ultimate Choice' report.\n"
    log_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs" / "activity_log.md"
    with open(log_path, "a", encoding="utf-8") as alog:
        alog.write(log_entry)

if __name__ == "__main__":
    run_deep_fit_simulation()
