"""
VECTIS KNOWLEDGE COLLECTOR (Wikipedia Style)
=============================================
構造化されたナレッジを収集するシステム

【設計思想】
- 各エントリは「小見出し」が決まっている（Wikipedia記事のように）
- 重複チェックはタイトルの類似度で行う
- 英語ソースも日本語に翻訳して統一
- 簡潔に、1エントリ = 1トピック
"""

import os
import sys
import json
import time
import random
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import hashlib

# === パス設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_knowledge.json")

os.makedirs(DATA_DIR, exist_ok=True)

# === LLM ===
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))
try:
    from modules.ollama_smart_selector import ask_ollama
    HAS_LLM = True
except:
    HAS_LLM = False
    print("[WARN] LLM not available")

# ============================================================
# 【重要】各ナレッジの構造（小見出し）を定義
# ============================================================
KNOWLEDGE_SCHEMA = {
    "title": "",          # タイトル（20文字以内）
    "category": "",       # カテゴリ（科学/歴史/技術/文化/経済/哲学/雑学）
    "definition": "",     # 定義（1文、50文字以内）
    "key_points": [],     # 要点（3つまで、各20文字以内）
    "source_url": "",     # 出典URL
    "collected_at": ""    # 収集日時
}

# ============================================================
# 【ソース】信頼できる知識ソース
# ============================================================
KNOWLEDGE_SOURCES = [
    # Wikipedia - 今日の記事/おすすめ
    ("Wikipedia Featured", "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=featured&feedformat=atom"),
    ("Wikipedia OnThisDay", "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=onthisday&feedformat=atom"),
    
    # Reddit TIL (Today I Learned)
    ("Reddit TIL", "https://www.reddit.com/r/todayilearned/.rss"),
    
    # Science
    ("Science Daily", "https://www.sciencedaily.com/rss/all.xml"),
    ("Phys.org", "https://phys.org/rss-feed/"),
    
    # Tech
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    
    # General Knowledge
    ("Mental Floss", "https://www.mentalfloss.com/feed"),
    ("Smithsonian", "https://www.smithsonianmag.com/rss/latest_articles/"),
]

def load_knowledge_base():
    """既存のナレッジベースを読み込む"""
    if os.path.exists(KNOWLEDGE_FILE):
        try:
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"entries": [], "stats": {"total": 0, "by_category": {}}}

def save_knowledge_base(kb):
    """ナレッジベースを保存"""
    kb["stats"]["total"] = len(kb["entries"])
    # カテゴリ別集計
    cat_count = {}
    for e in kb["entries"]:
        cat = e.get("category", "その他")
        cat_count[cat] = cat_count.get(cat, 0) + 1
    kb["stats"]["by_category"] = cat_count
    
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

def load_processed():
    """処理済みURLを読み込む"""
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            pass
    return set()

def save_processed(ids):
    """処理済みURLを保存（最新500件のみ）"""
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids)[-500:], f)

def get_title_hash(title):
    """タイトルのハッシュ（重複検出用）"""
    # 正規化：小文字、空白削除、記号削除
    normalized = re.sub(r'[^\w]', '', title.lower())[:20]
    return hashlib.md5(normalized.encode()).hexdigest()[:8]

def is_duplicate(kb, new_title):
    """重複チェック（タイトル類似度）"""
    new_hash = get_title_hash(new_title)
    for entry in kb["entries"]:
        if get_title_hash(entry.get("title", "")) == new_hash:
            return True
    return False

def fetch_rss(url):
    """RSSフィードを取得"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return ET.fromstring(response.read())
    except Exception as e:
        return None

def extract_items_from_rss(root):
    """RSS/Atomからアイテム抽出"""
    items = []
    # RSS 2.0
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        desc = item.findtext('description', '')[:300]
        if title and link:
            items.append({"title": title, "link": link, "desc": desc})
    # Atom
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = entry.findtext('{http://www.w3.org/2005/Atom}title', '')
        link_el = entry.find('{http://www.w3.org/2005/Atom}link')
        link = link_el.attrib.get('href', '') if link_el is not None else ''
        desc = entry.findtext('{http://www.w3.org/2005/Atom}summary', '')[:300]
        if title and link:
            items.append({"title": title, "link": link, "desc": desc})
    return items[:5]  # 各ソース最大5件

def structure_knowledge(raw_title, raw_desc, source_url, source_name):
    """
    【核心】生データを構造化されたナレッジに変換
    LLMを使って、決まったフォーマットに整形
    """
    if not HAS_LLM:
        # LLMなしの場合は簡易処理
        return {
            "title": raw_title[:20],
            "category": "雑学",
            "definition": raw_desc[:50] if raw_desc else raw_title[:50],
            "key_points": [],
            "source_url": source_url,
            "collected_at": datetime.now().isoformat()
        }
    
    prompt = f"""以下の情報を、簡潔な「ナレッジカード」に変換してください。

【入力】
タイトル: {raw_title}
概要: {raw_desc}
ソース: {source_name}

【出力形式】JSONのみ（説明不要）
{{
  "title": "日本語タイトル（15文字以内）",
  "category": "科学/歴史/技術/文化/経済/哲学/雑学のどれか",
  "definition": "1文で定義（40文字以内）",
  "key_points": ["要点1（15文字）", "要点2", "要点3"]
}}

ルール:
- 英語の場合は日本語に翻訳
- 必ず上記のJSON形式のみを出力"""

    try:
        result = ask_ollama(prompt)
        # JSON抽出
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        json_match = re.search(r'\{[^{}]*\}', result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            data["source_url"] = source_url
            data["collected_at"] = datetime.now().isoformat()
            return data
    except Exception as e:
        print(f"  [Parse Error] {e}")
    
    return None

def do_knowledge_patrol():
    """ナレッジ収集パトロール"""
    print("\n" + "="*50)
    print("📚 VECTIS Knowledge Collector")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    kb = load_knowledge_base()
    processed = load_processed()
    new_count = 0
    
    # ソースをシャッフル
    sources = list(KNOWLEDGE_SOURCES)
    random.shuffle(sources)
    
    for source_name, source_url in sources[:3]:  # 1回のパトロールで3ソース
        print(f"\n📡 {source_name}...")
        
        root = fetch_rss(source_url)
        if root is None:
            print("   [SKIP] Fetch failed")
            continue
        
        items = extract_items_from_rss(root)
        print(f"   Found {len(items)} items")
        
        for item in items:
            # 処理済みチェック
            if item["link"] in processed:
                continue
            
            # 重複チェック
            if is_duplicate(kb, item["title"]):
                print(f"   [DUP] {item['title'][:25]}...")
                processed.add(item["link"])
                continue
            
            # 構造化
            knowledge = structure_knowledge(
                item["title"], 
                item["desc"], 
                item["link"],
                source_name
            )
            
            if knowledge:
                kb["entries"].append(knowledge)
                processed.add(item["link"])
                new_count += 1
                print(f"   ✅ [{knowledge.get('category', '?')}] {knowledge.get('title', '')}")
                
                if new_count >= 5:  # 1回のパトロールで最大5件
                    break
        
        if new_count >= 5:
            break
    
    save_knowledge_base(kb)
    save_processed(processed)
    
    print(f"\n✅ 完了: {new_count}件追加 (総数: {len(kb['entries'])})")
    return new_count

def start_continuous():
    """連続パトロール"""
    INTERVAL = 30 * 60  # 30分
    print("🔄 Continuous Mode (30min interval)")
    print("   Ctrl+C to stop\n")
    
    while True:
        try:
            do_knowledge_patrol()
            print(f"\n⏰ Next patrol in 30 min...")
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\n👋 Stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    if "--continuous" in sys.argv:
        start_continuous()
    else:
        do_knowledge_patrol()
