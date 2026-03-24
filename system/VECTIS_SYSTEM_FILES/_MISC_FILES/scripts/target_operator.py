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

def run_targeted_mission():
    """
    VECTIS TARGET OPERATOR:
    Focus on: Publishing, Hyogo/Osaka Local, and Bureaucracy.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🏹 MISSION START: Multi-Path Target Hunt")
    
    persona_prompt = persona_agent.get_persona_prompt()
    
    targets = [
        "2026年卒 出版社 インターンシップ (講談社, 集英社, 小学館, KADOKAWA等) 大阪・兵庫拠点含む",
        "兵庫県・大阪府内の優良企業 インターンシップ 2026 募集情報",
        "国家公務員 総合職・一般職 (官僚) インターンシップ 2026 官公庁 募集"
    ]
    
    all_jobs = []
    
    for query in targets:
        print(f"🔍 Searching: {query}")
        raw_data = researcher.deep_research(query)
        
        parsing_prompt = f"""
        Based on this research:
        {raw_data}
        
        Extract 4-5 specific opportunities. 
        Return as a JSON list of objects:
        [
          {{
            "company": "Company or Ministry Name",
            "role": "Role Name",
            "url": "URL if found",
            "description": "Short description",
            "category": "Publishing" | "Local_Kansai" | "Bureaucracy"
          }}
        ]
        RETURN ONLY RAW JSON.
        """
        
        try:
            json_res = researcher._call_llm(parsing_prompt)
            json_match = re.search(r'\[.*\]', json_res, re.DOTALL)
            if json_match:
                jobs = json.loads(json_match.group(0))
                all_jobs.extend(jobs)
        except Exception as e:
            print(f"Parsing error for {query}: {e}")

    print(f"✅ Total {len(all_jobs)} targets identified.")

    results_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "es_assistant" / "drafts_targeted"
    os.makedirs(results_dir, exist_ok=True)
    
    for idx, job in enumerate(all_jobs):
        company = job.get('company', 'Unknown')
        cat = job.get('category', 'General')
        print(f"📝 Drafting targeted ES for {company} ({cat}) [{idx+1}/{len(all_jobs)}]...")
        
        es_prompt = f"""
        {persona_prompt}
        
        TASK: {company}のインターンシップに向けた、Entry Sheet（ES）のドラフトを作成してください。
        
        ATTENTION:
        - もし出版系なら「編集者としての直感とVECTIS OSのシステム構築力」を。
        - もし兵庫/大阪企業なら「地元・関西の発展への貢献」を。
        - もし官僚なら「公共の利益と技術による国家基盤の最適化」を。
        
        トーン：ユーザー本人の文体（Yuto）を完全に再現すること。
        """
        
        try:
            draft = researcher._call_llm(es_prompt)
            safe_name = re.sub(r'[^\w\s-]', '', company).strip().replace(' ', '_')
            filename = f"target_{cat}_{safe_name}.md"
            with open(results_dir / filename, "w", encoding="utf-8") as f:
                f.write(f"# TARGETED ES: {company}\n")
                f.write(f"Category: {cat}\n\n")
                f.write(draft)
            
            # Synapse Node
            synapse_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
            with open(synapse_dir / f"syn_target_{safe_name}.synapse", "w", encoding="utf-8") as f:
                json.dump({
                    "title": f"🎯 Priority Target: {company}",
                    "type": "Synapse",
                    "content": f"Yutoさんの希望条件（{cat}）に合致する最優先ノードです。\nESドラフト生成済み: {filename}",
                    "url": job.get('url'),
                    "mtime": time.time()
                }, f, indent=2, ensure_ascii=False)
        except: pass

    # Log to system
    log_entry = f"\n---\n\n## [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n\n### TARGETED MISSION: PUBLISHING & BUREAUCRACY\n- **Targets**: Publishing, Hyogo/Osaka, Bureaucracy.\n- **Results**: Generated {len(all_jobs)} specific strategy cards and ES drafts.\n- **Focus**: Strategic narrative alignment for local and national impact.\n"
    log_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs" / "activity_log.md"
    with open(log_path, "a", encoding="utf-8") as alog:
        alog.write(log_entry)
    
    print("✅ Mission Success.")

if __name__ == "__main__":
    run_targeted_mission()
