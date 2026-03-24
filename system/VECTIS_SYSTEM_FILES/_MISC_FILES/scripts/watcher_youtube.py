import time
import os
import sys
import re
import urllib.request
import xml.etree.ElementTree as ET
import json
import requests
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import scrapetube
import random

# Setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
INPUT_FILE = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "AUTO_YOUTUBE.txt")
CHANNEL_LIST_FILE = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "MY_CHANNELS.txt")

# Output to VECTIS Memory
OUTPUT_DIR = os.path.join(BASE_DIR, "apps", "memory", "data", "youtube_notes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Add path for modules
sys.path.insert(0, BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Ollama API (Local - NO RATE LIMIT)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# スキップログ（リトライ用）
SKIP_LOG_FILE = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "skipped_videos.log")

def log_skipped(vid, title, reason):
    """スキップした動画をログに記録"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = f"{timestamp} | {reason} | {vid} | {title}\n"
    
    with open(SKIP_LOG_FILE, "a", encoding="utf-8", errors="replace") as f:
        f.write(log_entry)
    print(f"   📝 Logged to skipped_videos.log")

def ollama_generate(prompt):
    """Ollamaでテキスト生成（レート制限なし）"""
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }, timeout=120)
    return response.json().get("response", "")

# Gemini API Client (Fallback - for no-subtitle videos)
from modules.gemini_client import GenerativeModel
gemini_model = GenerativeModel('gemini-2.0-flash-exp')

# Filter Keywords
IGNORE_KEYWORDS = ["ゲーム", "Gameplay", "実況", "配信", "Live", "🔴", "歌ってみた", "Playthrough"]

# Error Telemetry
import subprocess
from modules.error_relay import ErrorRelay

# Rust Matcher Config
RUST_MATCHER_EXE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/rust_matcher/target/release/rust_matcher.exe"))
KEYWORDS_FILE = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "EXCLUDE_KEYWORDS.txt") # Assuming this is the file for keywords to check against

relay = ErrorRelay("Auto_Watcher")

print(f"👀 Watching: {INPUT_FILE}")
print(f"📂 Output: {OUTPUT_DIR}")
print("チャンネルURL、または動画URLを検出すると自動処理します...")

def set_title(status):
    try:
        # Sanitize for Windows command prompt title
        safe_status = status.replace("|", "-").replace("&", " and ").replace(">", "").replace("<", "")
        os.system(f"title [YouTube Watcher] {safe_status}")
    except Exception as e:
        relay.report(e, context="set_title")

def get_channel_id_from_url(url):
    """チャンネルURLからID (UC...) をスクレイピングで取得"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'channel_id=([a-zA-Z0-9_-]+)', html)
            if match: return match.group(1)
            match = re.search(r'"channelId":"([a-zA-Z0-9_-]+)"', html)
            if match: return match.group(1)
            if "/channel/" in url: return url.split("/channel/")[1].split("/")[0]
    except Exception as e:
        relay.report(e, context=f"get_channel_id_from_url: {url}")
    return None

# ... (skip get_channel_videos, add_keyword) ...

def load_discovered_entities():
    """発見済みエンティティ（人物・組織・概念）を読み込む"""
    entity_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "discovered_entities.json")
    if os.path.exists(entity_file):
        try:
            with open(entity_file, "r", encoding="utf-8", errors="replace") as f:
                return json.load(f)
        except Exception as e:
            relay.report(e, context="load_discovered_entities (resetting to empty)")
            return {}
    return {}

def get_channel_videos(channel_url):
    """チャンネルの最新動画を取得 (RSS使用 - 安定版)"""
    videos = []
    try:
        # RSSフィードはチャンネルIDが必要。URLからIDを特定する
        cid = None
        if "channel_id=" in channel_url:
            cid = channel_url.split("channel_id=")[1]
        elif "/channel/" in channel_url:
            cid = channel_url.split("/channel/")[1].split("/")[0]
        else:
            # IDではないURL (@userなど) の場合、IDをスクレイピングする
            cid = get_channel_id_from_url(channel_url)
            
        if not cid:
            print(f"⚠️ RSS用ID特定不可: {channel_url}")
            return []

        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
        with urllib.request.urlopen(rss_url) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                vid = entry.find('yt:videoId', ns).text
                title = entry.find('atom:title', ns).text
                videos.append((vid, title))
                
    except Exception as e:
        print(f"❌ 動画リスト取得エラー(RSS): {e}")
    return videos

def get_exclude_keywords():
    """除外キーワードを読み込む"""
    keywords = []
    exclude_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "EXCLUDE_KEYWORDS.txt")
    if os.path.exists(exclude_file):
        with open(exclude_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    keywords.append(line.lower())
    return keywords

def add_keyword(keyword):
    """新しいキーワードを自動追加（バリデーション付き）"""
    keyword_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "MY_KEYWORDS.txt")
    
    # ゴミキーワードを除外
    GARBAGE_PATTERNS = [
        "できません", "ください", "提供", "抽出", "要約", "動画の内容",
        "申し訳", "具体的", "情報", "不明", "空欄", "ルール"
    ]
    
    for pattern in GARBAGE_PATTERNS:
        if pattern in keyword:
            return  # ゴミなので追加しない
    
    # 短すぎる・長すぎるキーワードを除外
    if len(keyword) < 3 or len(keyword) > 30:
        return
    
    existing = get_my_keywords()
    if keyword not in existing:
        with open(keyword_file, "a", encoding="utf-8", errors="replace") as f:
            f.write(f"\n# Auto-discovered\n{keyword}")
        print(f"   🆕 New keyword added: {keyword}")

def load_discovered_entities():
    """発見済みエンティティ（人物・組織・概念）を読み込む"""
    entity_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "discovered_entities.json")
    if os.path.exists(entity_file):
        try:
            with open(entity_file, "r", encoding="utf-8", errors="replace") as f:
                return json.load(f)
        except Exception as e:
            relay.report(e, context="load_discovered_entities (resetting to empty)")
            return {}
    return {}

def save_discovered_entities(entities):
    """エンティティをJSONとCSVで保存"""
    entity_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "discovered_entities.json")
    csv_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "discovered_entities.csv")
    
    # JSON保存
    with open(entity_file, "w", encoding="utf-8", errors="replace") as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)
    
    # CSV保存（出現回数の多い順）
    import csv
    from datetime import datetime
    
    sorted_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)
    
    with open(csv_file, "w", encoding="utf-8-sig", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["エンティティ", "出現回数", "最終更新"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for entity, count in sorted_entities:
            writer.writerow([entity, count, timestamp])

def extract_new_keywords(summary_text):
    """要約から人物・組織・専門用語を抽出し、頻度を追跡"""
    
    # 既知の除外人物（話者自身など）
    KNOWN_HOSTS = ["安野", "堀江", "ひろゆき", "水野", "佐久間", "三宅"]
    
    prompt = f"""以下のYouTube要約から、**深掘りすべき重要人物・高次な概念**を抽出してください。
    
    【優先順位】
    1. **哲学者・思想家・小説家** (例: ニーチェ、ドストエフスキー、カフカ)
    2. **AI・技術の深層概念** (例: フレーム問題、中国語の部屋、AGI、意識)
    3. **ビジネス・経済の理論** (例: プロスペクト理論)
    
    【除外】
    - 政治家（特に日本の地方・国会議員はNG）
    - タレント、YouTuber
    - 一般的すぎる言葉（日本、経済、AIなど単語のみ）

要約:
{summary_text[:1500]}

1行に1つ、最大5つまで出力してください:
"""
    
    try:
        # Use Gemini if possible for better extraction, fallback to Ollama
        try:
            res = gemini_model.generate_content(prompt)
            response_text = res.text
        except:
             response_text = ollama_generate(prompt)
        
        entities = []
        for line in response_text.split('\n'):
            entity = line.strip().replace('-', '').replace('*', '').replace('・', '')
            
            # 除外チェック
            if not entity or len(entity) < 2:
                continue
            if any(host in entity for host in KNOWN_HOSTS):
                continue
            if entity in ['日本', 'アメリカ', '中国', '政府', '企業', '該当なし', '特になし', 'None', 'N/A']:
                continue
                
            entities.append(entity)
        
        # 頻度追跡
        discovered = load_discovered_entities()
        for entity in entities[:5]:  # 最大5個
            if entity in discovered:
                discovered[entity] += 1
            else:
                discovered[entity] = 1
        
        save_discovered_entities(discovered)
        
        # 頻度が3回以上のものを優先的にキーワード化
        for entity, count in discovered.items():
            if count >= 3:
                add_keyword(entity)
                print(f"   🔥 High-frequency entity ({count}x): {entity}")
        
        return entities[:3]
        
    except Exception as e:
        print(f"   ❌ Entity extraction error: {e}")
        return []

def process_video(vid, title="Unknown"):
    set_title(f"📝 要約中... {title[:20]}")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r'[\\/:*?"<>|]+', '', title)[:30]
    out_filename = f"YouTube_{safe_title}_{vid}.md"
    out_path = os.path.join(OUTPUT_DIR, out_filename)
    
    if os.path.exists(out_path):
        return f"⏭️ Skip (Already exists): {title}"

    print(f"🎬 Processing: {title} ({vid})...")
    
    try:
        # 1. yt-dlpで字幕を取得
        import subprocess
        import tempfile
        
        url = f"https://www.youtube.com/watch?v={vid}"
        
        # 一時ディレクトリに字幕をダウンロード
        with tempfile.TemporaryDirectory() as tmpdir:
            subtitle_path = os.path.join(tmpdir, "subtitle")
            
            # yt-dlpで自動生成字幕を取得
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-lang", "ja,en",
                "--sub-format", "vtt",
                "-o", subtitle_path,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 字幕ファイルを探す
            text = ""
            for ext in ['.ja.vtt', '.en.vtt', '.vtt']:
                vtt_file = subtitle_path + ext
                if os.path.exists(vtt_file):
                    with open(vtt_file, 'r', encoding='utf-8', errors='replace') as f:
                        raw = f.read()
                        # VTTからテキストだけ抽出
                        lines = []
                        for line in raw.split('\n'):
                            if not line.startswith('WEBVTT') and '-->' not in line and line.strip():
                                lines.append(line.strip())
                        text = ' '.join(lines)
                    break
            
            if not text or len(text) < 100:
                # 字幕がない場合、Geminiで直接処理（フォールバック）
                print(f"   📡 No subtitles, using Gemini fallback...")
                try:
                    gemini_prompt = f"""以下のYouTube動画を視聴し、内容を要約してください。

動画URL: {url}

以下の形式でMarkdown形式で出力してください:

## 📌 要点
- (箇条書きで主要なポイント)

## 💡 重要な洞察
- (興味深い発見や学び)

## 🎯 アクションアイテム
- (視聴者が実践できること)
"""
                    gemini_response = gemini_model.generate_content(gemini_prompt)
                    
                    content = f"""# 📺 {title}
URL: {url}
Date: {timestamp}

{gemini_response.text}

---
*Generated by VECTIS AI Agent (Gemini Fallback)*
"""
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return f"✅ Generated (Gemini): {out_filename}"
                    
                except Exception as gemini_error:
                    if "429" in str(gemini_error):
                        log_skipped(vid, title, "Gemini quota exceeded")
                        return f"⏭️ Gemini quota exceeded"
                    log_skipped(vid, title, f"Gemini error: {str(gemini_error)[:30]}")
                    return f"⚠️ Gemini error: {str(gemini_error)[:40]}"
            
            # 2. Groqで要約
            prompt = f"""以下のYouTube動画の字幕を要約してください。

動画タイトル: {title}
動画URL: {url}

字幕:
{text[:8000]}

**重要な指示:**
1. 内容が事実に基づいているか検証してください
2. 誤情報や誇張表現があれば指摘してください

以下の形式でMarkdown形式で出力してください:

## 📌 要点
- (箇条書きで主要なポイント)

## 💡 重要な洞察
- (興味深い発見や学び)

## ⚠️ ファクトチェック
- (事実確認の結果、誤情報や要注意点があれば記載)

## 🎯 アクションアイテム
- (視聴者が実践できること)
"""
            
            summary = ollama_generate(prompt)
            
            if not summary or len(summary) < 50:
                return f"⚠️ Ollama error: empty response"
            
            content = f"""# 📺 {title}
URL: {url}
Date: {timestamp}

{summary}

---
*Generated by VECTIS AI Agent (Ollama Local)*
"""
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # エンティティ抽出（Groqで）
            try:
                new_keywords = extract_new_keywords(summary)
                for kw in new_keywords:
                    add_keyword(kw)
                    # ★ FRACTAL SEEDING ★
                    # 抽出されたキーワードを探査キューに追加
                    explorer.add_seed(kw, source_context=f"Video: {title}")
                    
            except Exception as e:
                print(f"   ⚠️ Keyword extraction failed: {e}")
                
            return f"✅ Generated: {out_filename}"
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate" in error_str.lower():
            print(f"   ⏸️ Rate limit. Waiting 60s...")
            time.sleep(60)
            return f"⏳ Rate limit - retry later"
        if "timeout" in error_str.lower():
            return f"⏭️ Timeout"
        return f"⚠️ Error: {str(e)[:50]}"

def process_url(url):
    url = url.strip()
    if not url or "例:" in url or "https" not in url: return "Skipped invalid line"
    
    # Check if channel URL
    if "/@" in url or "/channel/" in url:
        print(f"📡 Channel URL Detected: {url}")
        videos = get_channel_videos(url)
        print(f"📋 Found {len(videos)} videos. Starting Process...")
        
        results = []
        count = 0
        for vid, title in videos:
            res = process_video(vid, title)
            print(f"[{count+1}/{len(videos)}] {res}")
            results.append(res)
            time.sleep(10)
            count += 1
        return f"✅ Channel Processing Complete ({count} videos processed)"
    
    else:
        # Normal Video URL
        vid = None
        query = urlparse(url)
        if query.hostname == 'youtu.be': vid = query.path[1:]
        elif query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch': vid = parse_qs(query.query)['v'][0]
        
        if vid:
            return process_video(vid, f"Video_{vid}")
        else:
            return f"❌ Invalid URL format: {url}"

def check_keywords(text):
    """Checks if text contains any keywords using Rust accelerator if available."""
    text_lower = text.lower()
    
    # Try Rust First
    if os.path.exists(RUST_MATCHER_EXE):
        try:
            cmd = [
                RUST_MATCHER_EXE,
                "--keywords", KEYWORDS_FILE,
                "--target", text
            ]
            # No window
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', startupinfo=si)
            out = res.stdout.strip()
            if out and out != "NO_MATCH":
                return out.split(",") # Return list of matched keywords
            elif out == "NO_MATCH":
                return []
        except Exception as e:
            print(f"Rust Matcher Failed: {e}, falling back to Python.")
    
    # Python Fallback
    matched = []
    # Assuming KEYWORDS is a global list or can be loaded here
    # For this example, let's use get_exclude_keywords() as the source for keywords
    KEYWORDS = get_exclude_keywords() 
    for kw in KEYWORDS:
        if kw.lower() in text_lower:
            matched.append(kw)
    return matched

def is_interesting(title):
    """動画が興味深いかチェック（除外フィルタ適用）"""
    title_lower = title.lower()
    
    # 基本の除外ワード
    for kw in IGNORE_KEYWORDS:
        if kw.lower() in title_lower:
            return False
    
    # ユーザー定義の除外ワード
    exclude_list = get_exclude_keywords()
    for kw in exclude_list:
        if kw in title_lower:
            return False
    
    return True

def get_my_keywords():
    """キーワードリストを読み込む"""
    keywords = []
    keyword_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "MY_KEYWORDS.txt")
    if os.path.exists(keyword_file):
        with open(keyword_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    keywords.append(line)
    return keywords

def search_youtube_by_keyword(keyword, limit=100):
    """キーワードでYouTube検索し、動画リストを取得"""
    videos = []
    try:
        print(f"   🔎 Searching YouTube for: '{keyword}'")
        search_gen = scrapetube.get_search(keyword)
        
        count = 0
        for video in search_gen:
            if count >= limit: break
            
            try:
                vid = video['videoId']
                title = video['title']['runs'][0]['text']
                
                # 再生回数を取得（存在する場合）
                view_count = 0
                if 'viewCountText' in video:
                    vct = video['viewCountText']
                    view_text = ""
                    if 'simpleText' in vct:
                        view_text = vct['simpleText']
                    elif 'runs' in vct:
                        view_text = vct['runs'][0]['text']
                    
                    # 数字だけ抽出（カンマ、スペース、文字を除去）
                    digits = ''.join(filter(str.isdigit, view_text))
                    if digits:
                        view_count = int(digits)
                
                videos.append((vid, title, view_count))
                count += 1
            except:
                continue
                
    except Exception as e:
        print(f"   ❌ Search error: {e}")
    
    # 再生回数でソート（降順）
    videos.sort(key=lambda x: x[2], reverse=True)
    return videos

def auto_patrol():
    """キーワード検索ベースの自動巡回（バッチ処理モード）"""
    keywords = get_my_keywords()
    if not keywords:
        print("📭 No keywords in MY_KEYWORDS.txt")
        return False
    
    # ランダムにキーワードを選択
    keyword = random.choice(keywords)
    set_title(f"🔍 検索中: {keyword}")
    
    print(f"🤖 Patrol: Searching for '{keyword}'...")
    videos = search_youtube_by_keyword(keyword, limit=100)
    
    if not videos:
        print("   💤 No videos found.")
        return False
    
    print(f"   📋 Found {len(videos)} videos. Processing all unprocessed...")
    
    processed_count = 0
    # 上位から全てチェック（再生回数順）
    for i, (vid, title, views) in enumerate(videos):
        # 再生回数フィルタ（1万回以上のみ）
        if views < 10000:
            continue
            
        if not is_interesting(title): continue
        
        safe_title = re.sub(r'[\\/:*?"<>|]+', '', title)[:30]
        fname = f"YouTube_{safe_title}_{vid}.md"
        path = os.path.join(OUTPUT_DIR, fname)
        
        if not os.path.exists(path):
            print(f"   🎯 [{i+1}/{len(videos)}] {title} ({views:,} views)")
            set_title(f"📝 要約中 [{processed_count+1}]: {title[:15]}...")
            res = process_video(vid, title)
            print(f"      {res}")
            if "✅" in res:
                processed_count += 1
            # 次の動画へすぐ進む（returnしない）
            time.sleep(5)  # API制限対策で少し待機
    
# ... (Previous code) ...
        return False

class FractalExplorer:
    """
    Knowledge Fractal Explorer
    ==========================
    動画などのソースから得られた「種（キーワード）」を基に、
    辞書の辞書の辞書のように、無限に知識を深掘りしていくエージェント。
    
    Structure:
    - Root: 動画の要約
    - Branch: 抽出されたキーワード/人物
    - Leaf: 検索・深掘りされたWiki/K-Card
    """
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.explored_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "explored_terms.json")
        self.queue_file = os.path.join(BASE_DIR, "AUTO_YOUTUBE", "exploration_queue.json")
        
        self.explored = self._load_json(self.explored_file)
        self.queue = self._load_json(self.queue_file)  # List of terms to explore
    
    def _load_json(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return json.load(f)
            except:
                if path == self.queue_file: return []
                return {}
        return [] if path == self.queue_file else {}

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8", errors="replace") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_seed(self, term, source_context=""):
        """探索の種（キーワード）を追加"""
        if term not in self.explored and term not in self.queue:
            self.queue.append({"term": term, "source": source_context, "depth": 0})
            self._save_json(self.queue_file, self.queue)
            print(f"   [SEED] Added: {term}")

    def explore_step(self):
        """1ステップ深掘りする"""
        if not self.queue:
            return False, "No seeds to explore"
        
        # 優先度順（ここでは先頭から）で取り出す
        item = self.queue.pop(0)
        term = item["term"]
        depth = item.get("depth", 0)
        source = item.get("source", "")
        
        # 探索済みチェック
        if term in self.explored:
            self._save_json(self.queue_file, self.queue)
            return True, f"Already explored: {term}"
        
        print(f"\n[DEEP DIVE] {term} (Depth: {depth})")
        
        # --- [SEARCH & SYNTHESIZE] ---
        try:
            # Clean term name to avoid filesystem errors
            safe_term = re.sub(r'[\\/:*?"<>|]+', '', term)[:50]
            
            prompt = f"""
            【指令: 本質的洞察 (.core形式)】
            
            あなたは「行間を読む分析官」です。
            以下の用語について、表面的な辞書的意味ではなく、その背後にある**「文脈」「含意」「本質」**を深く鋭く解説してください。
            単なる要約ではなく、なぜそれが語られたのか、何を示唆しているのかを言語化してください。

            用語: {term}
            文脈: {source}
            
            出力形式:
            【本質】（この概念の核心を一言で・30文字以内）
            【背景】（なぜ今、この言葉が重要なのか。行間にある意図）
            【洞察】（ここから導き出される深い学びや仮説）
            【関連】（次に深掘りすべき概念3つ）
            """
            
            # Use Gemini for deep knowledge (Ollama is fallback)
            content = ""
            try:
                res = gemini_model.generate_content(prompt)
                content = res.text
            except:
                content = ollama_generate(prompt)
            
            # --- [EXTRACT NEW BRANCHES] ---
            # 生成されたコンテンツから、次の「枝」を見つける
            new_branches = extract_new_keywords(content)
            for br in new_branches:
                if br != term and br not in self.explored:
                     self.queue.append({"term": br, "source": f"Derived from {term}", "depth": depth + 1})
            
            # --- [SAVE RESULT] ---
            filename = f"KNOWLEDGE_{safe_term}.chi" # .md -> .chi (漢文圧縮的フォーマット)
            save_path = os.path.join(self.output_dir, filename)
            
            # Use module-level datetime
            from datetime import datetime
            
            # コンテンツを少し圧縮して保存（ヘッダー情報を簡素化）
            save_content = f"""TYPE:FRACTAL_NODE
TERM:{term}
SRC:{source}
DEPTH:{depth}
TIME:{datetime.now().strftime("%Y-%m-%d %H:%M")}
---BODY---
{content}
"""
            
            with open(save_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(save_content)
            
            # 探索済みに登録
            self.explored[term] = {"timestamp": datetime.now().isoformat(), "file": filename}
            
            # Save states
            self._save_json(self.explored_file, self.explored)
            self._save_json(self.queue_file, self.queue)
            
            return True, f"[OK] Explored: {term} -> Found {len(new_branches)} new branches"
            
        except Exception as e:
            # Error handling: Push back to queue if transient error, else skip
            return False, f"[ERROR] Exploration failed for {term}: {e}"

# ... (FractalExplorer definition) ...

# Global Explorer Instance
explorer = FractalExplorer(OUTPUT_DIR)

def load_presets():
    """Load channels.json from the dashboard app"""
    json_path = os.path.join(BASE_DIR, "apps", "youtube_channel", "data", "channels.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            return [(ch["channel_id"], ch["name"]) for ch in data.get("channels", []) if ch.get("enabled", True)]
        except:
            pass
    return []

def patrol_channels():
    """Registered Channels Patrol"""
    channels = load_presets()
    if not channels:
        return False
    
    print(f"📡 Patrolling {len(channels)} subscribed channels...")
    count = 0
    
    for cid, name in channels:
        # Check simplified feed (API free)
        videos = get_channel_videos(f"https://www.youtube.com/channel/{cid}")
        if videos:
            # Check top 1 video
            vid, title = videos[0]
            
            # Check if likely already processed
            safe_title = re.sub(r'[\\/:*?"<>|]+', '', title)[:30]
            # Simple check by filename existence to avoid API call
            # (Strict check happens inside process_video)
            
            res = process_video(vid, title)
            print(f"   [{name}] {res}")
            if "✅" in res:
                count += 1
                explorer.add_seed(title, source_context=f"Channel: {name}")
    
    return count > 0

# --- Main Loop ---
print("🚀 AI Agent Started: Hybrid Mode")
set_title("🚀 起動中... 待機モード")

while True:
    try:
        set_title("👀 監視中... (手動URL待機)")
        manual_job = False
        
        # 1. Manual Jobs
        if os.path.exists(INPUT_FILE):
             try:
                with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                
                if content and "http" in content:
                    set_title("⚡ 優先ジョブ実行中...")
                    print("\n========== ⚡ PRIORITY JOB ==========")
                    lines = content.split('\n')
                    with open(INPUT_FILE, "w", encoding="utf-8", errors="replace") as asf:
                        asf.write("") # Clear immediately
                    
                    for line in lines:
                        if "http" in line:
                             print(process_url(line))
                    print("=====================================\n")
                    manual_job = True
             except Exception as e:
                print(f"File Read Error: {e}")
        
        # 2. Auto Patrol (If no manual job)
        if not manual_job:
            print("\n[SEARCH] Starting Routine Patrol...")
            
            # Phase A: Channel Presets Check
            patrol_channels()
            
            # Phase B: Keyword Exploration
            auto_patrol()
            
            # --- FRACTAL EXPLORATION PHASE ---
            # Patrolが終わったら、次のサイクルまでの時間を深掘りに使う
            print("\n[PROBING] Entering Knowledge Fractal Phase...")
            print("   (Previously idle time is now used for deep diving)")
            
            start_time = time.time()
            IDLE_DURATION = 1200 # 20 minutes
            
            while (time.time() - start_time) < IDLE_DURATION:
                # 1. 探索実行
                success, msg = explorer.explore_step()
                print(f"   {msg}")
                
                # 2. 休憩 (API制限とCPU負荷軽減)
                if success:
                    sleep_time = 30 # 成功したら30秒休憩
                else:
                    sleep_time = 10 # キューが空なら確認頻度を下げる
                    print("   💤 Queue empty. Waiting for seeds...")
                
                # 残り時間表示
                elapsed = time.time() - start_time
                remaining = IDLE_DURATION - elapsed
                set_title(f"🌌 深掘り中... 残り {int(remaining/60)}分 | {msg[:20]}")
                time.sleep(sleep_time)
            
            print("⏰ Fractal Phase complete. Resuming Patrol.")
            # Skip the old sleep logic since we occupied it
            continue
                
    except Exception as e:
        relay.report(e, context="System Main Loop Crash")
        print(f"[ERROR] System Error: {e}")
        
    set_title("💤 休憩中 (3分)...")
    wait_sec = 180  # 3分に短縮
    print(f"\n⏳ Sleeping for {wait_sec/60} minutes... (Next: {time.strftime('%H:%M', time.localtime(time.time() + wait_sec))})")
    time.sleep(wait_sec)
