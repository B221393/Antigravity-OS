"""
EGO DEEP KNOWLEDGE COLLECTOR
================================
一つのトピックについて「本の1章」レベルで詳細に収集

【構造】各エントリは以下の小見出しを持つ：
1. タイトル (title)
2. 概要 (overview) - 3文程度
3. 背景・歴史 (background)
4. 主要ポイント (main_points) - 5つ
5. 具体例・事例 (examples)
6. 関連トピック (related_topics)
7. 出典 (sources)
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
from dotenv import load_dotenv

# === パス設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../../../.env"))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEEP_KNOWLEDGE_FILE = os.path.join(DATA_DIR, "deep_knowledge.json")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_deep.json")
DISCOVERY_QUEUE = os.path.join(DATA_DIR, "discovery_queue.json")
DISCOVERY_LOG = os.path.join(DATA_DIR, "discovery_log.json")

os.makedirs(DATA_DIR, exist_ok=True)

# === LLM（統合クライアント：Gemini → Groq → Ollama） ===
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))
try:
    from modules.unified_llm_client import ask_llm, get_available_providers
    providers = get_available_providers()
    if providers:
        HAS_LLM = True
        print(f"[LLM] Available: {', '.join(providers)}")
    else:
        HAS_LLM = False
        print("[LLM] No providers available - will use basic mode")
except Exception as e:
    HAS_LLM = False
    print(f"[WARN] LLM not available ({e}). Will save raw data only.")

# ============================================================
# 【重要】本の1章レベルの構造
# ============================================================
CHAPTER_SCHEMA = {
    "id": "",
    "title": "",              # 章タイトル（20文字）
    "category": "",           # 分類
    "overview": "",           # 概要（100文字）
    "background": "",         # 背景・歴史（150文字）
    "main_points": [],        # 主要ポイント（5つ、各50文字）
    "examples": [],           # 具体例（2-3つ）
    "related_topics": [],     # 関連トピック
    "sources": [],            # 出典URL
    "created_at": "",
    "word_count": 0           # 総文字数
}

# ============================================================
# 【品質閾値】文字数が少なすぎる章は保存しない
# ============================================================
MIN_CHAPTER_CHARS = 2000  # 最低2000文字必須（これ以下は「Geminiにコピペで聞いた方がマシ」）

# ============================================================
# 【ソース】深い知識を得られるソース
# ============================================================
DEEP_SOURCES = [
    # Wikipedia (詳細な記事)
    ("Wikipedia Featured", "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=featured&feedformat=atom"),
    
    # 学術・科学
    ("arXiv CS", "https://rss.arxiv.org/rss/cs"),
    ("arXiv Physics", "https://rss.arxiv.org/rss/physics"),
    ("Nature News", "https://www.nature.com/nature.rss"),
    ("Science Daily", "https://www.sciencedaily.com/rss/all.xml"),
    
    # 深い解説
    ("Aeon Essays", "https://aeon.co/feed.rss"),
    ("Stanford Encyclopedia", "https://plato.stanford.edu/rss/sep.xml"),
    ("Brain Pickings", "https://www.themarginalian.org/feed/"),
    
    # 技術
    ("ACM TechNews", "https://technews.acm.org/rss.rss"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
]

def load_knowledge():
    if os.path.exists(DEEP_KNOWLEDGE_FILE):
        try:
            with open(DEEP_KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"chapters": [], "stats": {"total": 0, "total_words": 0}}

def save_knowledge(kb):
    kb["stats"]["total"] = len(kb["chapters"])
    kb["stats"]["total_words"] = sum(c.get("word_count", 0) for c in kb["chapters"])
    with open(DEEP_KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

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
        json.dump(list(ids)[-300:], f)

def get_title_hash(title):
    normalized = re.sub(r'[^\w]', '', title.lower())[:30]
    return hashlib.md5(normalized.encode()).hexdigest()[:10]

def is_duplicate(kb, new_title):
    new_hash = get_title_hash(new_title)
    for ch in kb["chapters"]:
        if get_title_hash(ch.get("title", "")) == new_hash:
            return True
    return False

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            return ET.fromstring(response.read())
    except:
        return None

def extract_items(root):
    items = []
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        desc = item.findtext('description', '')[:500]
        if title and link:
            items.append({"title": title, "link": link, "desc": desc})
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = entry.findtext('{http://www.w3.org/2005/Atom}title', '')
        link_el = entry.find('{http://www.w3.org/2005/Atom}link')
        link = link_el.attrib.get('href', '') if link_el is not None else ''
        desc = entry.findtext('{http://www.w3.org/2005/Atom}summary', '')[:500]
        if title and link:
            items.append({"title": title, "link": link, "desc": desc})
    return items[:3]

def create_deep_chapter(raw_title, raw_desc, source_url, source_name):
    """
    【核心】一つのトピックを「本の1章」レベルに展開
    目標: 1万文字レベルの詳細な内容
    """
    if not HAS_LLM:
        # LLMなしの簡易版
        return {
            "id": f"ch_{int(time.time())}",
            "title": raw_title[:20],
            "category": "General",
            "overview": raw_desc[:100] if raw_desc else raw_title,
            "background": "",
            "main_points": [raw_desc[:50]] if raw_desc else [],
            "examples": [],
            "related_topics": [],
            "sources": [source_url],
            "created_at": datetime.now().isoformat(),
            "word_count": len(raw_desc) if raw_desc else 0
        }
    
    # ===== 【新機能】複数回のLLM呼び出しで段階的に詳細化 =====
    
    # Step 1: 基本構造を作成
    prompt_structure = f"""あなたは百科事典の編集最高責任者です。以下のトピックについて、専門書1冊の「章」に匹敵する、極めて網羅的で詳細な構造（8-10セクション）を設計してください。

【トピック】
タイトル: {raw_title}
概要: {raw_desc}

【出力】JSONのみ
{{
  "title": "日本語タイトル（最先端かつ包括的な名称）",
  "category": "科学/歴史/技術/哲学/経済/文化/社会/芸術/キャリア",
  "sections": [
    "第1節: 概念の定義と哲学的・技術的本質",
    "第2節: 黎明期から現代に至る歴史的変遷と重要事象",
    "第3節: 核心となる理論体系とメカニズムの深層",
    "第4節: グローバルな視点での市場・社会への影響分析",
    "第5節: 具体的かつ広範な応用事例と産業界の動向",
    "第6節: 専門家間の論争、批判的視点、および倫理的課題",
    "第7節: 2027年以降を見据えた将来展望と革新的トレンド",
    "第8節: 関連分野との学際的接続と相乗効果",
    "第9節: 実装・活用における具体的な戦略とロードマップ",
    "第10節: 総括：AI時代のパラダイムシフトにおける位置付け"
  ]
}}

ルール: 英語なら日本語に翻訳。JSONのみ出力。"""

    try:
        structure_result = ask_llm(prompt_structure)
        if "```json" in structure_result:
            structure_result = structure_result.split("```json")[1].split("```")[0]
        start = structure_result.find('{')
        end = structure_result.rfind('}') + 1
        if start != -1 and end > start:
            structure = json.loads(structure_result[start:end])
        else:
            raise Exception("No JSON found")
    except Exception as e:
        print(f"  [Structure Error] {e}")
        structure = {
            "title": raw_title[:20],
            "category": "General",
            "sections": ["導入", "背景", "詳細", "例", "まとめ"]
        }
    
    sections_content = {}
    for i, section_title in enumerate(structure.get("sections", [])[:10], 1):
        prompt_section = f"""あなたは大学教授レベルの高度な知識を持つ百科事典執筆者です。以下のセクションを、学術論文や専門書の1項に相当する**圧倒的な情報量**で執筆してください。

【章タイトル】{structure.get('title', raw_title)}
【セクション】{section_title}
【参考情報】{raw_desc[:500]}

【出力ルール】
- この1セクションだけで**1500〜2500文字**を目標に、徹底的に詳しく書いてください。
- 専門用語、具体的なデータ、歴史的固有名詞、複雑な内部構造、社会的な反響、詳細なメカニズムを網羅してください。
- 箇条書きを多用せず、深い考察を含む重厚な文章スタイルにしてください。
- **文字数制限はありません。多ければ多いほど高く評価されます。**
- 日本語で執筆し、説明文（「以下に述べます」等）は一切省き、本文のみを出力してください。
- 27卒などのキャリア視点が含まれる場合は、その戦略的意義についても詳しく触れてください。"""

        try:
            section_content = ask_llm(prompt_section)
            # クリーンアップ（文字数制限を撤廃）
            section_content = section_content.replace("```", "").strip()
            sections_content[section_title] = section_content  # 制限なし
            print(f"    ✓ {section_title[:20]}... ({len(section_content)}文字)")
        except Exception as e:
            print(f"    ✗ {section_title}: {e}")
            sections_content[section_title] = f"{section_title}の内容（詳細は今後追加予定）"
    
    # Step 3: 要点・例・関連トピックを抽出
    prompt_meta = f"""以下の章から、要点・具体例・関連トピックを抽出してください。

【章タイトル】{structure.get('title')}
【内容サンプル】{str(sections_content)[:500]}

【出力】JSONのみ
{{
  "main_points": ["要点1（50文字）", "要点2", "要点3", "要点4", "要点5"],
  "examples": ["具体例1（30文字）", "具体例2", "具体例3"],
  "related_topics": ["関連1", "関連2", "関連3", "関連4"]
}}"""

    try:
        meta_result = ask_llm(prompt_meta)
        if "```json" in meta_result:
            meta_result = meta_result.split("```json")[1].split("```")[0]
        start = meta_result.find('{')
        end = meta_result.rfind('}') + 1
        if start != -1 and end > start:
            meta = json.loads(meta_result[start:end])
        else:
            raise Exception("No JSON")
    except Exception as e:
        print(f"  [Meta Error] {e}")
        meta = {
            "main_points": ["（要点抽出中）"],
            "examples": ["（例抽出中）"],
            "related_topics": ["（関連トピック抽出中）"]
        }
    
    # 最終的な章データを構築
    full_content = "\n\n".join([f"## {title}\n{content}" for title, content in sections_content.items()])
    
    chapter = {
        "id": f"ch_{int(time.time())}_{random.randint(1000,9999)}",
        "title": structure.get("title", raw_title[:20]),
        "category": structure.get("category", "General"),
        "overview": list(sections_content.values())[0][:150] if sections_content else raw_desc[:150],
        "background": list(sections_content.values())[1][:200] if len(sections_content) > 1 else "",
        "sections": structure.get("sections", []),
        "sections_content": sections_content,
        "full_text": full_content,
        "main_points": meta.get("main_points", [])[:5],
        "examples": meta.get("examples", [])[:3],
        "related_topics": meta.get("related_topics", [])[:5],
        "sources": [source_url],
        "created_at": datetime.now().isoformat(),
        "word_count": len(full_content)
    }
    
    return chapter

    save_knowledge(kb)
    save_processed(processed)
    
    total_words = sum(c.get("word_count", 0) for c in kb["chapters"])
    avg_words = total_words // len(kb["chapters"]) if kb["chapters"] else 0
    
    print(f"\n{'='*55}")
    print(f"✅ 完了: {new_count}章追加")
    print(f"   総章数: {len(kb['chapters'])}")
    print(f"   総文字数: {total_words:,}文字")
    print(f"   平均: {avg_words:,}文字/章")
    print(f"{'='*55}")
    
    return new_count

def check_discovery_queue():
    """Discovery Queueから未処理のキーワードを取得"""
    if not os.path.exists(DISCOVERY_QUEUE):
        return None
    
    try:
        with open(DISCOVERY_QUEUE, "r", encoding="utf-8") as f:
            queue = json.load(f)
        
        pending = [i for i in queue if i.get("status") == "pending"]
        if pending:
            return pending[0]
    except:
        pass
    return None

def mark_discovery_as_done(item):
    """キーワードを処理済みとしてマーク"""
    try:
        # Load Queue
        with open(DISCOVERY_QUEUE, "r", encoding="utf-8") as f:
            queue = json.load(f)
        
        # Update status
        for q in queue:
            if q["keyword"] == item["keyword"]:
                q["status"] = "done"
                q["processed_at"] = datetime.now().isoformat()
        
        # Save Queue
        with open(DISCOVERY_QUEUE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
            
        # Append to Log
        log = []
        if os.path.exists(DISCOVERY_LOG):
            with open(DISCOVERY_LOG, "r", encoding="utf-8") as f:
                log = json.load(f)
        
        log.append(item)
        with open(DISCOVERY_LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"  [Discovery Log Error] {e}")

def do_deep_patrol():
    """深いナレッジ収集パトロール (Discovery Queue優先)"""
    print("\n" + "="*55)
    print("📖 EGO Deep Knowledge Collector")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("   Mode: Book Chapter Level (10,000+ chars)")
    print("="*55)
    
    # --- Discovery Engine の実行 ---
    try:
        print("\n🔍 ニュースから新しい概念を探索中...")
        from discovery_engine import run_discovery
        run_discovery()
    except Exception as e:
        print(f"  [Discovery Engine Error] {e}")

    kb = load_knowledge()
    processed = load_processed()
    new_count = 0

    # 1. Discovery Queueのチェック
    discovery_item = check_discovery_queue()
    if discovery_item:
        kw = discovery_item["keyword"]
        print(f"\n🌟 [Discovery Target Found] {kw} を深掘りします...")
        
        chapter = create_deep_chapter(
            kw,
            f"発見された新概念: {discovery_item.get('reason', '')} (文脈: {discovery_item.get('context_brief', '')})",
            "EGO Discovery Engine",
            "Discovery Engine"
        )
        
        if chapter:
            wc = chapter.get('word_count', 0)
            if wc < MIN_CHAPTER_CHARS:
                print(f"   ⚠️ [品質不足] {kw} ({wc:,}文字 < {MIN_CHAPTER_CHARS:,}文字閾値) - 保存スキップ")
            else:
                kb["chapters"].append(chapter)
                mark_discovery_as_done(discovery_item)
                new_count += 1
                print(f"   ✅ [Discovery Done] {kw} ({wc:,}文字)")
            
    # 2. まだ新規追加があればRSSも回す（予備的な発見のため）
    if new_count == 0:
        sources = list(DEEP_SOURCES)
        random.shuffle(sources)
        
        for source_name, source_url in sources[:2]:  # 1回で2ソース
            print(f"\n📡 {source_name}...")
            
            root = fetch_rss(source_url)
            if root is None:
                print("   [SKIP] Fetch failed")
                continue
            
            items = extract_items(root)
            print(f"   Found {len(items)} items")
            
            for item in items:
                if item["link"] in processed:
                    continue
                
                if is_duplicate(kb, item["title"]):
                    print(f"   [DUP] {item['title'][:30]}...")
                    processed.add(item["link"])
                    continue
                
                print(f"\n   📝 Processing: {item['title'][:40]}...")
                print(f"   ⏳ Generating detailed chapter (this may take 1-2 min)...")
                
                chapter = create_deep_chapter(
                    item["title"],
                    item["desc"],
                    item["link"],
                    source_name
                )
                
                if chapter:
                    wc = chapter.get("word_count", 0)
                    if wc < MIN_CHAPTER_CHARS:
                        print(f"   ⚠️ [品質不足] {chapter.get('title', '')[:20]} ({wc:,}文字 < {MIN_CHAPTER_CHARS:,}文字閾値) - 保存スキップ")
                        processed.add(item["link"])  # 再処理防止
                    else:
                        kb["chapters"].append(chapter)
                        processed.add(item["link"])
                        new_count += 1
                        print(f"   ✅ [{chapter.get('category', '?')}] {chapter.get('title', '')} ({wc:,}文字)")
                    
                    if new_count >= 1:  # 1回で1章（30分で1冊）
                        break
            
            if new_count >= 1:
                break
    
    save_knowledge(kb)
    save_processed(processed)

    # --- Uzuki Bridge (Intel Reporter) への報告 ---
    try:
        from intel_reporter import update_bridge
        update_bridge()
    except Exception as e:
        print(f"  [Bridge Error] {e}")
    
    total_words = sum(c.get("word_count", 0) for c in kb["chapters"])
    avg_words = total_words // len(kb["chapters"]) if kb["chapters"] else 0
    
    print(f"\n{'='*55}")
    print(f"✅ 完了: {new_count}章追加")
    print(f"   総章数: {len(kb['chapters'])}")
    print(f"   総文字数: {total_words:,}文字")
    print(f"   平均: {avg_words:,}文字/章")
    print(f"{'='*55}")
    
    return new_count

def start_continuous():
    INTERVAL = 30 * 60  # 30分（1章 = 1冊レベル）
    print("🔄 Continuous Mode (30min = 1 Book)")
    print("   Ctrl+C to stop\n")
    
    while True:
        try:
            do_deep_patrol()
            print(f"\n⏰ Next book in 30 min...")
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\n👋 Stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(120)

if __name__ == "__main__":
    if "--continuous" in sys.argv:
        start_continuous()
    else:
        do_deep_patrol()
