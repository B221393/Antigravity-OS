
import os
import sys
import json
import glob
from datetime import datetime

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SHUKATSU_DIR = os.path.join(DATA_DIR, "shukatsu")
FEEDBACK_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../data/ai_feedback_loop.json"))

# Import LLM
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))
try:
    from modules.unified_llm_client import ask_llm
except:
    def ask_llm(p): return "Error loading LLM"

def load_recent_intelligence(count=5):
    files = glob.glob(os.path.join(SHUKATSU_DIR, "SHUKATSU_*.json"))
    files.sort(key=os.path.getmtime, reverse=True)
    
    recent_data = []
    for f in files[:count]:
        try:
            with open(f, 'r', encoding='utf-8') as j:
                recent_data.append(json.load(j))
        except: pass
    return recent_data

def audit_and_feedback():
    print("🔍 Starting Intelligence Audit...")
    intel = load_recent_intelligence(10)
    
    if not intel:
        print("   ⚠️ No intelligence found to audit.")
        return

    # Prepare context for the Auditor AI
    audit_context = ""
    for item in intel:
        audit_context += f"\n- Title: {item.get('title')}\n  Analysis: {json.dumps(item.get('ai_analysis'), ensure_ascii=False)}\n"

    prompt = f"""
あなたはEGOシステムの「品質管理AI (QA Auditor)」です。
以下の最近の収集情報の分析結果をレビューし、精度や戦略性が不足している点を指摘してください。

【最近の分析内容】
{audit_context}

【あなたの任務】
1. 分析が表面的なもの（ニュースの単なる要約）になっていないかチェック。
2. ユーザー（Yuto）にとっての「具体的なアクション」が伴っているか。
3. 27卒就活としての戦略性が薄い場合、どのような視点を追加すべきか。

以下のJSON形式で、改善のための「フィードバック指令」を1つ〜3つ作成してください：
{{
    "feedbacks": [
        {{
            "target_topic": "対象トピックまたは全体",
            "critique": "具体的な問題点の指摘",
            "instruction": "今後AIが分析時に守るべき具体的な指示（例：『単なる要約ではなく、必ず競合他社との比較を含めよ』等）",
            "priority": "high/medium/low"
        }}
    ]
}}
"""
    try:
        response = ask_llm(prompt)
        
        # Extract JSON
        import re
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        if start_idx != -1 and end_idx != -1:
            feedback_data = json.loads(response[start_idx:end_idx+1])
            
            # Save to feedback loop
            existing_feedback = []
            if os.path.exists(FEEDBACK_FILE):
                try:
                    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                        existing_feedback = json.load(f)
                except: pass
            
            # Add timestamp and source
            for fb in feedback_data.get('feedbacks', []):
                fb['created_at'] = datetime.now().isoformat()
                fb['status'] = 'active'
                existing_feedback.insert(0, fb)
            
            # Keep only last 20 instructions
            existing_feedback = existing_feedback[:20]
            
            with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_feedback, f, indent=2, ensure_ascii=False)
                
            print(f"   ✅ Feedback Loop updated: {len(feedback_data.get('feedbacks', []))} new instructions.")
            return feedback_data
    except Exception as e:
        print(f"   ❌ Audit Error: {e}")
        return None

if __name__ == "__main__":
    audit_and_feedback()
