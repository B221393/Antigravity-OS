"""
EGO RELAY ANALYZER (Terminal 2)
==================================
バケツリレー方式: 分析専門

役割:
- relay_queue.json を監視
- 新しいアイテムがあればAI分析
- 結果を relay_result.json に書き込み
"""

import os
import sys
import json
import time
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
QUEUE_FILE = os.path.join(DATA_DIR, "relay_queue.json")
RESULT_FILE = os.path.join(DATA_DIR, "relay_result.json")

# LLM読み込み
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, "../../../.env"))

try:
    from modules.unified_llm_client import ask_llm, get_available_providers
    providers = get_available_providers()
    HAS_LLM = bool(providers)
    if HAS_LLM:
        print(f"[LLM] Available: {', '.join(providers)}")
except:
    HAS_LLM = False
    print("[WARN] LLM not available")

def load_queue():
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"queue": [], "last_updated": ""}

def save_queue(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_result():
    if os.path.exists(RESULT_FILE):
        try:
            with open(RESULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"results": [], "last_updated": ""}

def save_result(data):
    data["last_updated"] = datetime.now().isoformat()
    # 最新100件のみ保持
    data["results"] = data["results"][-100:]
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def analyze_item(item):
    """AIでアイテムを分析"""
    if not HAS_LLM:
        return {
            "priority": 5,
            "category": "未分類",
            "insight": "LLMなしのため分析スキップ",
            "action": "手動確認"
        }
    
    prompt = f"""以下のニュース/情報を27卒就活生の視点で分析してください。

タイトル: {item['title']}
概要: {item.get('summary', '')}

JSONで回答:
{{
  "priority": 1-10の重要度,
  "category": "就活/企業/技術/教養/その他",
  "insight": "50文字で核心を一言",
  "action": "次のアクション提案(20文字)"
}}
"""
    try:
        result = ask_llm(prompt)
        # JSONを抽出
        if "{" in result and "}" in result:
            start = result.find("{")
            end = result.rfind("}") + 1
            return json.loads(result[start:end])
    except Exception as e:
        print(f"   ⚠️ 分析エラー: {e}")
    
    return {
        "priority": 5,
        "category": "未分類",
        "insight": "分析失敗",
        "action": "手動確認"
    }

def process_one_item():
    """キューから1件取り出して分析"""
    queue_data = load_queue()
    
    if not queue_data["queue"]:
        return None
    
    # 1件取り出し
    item = queue_data["queue"].pop(0)
    save_queue(queue_data)
    
    print(f"\n🧠 分析中: {item['title'][:40]}...")
    
    # AI分析
    analysis = analyze_item(item)
    
    # 結果を保存
    result_data = load_result()
    result_data["results"].append({
        **item,
        "analysis": analysis,
        "analyzed_at": datetime.now().isoformat()
    })
    save_result(result_data)
    
    print(f"   ✅ 優先度: {analysis['priority']} | {analysis['category']}")
    print(f"   💡 {analysis['insight']}")
    
    return item

def start_continuous():
    """連続分析モード"""
    CHECK_INTERVAL = 10  # 10秒ごとにキューをチェック
    REST_AFTER_ANALYSIS = 30  # 分析後30秒休憩
    
    print("\n🧠 RELAY ANALYZER 開始 (バケツリレー: 分析担当)")
    print("   役割: relay_queue.json → AI分析 → relay_result.json へ手渡し")
    print("   Ctrl+C で停止\n")
    
    while True:
        try:
            queue_data = load_queue()
            queue_len = len(queue_data.get("queue", []))
            
            if queue_len > 0:
                print(f"\n📥 キューに {queue_len} 件あり")
                item = process_one_item()
                if item:
                    print(f"\n☕ {REST_AFTER_ANALYSIS}秒休憩...")
                    time.sleep(REST_AFTER_ANALYSIS)
            else:
                print(f"⏳ キュー空 - {CHECK_INTERVAL}秒後に再チェック...")
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n👋 アナライザー終了")
            break
        except Exception as e:
            print(f"❌ エラー: {e}")
            time.sleep(30)

if __name__ == "__main__":
    if "--once" in sys.argv:
        process_one_item()
    else:
        start_continuous()
