# EGO DISCOVERY ENGINE
# =======================
# universe.json の最新ログから「27卒就活」「先端概念」を抽出し、
# Deep Knowledge Collector のキューに追加する。

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# === パス設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../../../.env"))
DATA_DIR = os.path.join(BASE_DIR, "data")
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json")
DISCOVERY_QUEUE = os.path.join(DATA_DIR, "discovery_queue.json")
DISCOVERY_LOG = os.path.join(DATA_DIR, "discovery_log.json")

os.makedirs(DATA_DIR, exist_ok=True)

# === LLM 統合 ===
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))
try:
    from modules.unified_llm_client import ask_llm
    HAS_LLM = True
except:
    HAS_LLM = False

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

COLLECTION_MODES_FILE = os.path.join(BASE_DIR, "../../../config/collection_modes.json")

def get_active_mode():
    """現在の収集モード設定を読み込む"""
    data = load_json(COLLECTION_MODES_FILE, {"active_mode": "general", "modes": {}})
    active_key = data.get("active_mode", "general")
    mode_config = data.get("modes", {}).get(active_key, {})
    
    # デフォルト値補完
    if not mode_config:
        mode_config = {
            "name": "General", 
            "description": "General collection",
            "keywords": ["AI", "Technology", "Future"],
            "sources": ["General Web"]
        }
    
    return active_key, mode_config

def extract_discovery_targets():
    """universe.json から、現在のモードに基づいて深掘り対象を抽出"""
    if not HAS_LLM:
        print("[Discovery] No LLM available for extraction.")
        return []

    # モード情報の取得
    mode_key, mode_config = get_active_mode()
    print(f"[Discovery] Active Mode: {mode_config.get('name')} ({mode_key})")

    universe = load_json(UNIVERSE_FILE, {"nodes": []})
    nodes = universe.get("nodes", [])
    print(f"[Discovery] Total nodes in universe: {len(nodes)}")
    
    recent_nodes = nodes[-30:] # 直近30件
    
    if not recent_nodes:
        print("[Discovery] No nodes found in universe.json")
        return []

    # プロマイド作成
    context = ""
    for n in recent_nodes:
        context += f"- Title: {n.get('title')}\n  Summary: {n.get('summary')[:100]}...\n  Group: {n.get('group', 'General')}\n"

    # モードに応じたプロンプト構築
    prompt = f"""
あなたはEGO OSの「インテリジェンス・アナリスト」です。
現在、システムは**【{mode_config.get('name')}】**モードで稼働しています。

このモードの目的: {mode_config.get('description')}
優先キーワード: {', '.join(mode_config.get('keywords', []))}

以下の直近の知識（ニュース・YouTube情報の要約）から、
このモードの目的に合致し、かつ「百科事典として深掘りすべき価値があるトピック」を3つ抽出してください。

【コンテキスト（直近の知識）】
{context}

【抽出条件】
1. 現在のモード（{mode_config.get('name')}）に関連するトピックを最優先する。
2. そのトピックがなぜこのモードにおいて重要か（理由）を含める。
3. 日本語で、具体的かつ専門的なキーワードを選ぶ。

【出力形式】JSONのみ
[
  {{
    "keyword": "単語名",
    "reason": "選定理由（モードの文脈に沿って）",
    "context_brief": "どのような文脈で見つかったか"
  }},
  ...
]
"""
    
    print("[Discovery] Analyzing universe with mode-specific prompt...")
    try:
        result = ask_llm(prompt)
        if not result:
            print("[Discovery] LLM returned None.")
            return []
        
        # JSONクリーンアップ
        start = result.find('[')
        end = result.rfind(']') + 1
        if start != -1 and end > start:
            json_str = result[start:end]
            targets = json.loads(json_str)
            return targets
        else:
            print("[Discovery] No JSON array found in response.")
    except Exception as e:
        print(f"[Discovery] extraction failed: {e}")
    
    return []

def run_discovery():
    mode_key, mode_config = get_active_mode()
    print(f"\n{'='*60}")
    print(f"🌟 EGO Discovery Engine Running... [MODE: {mode_config.get('name')}]")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    targets = extract_discovery_targets()
    if not targets:
        print("   No new targets discovered.")
        return

    # 構造がリストか辞書かで処理を分ける（前回のエラー対策）
    queue_data = load_json(DISCOVERY_QUEUE, {"queue": []})
    if isinstance(queue_data, list): # 古いフォーマットの場合
        queue_data = {"queue": queue_data}
    
    queue = queue_data.get("queue", [])
    log = load_json(DISCOVERY_LOG, [])
    
    processed_keywords = {item["keyword"] for item in log}
    queue_keywords = {item["keyword"] for item in queue}
    
    added_count = 0
    for t in targets:
        kw = t["keyword"]
        if kw not in processed_keywords and kw not in queue_keywords:
            print(f"   ✨ New Concept Discovered: {kw}")
            print(f"      Reason: {t['reason']}")
            queue.append({
                "keyword": kw,
                "reason": t["reason"],
                "context_brief": t["context_brief"],
                "status": "pending",
                "mode": mode_key, # モード情報を付与
                "discovered_at": datetime.now().isoformat()
            })
            added_count += 1
    
    if added_count > 0:
        save_json(DISCOVERY_QUEUE, {"queue": queue}) # 正しい辞書形式で保存
        print(f"\n✅ {added_count} items added to Discovery Queue.")
    else:
        print("\n🤙 All discovered concepts are already in queue or processed.")

if __name__ == "__main__":
    run_discovery()
