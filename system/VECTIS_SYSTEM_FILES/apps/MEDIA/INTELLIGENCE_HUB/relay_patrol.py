"""
EGO RELAY PATROL (Terminal 1)
================================
バケツリレー方式: 収集専門

役割:
- RSSから情報を収集
- relay_queue.json に書き込み
- AI分析はしない（次のプロセスに任せる）
"""

import os
import sys
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import html
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
QUEUE_FILE = os.path.join(DATA_DIR, "relay_queue.json")
PROCESSED_FILE = os.path.join(DATA_DIR, "relay_patrol_processed.json")

# 収集ソース（シンプル版）
SOURCES = [
    ("就活ニュース", "https://news.google.com/rss/search?q=%E5%B0%B1%E6%B4%BB+2027&hl=ja&gl=JP&ceid=JP:ja"),
    ("Tech News", "https://news.google.com/rss/search?q=AI+technology&hl=ja&gl=JP&ceid=JP:ja"),
    ("企業採用", "https://news.google.com/rss/search?q=%E6%8E%A1%E7%94%A8+%E6%96%B0%E5%8D%92&hl=ja&gl=JP&ceid=JP:ja"),
]

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

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            pass
    return set()

def save_processed(ids):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids)[-500:], f)

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return ET.fromstring(response.read())
    except:
        return None

def extract_items(root):
    items = []
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        desc = item.findtext('description', '')[:300]
        if title and link:
            items.append({
                "title": html.unescape(title),
                "link": link,
                "summary": html.unescape(re.sub('<[^<]+?>', '', desc)),
                "collected_at": datetime.now().isoformat()
            })
    return items[:5]  # 各ソースから最大5件

def do_patrol_cycle():
    """1サイクル: 全ソースを回って収集"""
    print(f"\n{'='*50}")
    print(f"📰 RELAY PATROL - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    queue_data = load_queue()
    processed = load_processed()
    new_count = 0
    
    for name, url in SOURCES:
        print(f"\n🔍 {name}...")
        root = fetch_rss(url)
        if root is None:
            print("   ❌ 取得失敗")
            continue
        
        items = extract_items(root)
        for item in items:
            if item["link"] in processed:
                continue
            
            # キューに追加
            queue_data["queue"].append(item)
            processed.add(item["link"])
            new_count += 1
            print(f"   ✅ {item['title'][:40]}...")
    
    save_queue(queue_data)
    save_processed(processed)
    
    print(f"\n📦 キューに {new_count} 件追加 (総数: {len(queue_data['queue'])})")
    return new_count

def start_continuous():
    """連続パトロールモード"""
    INTERVAL = 60  # 60秒ごと
    
    print("\n🔄 RELAY PATROL 開始 (バケツリレー: 収集担当)")
    print("   役割: 情報収集 → relay_queue.json へ手渡し")
    print("   Ctrl+C で停止\n")
    
    while True:
        try:
            do_patrol_cycle()
            print(f"\n☕ {INTERVAL}秒休憩...")
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\n👋 パトロール終了")
            break
        except Exception as e:
            print(f"❌ エラー: {e}")
            time.sleep(30)

if __name__ == "__main__":
    if "--once" in sys.argv:
        do_patrol_cycle()
    else:
        start_continuous()
