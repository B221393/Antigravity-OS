import json
import os
import sys

# Add modules directory to path
sys.path.append(r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES")
from modules.unified_llm_client import ask_llm_high_quality

CACHE_PATH = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data\kddi_intelligence_cache.json"
ES_PATH = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\CAREER\KDDI_ES_FINAL.md"

def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {"focus_areas": [], "intelligence_updates": []}
    with open(CACHE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_es_quality(new_text):
    """ESの品質と文字数制限をチェックする"""
    if not new_text or len(new_text) < 500: # 全文なのである程度の長さが必要
        return False, "出力が短すぎます。"
    
    # セクション分割して文字数チェック（簡易）
    if "## 設問 2" in new_text and "## 設問 3" in new_text:
        q2_start = new_text.find("## 設問 2")
        q3_start = new_text.find("## 設問 3")
        q3_end = new_text.find("## 🚀") if "## 🚀" in new_text else len(new_text)
        
        q2_content = new_text[q2_start:q3_start]
        # 文字数カウント（前後の余白と見出しを除く）
        q2_body = q2_content.split("**お答えください。（400文字以下）**")[-1].strip()
        q2_count = len(q2_body.split("（")[0].strip()) # （398文字）などを除外
        
        if q2_count > 410: # 10文字程度のバッファ
            return False, f"設問2が文字数オーバーです ({q2_count}文字)。"
            
    return True, "OK"

def refine_es():
    """RAG: キャッシュ情報に基づきESを自動推敲する"""
    print("🚀 Starting RAG Refinement (Secure Mode)...")
    
    with open(ES_PATH, 'r', encoding='utf-8') as f:
        es_text = f.read()
    
    cache = load_cache()
    intel = json.dumps(cache, ensure_ascii=False, indent=2)
    
    prompt = f"""
あなたはKDDIの採用官を唸らせる最強のキャリアアドバイザーです。
以下の「最新インテリジェンス」と「現在のES」を元に、ESの内容をさらにブラッシュアップしてください。

【最新インテリジェンス（KDDI動向）】
{intel}

【現在のES】
{es_text}

【制約条件】
1. 設問2は400文字以内、設問3は400〜500文字を厳守。
2. KDDIの「サテライト成長戦略」「Connected Experience」「内製化」「αU」といったキーワードを、文脈に合わせてより具体的に組み込んでください。
3. 出力は、Markdown形式の「ES全文」のみを返してください（解説は不要）。

修正後のESを出力してください：
"""
    
    # 高性能モデルのみを使用（Gemma等へのフォールバックは品質低下を招くため禁止）
    new_es = ask_llm_high_quality(prompt)
    
    if new_es:
        is_ok, msg = validate_es_quality(new_es)
        if is_ok:
            backup_path = ES_PATH + ".bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(es_text)
                
            with open(ES_PATH, 'w', encoding='utf-8') as f:
                f.write(new_es)
            print(f"✅ ES successfully updated. ({msg})")
        else:
            print(f"⚠️ Quality check failed: {msg} (Updates skipped to protect draft)")
    else:
        print("❌ High-quality LLM currently unavailable (Quota limit?). Skipping update.")

if __name__ == "__main__":
    refine_es()
