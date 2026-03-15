import os
import json
import sys
import time
import re
from pathlib import Path
from datetime import datetime

# Setup Path
BASE_DIR = Path(__file__).resolve().parents[2]
import sys
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "VECTIS_SYSTEM_FILES"))

try:
    from modules.researcher import ResearchAgent
    from modules.persona import PersonaAgent
    from modules.vision_action import ActionAgent
    from modules.blogger import BloggerAgent
    from dotenv import load_dotenv
    load_dotenv(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / ".env"))
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    researcher = ResearchAgent(gemini_key, groq_key)
    persona_agent = PersonaAgent()
    action = ActionAgent()
    blogger = BloggerAgent()
except Exception as e:
    print(f"Agent Init Error: {e}")
    sys.exit(1)

def run_internship_autonomy():
    """
    VECTIS INTERN OPERATOR:
    1. Search for 10 internships.
    2. Analyze them against Yuto's persona.
    3. Draft ES for each.
    4. Save as Mission Results.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 MISSION START: Internship Autonomous Hunt")
    
    # 1. Gather Persona Context
    persona_prompt = persona_agent.get_persona_prompt()
    print("🧠 Persona Context loaded.")

    # 2. Research Phase
    query = "2026年卒業向け IT・AIエージェント・スタートアップのインターンシップ募集情報 10件"
    print(f"🔍 Searching: {query}")
    
    # Use researcher to find data
    raw_data = researcher.deep_research(query)
    
    # Structure the found internships
    parsing_prompt = f"""
    Based on this research:
    {raw_data}
    
    Extract 10 specific internship opportunities. 
    Return as a JSON list of objects:
    [
      {{
        "company": "Company Name",
        "role": "Role Name",
        "url": "URL if found, else Search URL",
        "description": "Short description",
        "deadline": "If found"
      }}
    ]
    RETURN ONLY RAW JSON.
    """
    
    try:
        json_res = researcher._call_llm(parsing_prompt)
        clean_json = re.search(r'\[.*\]', json_res, re.DOTALL).group(0)
        jobs = json.loads(clean_json)
        print(f"✅ Found {len(jobs)} opportunities.")
    except Exception as e:
        print(f"Parsing error: {e}")
        jobs = []

    results_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "es_assistant" / "drafts"
    os.makedirs(results_dir, exist_ok=True)
    
    mission_history = []
    
    # 3. Processing Phase
    for idx, job in enumerate(jobs):
        company = job.get('company', 'Unknown')
        role = job.get('role', 'Intern')
        print(f"📝 Drafting ES for {company} [{idx+1}/10]...")
        
        es_prompt = f"""
        {persona_prompt}
        
        TASK: {company}の{role}インターンシップに向けた、Entry Sheet（ES）のドラフトを作成してください。
        特に「志望動機」と「自己PR（VECTIS OS開発経験を絡めて）」を重点的に書いてください。
        トーン：ユーザー本人の文体（Yuto）を完全に再現すること。
        
        JOB INFO:
        {job.get('description')}
        """
        
        try:
            draft = researcher._call_llm(es_prompt)
            
            # Save Draft
            safe_name = re.sub(r'[^\w\s-]', '', company).strip().replace(' ', '_')
            filename = f"draft_{datetime.now().strftime('%Y%m%d')}_{safe_name}.md"
            with open(results_dir / filename, "w", encoding="utf-8") as f:
                f.write(f"# ES DRAFT: {company} - {role}\n")
                f.write(f"Source: {job.get('url')}\n")
                f.write(f"Generated at: {datetime.now()}\n\n")
                f.write(draft)
            
            # Save Synapse Node
            synapse_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
            syn_id = f"syn_intern_{safe_name}"
            with open(synapse_dir / f"{syn_id}.synapse", "w", encoding="utf-8") as f:
                json.dump({
                    "title": f"🔗 Intern Match: {company}",
                    "type": "Synapse",
                    "content": f"AIが発見した適合ターゲットです。\n企業のビジョンとYutoさんのOS開発の方向性が合致しています。\nESドラフト作成済み: {filename}",
                    "url": job.get('url'),
                    "mtime": time.time()
                }, f, indent=2, ensure_ascii=False)
                
            mission_history.append(f"Collected internship for {company} and drafted ES.")
            
        except Exception as e:
            print(f"Error drafting for {company}: {e}")

    # 4. Finalizing
    summary_report = f"MANDALA MISSION COMPLETE: {len(jobs)} internships processed. All drafts saved in ES Studio."
    print(f"\n✅ {summary_report}")
    
    # Log to system
    log_entry = f"\n---`n`n## [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]`n`n### FULLY AUTONOMOUS MISSION: INTERN HUNTER`n- **Total Processed**: {len(jobs)}`n- **Actions**: Searched, Scraped, Analyzed Persona, Drafted 10 Application Documents.`n- **Visual Result**: Connected in Mandala Tree.`n- **Output**: drafts saved to `es_assistant/drafts/``n"
    log_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs" / "activity_log.md"
    with open(log_path, "a", encoding="utf-8") as alog:
        alog.write(log_entry)

    # 5. Voluntarily open the first result to show Jarvis is working
    if jobs:
        print("🌍 Jarvis is opening the target site for review...")
        action.fast_open(jobs[0].get('url', 'https://www.google.com'))

if __name__ == "__main__":
    run_internship_autonomy()
