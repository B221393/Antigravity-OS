"""
EGO RELAY REPORTER (Terminal 3)
==================================
バケツリレー方式: 報告専門

役割:
- relay_result.json を監視
- 新しい結果があれば保存/報告
- EGO_STATUS.txt を更新
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
RESULT_FILE = os.path.join(DATA_DIR, "relay_result.json")
SHUKATSU_DIR = os.path.join(DATA_DIR, "shukatsu")
STATUS_FILE = os.path.join(BASE_DIR, "../../../../EGO_STATUS.txt")
REPORTED_FILE = os.path.join(DATA_DIR, "relay_reported.json")

os.makedirs(SHUKATSU_DIR, exist_ok=True)

def load_result():
    if os.path.exists(RESULT_FILE):
        try:
            with open(RESULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"results": [], "last_updated": ""}

def load_reported():
    if os.path.exists(REPORTED_FILE):
        try:
            with open(REPORTED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            pass
    return set()

def save_reported(ids):
    with open(REPORTED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids)[-500:], f)

def save_to_shukatsu(item):
    """個別ファイルとして保存"""
    filename = f"relay_{int(time.time())}_{hash(item['link']) % 10000}.json"
    filepath = os.path.join(SHUKATSU_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2, ensure_ascii=False)
    return filename

def update_status(stats):
    """EGO_STATUS.txt を更新"""
    try:
        content = f"""EGO STATUS (Bucket Relay)
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== Relay Stats ===
Today Processed: {stats['today_count']}
High Priority: {stats['high_priority']}
Last Item: {stats['last_title'][:50]}...

Categories:
{stats['categories']}
"""
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"   ⚠️ Status更新失敗: {e}")

def process_results():
    """未報告の結果を処理"""
    result_data = load_result()
    reported = load_reported()
    
    new_items = []
    for item in result_data.get("results", []):
        if item["link"] not in reported:
            new_items.append(item)
    
    if not new_items:
        return 0
    
    stats = {
        "today_count": len(new_items),
        "high_priority": 0,
        "last_title": "",
        "categories": {}
    }
    
    for item in new_items:
        # 保存
        filename = save_to_shukatsu(item)
        reported.add(item["link"])
        
        # 統計
        analysis = item.get("analysis", {})
        priority = analysis.get("priority", 5)
        category = analysis.get("category", "未分類")
        
        if priority >= 7:
            stats["high_priority"] += 1
        
        if category not in stats["categories"]:
            stats["categories"][category] = 0
        stats["categories"][category] += 1
        
        stats["last_title"] = item["title"]
        
        print(f"   📊 保存: {item['title'][:30]}... → {filename}")
    
    # カテゴリを文字列化
    cat_str = "\n".join([f"  {k}: {v}件" for k, v in stats["categories"].items()])
    stats["categories"] = cat_str
    
    update_status(stats)
    save_reported(reported)
    
    return len(new_items)

def start_continuous():
    """連続報告モード"""
    CHECK_INTERVAL = 15  # 15秒ごとにチェック
    
    print("\n📊 RELAY REPORTER 開始 (バケツリレー: 報告担当)")
    print("   役割: relay_result.json → 保存/報告")
    print("   Ctrl+C で停止\n")
    
    while True:
        try:
            count = process_results()
            if count > 0:
                print(f"\n✅ {count}件を報告完了")
            else:
                print(f"⏳ 新規なし - {CHECK_INTERVAL}秒後に再チェック...")
            
            time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n👋 レポーター終了")
            break
        except Exception as e:
            print(f"❌ エラー: {e}")
            time.sleep(30)

if __name__ == "__main__":
    if "--once" in sys.argv:
        process_results()
    else:
        start_continuous()
