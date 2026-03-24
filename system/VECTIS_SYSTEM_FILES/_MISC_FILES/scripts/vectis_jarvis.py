import os
import json
import time
from pathlib import Path
from datetime import datetime

# Root DIR
BASE_DIR = Path(__file__).resolve().parents[2]
import sys
# Add both root and system files to path for flexibility
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "VECTIS_SYSTEM_FILES"))

try:
    from modules.vision_action import VisionAgent, ActionAgent
    from modules.researcher import ResearchAgent
    from dotenv import load_dotenv
    # Load .env from VECTIS_SYSTEM_FILES
    load_dotenv(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / ".env"))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    vision = VisionAgent(GEMINI_API_KEY)
    action = ActionAgent()
    researcher = ResearchAgent(GEMINI_API_KEY, GROQ_API_KEY)
except Exception as e:
    print(f"Jarvis Init Error: {e}")
    vision = None

def jarvis_self_evolution_cycle():
    """
    VECTIS Jarvis: Autonomous Self-Evolution.
    Inspired by OpenAI Operator & Google Jarvis.
    This agent researches AI agent trends and then TRIES TO IMPROVE VECTIS.
    """
    if not vision or not vision.model:
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ VECTIS JARVIS: Initiating autonomous development cycle...")

    # 1. Research Current State-of-the-Art (Masao AI references)
    goal = "OpenAIのOperatorやGoogleのJarvisの最新機能を調べて、VECTIS OSに実装すべき『面白い新機能』のアイデアを1つだけ選んで提案し、そのための新しいファイルを作成せよ。"
    print(f"🧠 [THINK] Researching high-level objectives...")
    
    ideas_summary = researcher.deep_research("AIエージェント（Operator, Jarvis, Computer Use）の最新トレンドと、個人開発OS『VECTIS』に組み込むべき面白い機能の具体案。")
    
    # 2. Design the feature
    prompt = f"""
    CONTEXT:
    The user wants something as 'interesting' as OpenAI Operator or Google Jarvis.
    VECTIS is a personal developer OS with a 3D Mandala Chart and autonomous memory agents.
    
    RESEARCH SUMMARY:
    {ideas_summary}
    
    TASK:
    Design ONE radical, interesting, and premium feature for VECTIS. 
    It must be something an AI Agent can realistically build within the current filesystem.
    
    Examples:
    - 'Dynamic Weather System' that changes the 3D map colors based on REAL local weather.
    - 'Autonomous GitHub Repo Fetcher' that visualizes user's code as part of the Mandala.
    - 'AI-Driven Music/Soundscape' that plays sounds based on the currently selected node type.
    
    RETURN ONLY A JSON OBJECT:
    {{
        "feature_name": "Unique Name",
        "description": "What it does",
        "implementation_plan": "Step by step",
        "filename": "absolute_path_to_new_script",
        "code_content": "Full python code for the script"
    }}
    """
    
    try:
        response = researcher._call_llm(prompt)
        # Handle cases where LLM might wrap in markers
        clean_json = response.strip().replace("```json", "").replace("```", "")
        plan = json.loads(clean_json)
        
        feature_name = plan.get("feature_name")
        new_file = plan.get("filename", "").replace("absolute_path_to_new_script", str(BASE_DIR / "VECTIS_SYSTEM_FILES" / "scripts" / "new_feature.py"))
        content = plan.get("code_content")
        
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        with open(new_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"✅ [JARVIS] Feature Developed: {feature_name}")
        print(f"📂 Created: {new_file}")
        
        # log to activity log
        log_entry = f"\n---`n`n## [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]`n`n### JARVIS AUTONOMOUS DEVELOPMENT`n- **Developed**: {feature_name}`n- **Rationale**: Inspired by OpenAI Operator/Jarvis trends.`n- **Details**: {plan.get('description')}`n"
        # Since we are in python, use file append
        log_path = BASE_DIR / "VECTIS_SYSTEM_FILES" / "outputs" / "logs" / "activity_log.md"
        with open(log_path, "a", encoding="utf-8") as alog:
            alog.write(log_entry)

    except Exception as e:
        print(f"❌ [JARVIS] Evolution Loop Failed: {e}")

if __name__ == "__main__":
    jarvis_self_evolution_cycle()
