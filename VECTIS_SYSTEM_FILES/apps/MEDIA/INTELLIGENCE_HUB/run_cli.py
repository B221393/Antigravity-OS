import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv
import sys
import textwrap
import time
import glob
import yt_dlp
import re
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
# import scrapetube (Removed for stability - using RSS)
# import scrapetube (Removed for stability - using RSS)
# Error Telemetry
# Setup Paths & Env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMO_FILE = os.path.join(DATA_DIR, "channel_memos.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json") # The Knowledge Universe

sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))
load_dotenv(os.path.join(BASE_DIR, "../../../.env"))

# Error Telemetry
from modules.error_relay import ErrorRelay
relay = ErrorRelay("YouTube_CLI")

# Use Ollama Smart Selector (Dynamic Model Selection)
try:
    from modules.ollama_smart_selector import ask_ollama, get_optimal_model
    model_name, reason = get_optimal_model()
    print(f"[LLM] {reason}")
    llm = "smart_ollama"  # Flag for smart selector
except Exception as e:
    print(f"[WARN] Ollama not available ({e}). Using fallback UnifiedLLM.")
    from modules.unified_llm import UnifiedLLM
    llm = UnifiedLLM(provider="ollama", model_name="gemma:2b")

# Import the new Architect
from modules.antigravity import AntigravityArchitect
architect = AntigravityArchitect()

# Ensure data dir
os.makedirs(DATA_DIR, exist_ok=True)

# --- Universe Manager (Knowledge Graph) ---
class UniverseManager:
    """
    Manages the EGO Universe (Knowledge Graph) stored in universe.json.
    
    【INVARIANT】
    - data always contains 'nodes' and 'links' lists
    - All node IDs are unique within the universe
    
    【REASONING】
    Q: Why a class instead of functions?
    A: - Encapsulates file path and data state
       - Provides caching to avoid repeated file reads
       - Methods like add_node can atomically update and save
    """
    
    def __init__(self, filepath=UNIVERSE_FILE):
        self.filepath = filepath
        self.data = self._load()
    
    def _load(self):
        """Load universe data from file, creating empty structure if missing."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure structure
                    if 'nodes' not in data:
                        data['nodes'] = []
                    if 'links' not in data:
                        data['links'] = []
                    return data
            except Exception as e:
                print(f"[WARN] Failed to load universe.json: {e}")
        return {'nodes': [], 'links': []}
    
    def _save(self):
        """Persist universe data to file."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # Export as JS for Static Dashboard (CORS bypass)
            self._save_as_js()
            
        except Exception as e:
            relay.report(e, context="UniverseManager._save")

    def _save_as_js(self):
        """Save data as a JS file for static HTML access."""
        js_path = self.filepath.replace('.json', '.js')
        try:
            with open(js_path, 'w', encoding='utf-8') as f:
                # Assign to global variable
                json_str = json.dumps(self.data, ensure_ascii=False)
                f.write(f"window.UNIVERSE_DATA = {json_str};")
        except Exception as e:
            print(f"[WARN] Failed to save JS bridge: {e}")
    
    def get_node_summaries(self):
        """
        Returns list of simplified node info for deduplication checks.
        
        【POSTCONDITION】
        Returns list of dicts with at least 'title' key.
        """
        return [{'id': n.get('id'), 'title': n.get('title', '')} for n in self.data.get('nodes', [])]
    
    def add_node(self, metadata, links=None):
        """
        Add a new node to the universe.
        
        【PRECONDITION】
        - metadata contains at least 'title' and 'group'
        
        【POSTCONDITION】
        - Node with unique ID is added to universe
        - Returns (node_id, title) on success, (None, None) if duplicate
        """
        import difflib
        from datetime import datetime
        
        title = metadata.get('title', 'Untitled')
        
        # Duplicate check (fuzzy matching)
        for existing in self.data['nodes']:
            ratio = difflib.SequenceMatcher(None, title, existing.get('title', '')).ratio()
            if ratio > 0.85:  # 85% similarity threshold
                return None, None  # Duplicate detected
        
        # Generate unique ID
        node_count = len(self.data['nodes'])
        node_id = f"N{node_count + 1:03d}"
        
        new_node = {
            'id': node_id,
            'title': title,
            'summary': metadata.get('summary', ''),
            'group': metadata.get('group', 'General'),
            'importance': metadata.get('importance_score', 5),
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        self.data['nodes'].append(new_node)
        
        # Add links if provided
        if links:
            for link in links:
                self.data['links'].append({
                    'source': node_id,
                    'target': link.get('target'),
                    'strength': link.get('strength', 1)
                })
        
        self._save()
        return node_id, title

# Instantiate the Universe Manager
universe_manager = UniverseManager()

# --- Load Channels from File ---
def load_channels() -> dict[str, tuple[str, str]]:
    """
    Load YouTube channel configurations from external JSON file.
    
あｙにゃうづｒｇｇｇｙふぇ。ｗｌｙｔｒｔｎｙうぃｗ、ｗｇｙねｌえｎ
    - OUTPUT: Dictionary mapping numeric IDs to (channel_name, channel_id) tuples
    - PROPERTY: Only enabled channels are included in the output
    - FALLBACK: Always returns a valid dict (hardcoded defaults if file missing)
    
    【PRECONDITION】
    1. If CHANNELS_FILE exists, it must be valid JSON
    2. channels.json format: {"channels": [{"name": str, "channel_id": str, "enabled": bool}]}
    
    【POSTCONDITION】
    1. Returns non-empty dict (at least fallback defaults)
    2. All values are (str, str) tuples
    3. All keys are numeric strings ("1", "2", "3", ...)
    
    【REASONING】
    Q: Why load from external file instead of hardcoding?
    A: - Allows dynamic channel management via Magi HUD
       - Users can add channels without editing code
       - Configuration persists across updates
       - Separation of code and data
    
    Q: Why filter by 'enabled' field?
    A: - Temporarily disable channels without deleting them
       - Preserves history and metadata
       - User can re-enable later without re-adding
       - Reduces friction in channel management
    
    Q: Why fallback to hardcoded defaults?
    A: - System remains functional on first run (before file created)
       - Recovery from corrupted/deleted file
       - Bootstrap mechanism for new installations
    
    Q: Why use numeric string keys instead of channel_id directly?
    A: - Legacy compatibility with CLI menu system
       - User-friendly numbered selection (type "1" not "UC8yHePe...")
       - Maintains stable order across reloads
    """
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Convert to PRESETS format: {id: (name, channel_id)}
            # REASONING: Only include enabled channels (user can toggle without delete)
            presets = {}
            for i, ch in enumerate(data.get("channels", [])):
                if ch.get("enabled", True):  # Default True for safety
                    presets[str(i+1)] = (ch["name"], ch["channel_id"])
            
            # INVARIANT: Return non-empty dict (or fallback if all disabled)
            return presets if presets else _get_default_channels()
            
        except Exception as e:
            relay.report(e, context="load_channels - falling back to defaults")
            print(f"[WARN] Failed to load channels.json: {e}. Using defaults.")
            return _get_default_channels()
    
    # Fallback: File doesn't exist yet
    return _get_default_channels()

def _get_default_channels() -> dict[str, tuple[str, str]]:
    """Hardcoded fallback channels (INVARIANT: always available)"""
    return {
        "1": ("Pivot 公式", "UC8yHePe_RgUBE-waRWy6olw"),
        "2": ("ReHacQ", "UCG_oqDSlIYEspNpd2H4zWhw"),
        "3": ("NewsPicks", "UCfTnJmRQP79C4y_BMF_XrlA"),
        "4": ("Janji Music", "UCuz2eFomc37LEbR1zd0yqJw")
    }

PRESETS = load_channels()

# --- News Sources ---
# --- History / Deduplication ---
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_log.json")

def load_processed_log():
    try:
        if os.path.exists(PROCESSED_FILE):
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except: pass
    return set()

def save_processed_log(current_set):
    try:
        # Keep only last 1000 items to avoid infinite growth
        trimmed = list(current_set)[-1000:]
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(trimmed, f)
    except: pass

# --- News Sources (Expanded for Variety) ---
NEWS_SOURCES = {
    "1": ("GIGAZINE", "https://gigazine.net/news/rss_2.0/"),
    "2": ("TechCrunch JP", "https://techcrunch.com/feed/"),
    "3": ("Publickey (Tech)", "https://www.publickey1.jp/atom.xml"),
    "4": ("Wired JP", "https://wired.jp/rss.xml"),
    "5": ("Publishing (出版業界)", "https://news.google.com/rss/search?q=%E5%87%BA%E7%89%88%E6%A5%AD%E7%95%8C&hl=ja&gl=JP&ceid=JP:ja"),
    "6": ("NHK (社会・常識)", "https://www.nhk.or.jp/rss/news/cat0.xml"),
    "7": ("National Geographic", "https://natgeo.nikkeibp.co.jp/rss/flash.xml"),
    "8": ("Bijutsu Techo (Art)", "https://bijutsutecho.com/news/feed.xml"),
    "9": ("Courrier (Intl)", "https://courrier.jp/feed/"),
    "10": ("Business Insider", "https://www.businessinsider.jp/feed/index.xml"),
    "11": ("JAXA (Space)", "https://www.jaxa.jp/rss/press_j.rdf"),
    "12": ("Cinra (Culture)", "https://www.cinra.net/feed"),
    "13": ("arXiv AI (cs.AI)", "http://export.arxiv.org/rss/cs.AI"),
    "14": ("Nature Reviews", "http://feeds.nature.com/nature/rss/current"),
    # === 追加ソース (2026-01-24) ===
    "15": ("Yahoo News JP", "https://news.yahoo.co.jp/rss/topics/top-picks.xml"),
    "16": ("日経電子版", "https://assets.wor.jp/rss/rdf/nikkei/news.rdf"),
    "17": ("Hacker News", "https://hnrss.org/frontpage"),
    "18": ("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss"),
    "19": ("東洋経済オンライン", "https://toyokeizai.net/list/feed/rss"),
    "20": ("現代ビジネス", "https://gendai.media/list/feed/rss"),
    "21": ("PR TIMES (Business)", "https://prtimes.jp/main/html/searchrlp/key/Business/rss"),
    "22": ("日経ビジネス電子版", "https://news.google.com/rss/search?q=%E6%97%A5%E7%B5%8C%E3%83%93%E3%82%B8%E3%83%8D%E3%82%B9+%E6%88%A6%E7%95%A5&hl=ja&gl=JP&ceid=JP:ja"),
    "23": ("Forbes JAPAN", "https://forbesjapan.com/feed/"),
}

# --- CHAOS SOURCES (Curiosity/Weird/Science) ---
# --- CHAOS SOURCES (Liberal Arts / Kyoyo / High Context / TRIVIA) ---
CHAOS_SOURCES = {
    # === 書籍・レビュー ===
    "1": ("HONZ (Book Rev)", "https://honz.jp/feed"),
    "2": ("ALL REVIEWS", "https://allreviews.jp/rss"),
    
    # === 大学研究・論文 ===
    "3": ("UTokyo Research", "https://www.u-tokyo.ac.jp/content/400002233.xml"),
    "4": ("Kyoto Univ Res", "https://www.kyoto-u.ac.jp/ja/research/rss.xml"),
    "5": ("arXiv cs.AI", "http://export.arxiv.org/rss/cs.AI"),
    "6": ("arXiv Physics", "http://export.arxiv.org/rss/physics"),
    "7": ("arXiv Math", "http://export.arxiv.org/rss/math"),
    "8": ("arXiv q-bio (Biology)", "http://export.arxiv.org/rss/q-bio"),
    "9": ("arXiv Econ", "http://export.arxiv.org/rss/econ"),
    "10": ("Nature Reviews", "http://feeds.nature.com/nature/rss/current"),
    "11": ("Science Daily", "https://www.sciencedaily.com/rss/all.xml"),
    
    # === カルチャー・芸術 ===
    "12": ("Wired JP", "https://wired.jp/rss.xml"),
    "13": ("Bijutsu Techo", "https://bijutsutecho.com/news/feed.xml"),
    "14": ("National Geographic", "https://natgeo.nikkeibp.co.jp/rss/flash.xml"),
    "15": ("Mit Technology Review", "https://www.technologyreview.jp/feed/"),
    
    # === 雑学・クイズ・百科事典 ===
    "16": ("Wikipedia Featured (EN)", "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=featured&feedformat=rss"),
    "17": ("Wikipedia DYK (EN)", "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=dyk&feedformat=rss"),
    "18": ("Wikipedia OnThisDay (EN)", "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=onthisday&feedformat=rss"),
    "19": ("Mental Floss (Trivia)", "https://www.mentalfloss.com/feed"),
    "20": ("todayilearned (Reddit)", "https://www.reddit.com/r/todayilearned/.rss"),
    
    # === 哲学・思想 ===
    "21": ("Philosophy Now", "https://philosophynow.org/feed"),
    "22": ("Brain Pickings", "https://www.themarginalian.org/feed/"),
    
    # === 歴史 ===
    "23": ("History Today", "https://www.historytoday.com/feed/rss.xml"),
    "24": ("Smithsonian Mag", "https://www.smithsonianmag.com/rss/latest_articles/"),
}

# --- KYOYO KEYWORDS (Active Injection) ---
KYOYO_KEYWORDS = [
    "世界史 講義", "哲学 入門", "文学史", "現代思想", 
    "リベラルアーツ", "クラシック音楽 解説", "NHKスペシャル", 
    "落語", "能楽", "美術史", "サイエンスZERO", 
    "100分de名著", "教養 講座", "数学の歴史", "認知科学"
]

# --- BOOK SOURCES (Best Sellers / Rankings) ---
BOOK_SOURCES = {
    "1": ("HONZ (Book Review)", "https://honz.jp/feed"),
    "2": ("Book Bang", "https://www.bookbang.jp/feed/"),
    "3": ("Kinokuniya Ranking", "https://www.kinokuniya.co.jp/disp/RSS/ranking_weekly_general.rdf")
}

# --- JOB SOURCES (Shukatsu) ---
JOB_SOURCES = {
    "1": ("Shukatsu (General)", "https://news.google.com/rss/search?q=%E5%B0%B1%E6%B4%BB&hl=ja&gl=JP&ceid=JP:ja"),
    "2": ("Mynavi (Trend)", "https://agora-web.jp/rss"), # Example proxied/related feed
    "3": ("Nikkei (Career)", "https://assets.wor.jp/rss/rdf/nikkei/career.rdf")
}

def do_patrol(auto_launch=False, return_items=False, chaos_mode=False):
    print("\n🔄 === INTELLIGENCE PATROL STARTS ===")
    if chaos_mode:
        print("🌀 [MODE] CHAOS / CURIOSITY (Business Filters: ACTIVE) 🌀")
    else:
        print("🏢 [MODE] STANDARD (Business/Tech)")
        
    print("Scanning YouTube & News Sources...\n")
    
    # Load History
    processed_ids = load_processed_log()
    patrol_items = [] 
    
    import random
    
    # --- YouTube ---
    channel_keys = list(PRESETS.keys())
    
    for key in channel_keys:
        name, cid = PRESETS[key]
        if chaos_mode:
            banned_keywords = ["Pivot", "NewsPicks", "ReHacQ", "堀江", "ひろゆき"]
            if any(bk in name for bk in banned_keywords):
                continue

        print(f"📡 [YouTube] {name}...", end="\r")
        try:
            title, videos = get_channel_feed(cid)
            if videos and isinstance(videos, list):
                new_videos = [v for v in videos if v['id'] not in processed_ids]
                
                # Dedupe against Universe
                existing_titles = [n['title'] for n in universe_manager.get_node_summaries()]
                import difflib
                
                unique_videos = []
                for v in new_videos:
                    is_dup = False
                    for ext in existing_titles:
                        ratio = difflib.SequenceMatcher(None, v['title'], ext).ratio()
                        if ratio > 0.6: 
                            is_dup = True
                            break
                    if not is_dup:
                        unique_videos.append(v)

                if unique_videos:
                    v = random.choice(unique_videos) 
                    patrol_items.append({
                        "type": "youtube", 
                        "label": f"[Y]", 
                        "title": v['title'], 
                        "source": name,
                        "data": v,
                        "unique_id": v['id']
                    })
        except: pass
        
    # --- News ---
    current_news_sources = CHAOS_SOURCES if chaos_mode else NEWS_SOURCES
    news_keys = list(current_news_sources.keys())
    
    for key in news_keys:
        name, url = current_news_sources[key]
        print(f"📡 [News] {name}...", end="\r")
        try:
            ftitle, items = get_rss_feed(url)
            if items:
                new_items = [i for i in items if i['link'] not in processed_ids]
                if new_items:
                    item = random.choice(new_items)
                    patrol_items.append({
                        "type": "news", 
                        "label": f"[N]", 
                        "title": item['title'], 
                        "source": name,
                        "data": item,
                        "unique_id": item['link']
                    })
        except: pass

    # --- JOB HUNTING (Shukatsu) ---
    print(f"📡 [Job] Scanning Career Feeds...", end="\r")
    for key, (name, url) in JOB_SOURCES.items():
        try:
            ftitle, items = get_rss_feed(url)
            if items:
                new_items = [i for i in items if i['link'] not in processed_ids]
                if new_items:
                    # Take up to 2 items per source to ensure coverage
                    for item in new_items[:2]:
                        patrol_items.append({
                            "type": "shukatsu", 
                            "label": f"[JOB]", 
                            "title": item['title'], 
                            "source": name,
                            "data": item,
                            "unique_id": item['link']
                        })
        except: pass

    # --- Books (Best Sellers) ---
    print(f"📡 [Books] Scanning Best Sellers...", end="\r")
    for key, (name, url) in BOOK_SOURCES.items():
        try:
            ftitle, items = get_rss_feed(url)
            if items:
                new_items = [i for i in items if i['link'] not in processed_ids]
                if new_items:
                    item = random.choice(new_items)
                    patrol_items.append({
                        "type": "book", 
                        "label": f"[B]", 
                        "title": item['title'], 
                        "source": name,
                        "data": item,
                        "unique_id": item['link']
                    })
        except: pass

    random.shuffle(patrol_items)
    
    print(f"\n✅ Scan Complete. Total {len(patrol_items)} New Intelligence Items.\n")
    
    for i, item in enumerate(patrol_items[:10]): 
        print(f"{i+1:02d}. {item['source']:<15} : {item['title'][:60]}...")
    
    # AUTO LAUNCH SEQUENCE
    if auto_launch:
        print("\n🚀 === AUTO-LAUNCH SEQUENCE INITIATED (Turbo Mode) ===\n")
        
        # Prioritize BOOKS, then others
        book_items = [i for i in patrol_items if i['type'] == 'book']
        other_items = [i for i in patrol_items if i['type'] != 'book']
        targets = book_items[:2] + other_items[:8-min(len(book_items), 2)]
        
        def process_patrol_item(item):
            """Parallel worker for knowledge extraction"""
            try:
                # Additional Dedupe Check
                existing_summaries = universe_manager.get_node_summaries()
                if any(node['title'] == item['title'] for node in existing_summaries):
                    return f"      ⚠️ Already in Universe: {item['title'][:20]}"

                content = ""
                if item['type'] == 'youtube':
                    v_id = item['data']['id']
                    transcript = get_transcript(v_id)
                    content = transcript if transcript and transcript != "RATE_LIMITED" else f"Video: {item['title']}"
                elif item['type'] in ['news', 'shukatsu', 'book']:
                    raw_summary = item['data']['summary']
                    clean_desc = re.sub('<[^<]+?>', '', html.unescape(raw_summary))
                    content = f"Title: {item['title']}\nSummary: {clean_desc}"
                
                # Special Handle for Shukatsu
                if item['type'] == 'shukatsu':
                    events = extract_shukatsu_schedule(content, item['title'])
                    for ev in events: register_schedule_to_magi(ev)
                
                # Launch
                launch_to_universe(item['title'], content, item['type'])
                return f"      ✅ Launched: {item['title'][:30]}"
            except Exception as e:
                return f"      ❌ Error: {item['title'][:20]} ({e})"

        # Parallelize Knowledge Processing
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_patrol_item, item) for item in targets]
            for future in as_completed(futures):
                print(future.result())
                # Note: processed_ids is updated outside for thread safety
        
        for item in targets:
            processed_ids.add(item['unique_id'])
        
        save_processed_log(processed_ids)
        print("\n🌌 Auto-Patrol Cycle Complete.")
        return

    # MANUAL MODE
    while True:
        sel = input("\nSelect Number to Deep Dive / (U)niverse All / (B)ack > ").strip().lower()
        if sel == 'b': break
        
        if sel == 'u':
             # Manual U Logic (Same as auto basically)
             # ... (omitted for brevity, assume similar loop)
             pass
            
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(patrol_items):
                target = patrol_items[idx]
                if target['type'] == 'youtube':
                    process_video(target['data'])
                else:
                    process_news_item(target['data'])
        except ValueError: pass

# --- CLI Main Loop ---




# --- Logic Functions ---

def get_rss_feed(url):
    """Generic RSS/Atom parser using standard lib"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = []
        
        # Try finding items (RSS 2.0) or entries (Atom)
        # Naive approach: find all 'item' or 'entry' tags recursively
        all_items = root.findall('.//item') + root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        title_node = root.find('.//channel/title')
        if title_node is None: title_node = root.find('.//{http://www.w3.org/2005/Atom}title')
        feed_title = title_node.text if title_node is not None else "Unknown Feed"

        for entry in all_items:
            # Title
            t = entry.find('title')
            if t is None: t = entry.find('{http://www.w3.org/2005/Atom}title')
            title = t.text if t is not None else "No Title"
            
            # Link
            l = entry.find('link')
            if l is None: l = entry.find('{http://www.w3.org/2005/Atom}link')
            
            link = ""
            if l is not None:
                link = l.text if l.text else l.attrib.get('href', '')

            # Description/Summary for content
            d = entry.find('description')
            if d is None: d = entry.find('{http://www.w3.org/2005/Atom}summary')
            if d is None: d = entry.find('{http://www.w3.org/2005/Atom}content')
            desc = d.text if d is not None else ""
            
            items.append({'title': title, 'link': link, 'summary': desc})
            
        return feed_title, items
    except Exception as e:
        return None, str(e)

def get_channel_feed(channel_id):
    """RSSフィードから最新動画を取得 (API Key不要 - More Stable)"""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
            # Standardize namespaces
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/', 'atom': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(xml_data)
            
            videos = []
            # Find all entries
            for entry in root.findall('atom:entry', ns):
                vid_node = entry.find('yt:videoId', ns)
                title_node = entry.find('atom:title', ns)
                link_node = entry.find('atom:link', ns)
                pub_node = entry.find('atom:published', ns)
                
                if vid_node is None or title_node is None:
                    continue
                    
                vid = {
                    'id': vid_node.text,
                    'title': title_node.text,
                    'link': link_node.attrib['href'] if link_node is not None else "",
                    'published': pub_node.text if pub_node is not None else "Unknown"
                }
                videos.append(vid)
                
            # Get channel title
            title_node = root.find('atom:title', ns)
            channel_title = title_node.text if title_node is not None else "Unknown Channel"
                
            return channel_title, videos
    except Exception as e:
        return None, str(e)

def search_youtube_topic(query: str):
    """
    Active Injection: Uses yt-dlp to search for specific topics.
    """
    try:
        # search_query format for yt-dlp: 'ytsearchN:keyword'
        search_str = f"ytsearch3:{query}"
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'extract_flat': True, 
            'default_search': 'ytsearch'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # yt-dlp returns search results as a playlist
            info = ydl.extract_info(search_str, download=False)
            if 'entries' in info and info['entries']:
                # Pick a random one from top 3 to ensure some rotation
                import random
                entry = random.choice(info['entries'])
                return {
                    'id': entry['id'],
                    'title': entry['title'],
                    'link': f"https://www.youtube.com/watch?v={entry['id']}" if entry.get('id') else "",
                    'published': "Search Result"
                }
    except Exception as e:
        print(f"      (Search Injection Failed: {e})")
        return None


def get_transcript(video_id: str) -> str | None:
    """
    Fetch YouTube video transcript with intelligent fallback mechanism.
    
    【INVARIANT】
    - INPUT: video_id must be a valid YouTube video ID (11 chars, alphanumeric + - _)
    - OUTPUT: transcript text (str), "RATE_LIMITED" marker, or None
    - PROPERTY: Idempotent - same video_id always returns same transcript (unless YouTube changes it)
    
    【PRECONDITION】
    1. video_id is not empty and is valid format
    2. Network connection is available
    3. At least one of: youtube_transcript_api or yt-dlp is installed
    
    【POSTCONDITION】
    1. result is None OR result == "RATE_LIMITED" OR (isinstance(result, str) and len(result) > 100)
    2. If result == "RATE_LIMITED", caller must use Gemini direct mode
    3. Function does not raise exceptions (all errors handled internally)
    """
    
    # INVARIANT CHECK
    if not video_id or len(video_id) != 11:
        return None

    # === METHOD 1: youtube_transcript_api (Preferred) ===
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Safe retrieval with language fallback
        try:
           transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
           # Prioritize Japanese, then English
           transcript = transcript_list.find_transcript(['ja', 'en']) 
           data = transcript.fetch()
           text = " ".join([t['text'] for t in data])
           return text
        except AttributeError:
             # Fallback for older API versions
             data = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
             text = " ".join([t['text'] for t in data])
             return text
             
    except Exception as e:
        error_str = str(e)
        if "429" in error_str: return "RATE_LIMITED"
        # If transcript disabled or not found, fall through to yt-dlp
        pass 
        
    # === METHOD 2: yt-dlp (fallback) ===
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': ['ja', 'en'],
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        # Suppress stderr to avoid alarming users with "ERROR" logs for normal fallbacks
        import sys
        from io import StringIO
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # yt-dlp extraction of subs without download is complex.
                # Often it's better to rely on metadata if transcript api failed.
                # For now, we return None to trigger the "Comment/Summary" fallback in caller.
                pass
        finally:
            sys.stderr = old_stderr

    except Exception:
        pass
        
    return None

# --- Auto Pilot Logic ---

# --- Command Link ---
# --- Command Link ---
COMMAND_FILE = os.path.join(os.path.dirname(BASE_DIR), "../../EGO_COMMAND.txt")

# --- HELPER: BOOKSHELF IO ---
def save_to_bookshelf(title, content, subfolder, source="Unknown"):
    """
    Saves content to EGO_SYSTEM_FILES/OBSIDIAN_WRITING/BOOKSHELF/<subfolder>
    """
    # Sanitize Title
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_").strip()[:50]
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Construct Path
    # ../../../OBSIDIAN_WRITING/BOOKSHELF relative to BASE_DIR (apps/youtube_channel)
    shelf_root = os.path.abspath(os.path.join(BASE_DIR, "../../OBSIDIAN_WRITING/BOOKSHELF"))
    target_dir = os.path.join(shelf_root, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    filename = f"[{date_str}] {safe_title}.md"
    full_path = os.path.join(target_dir, filename)
    
    # Metadata Header
    meta = f"""---
created: {datetime.now().isoformat()}
source_name: {source}
tags: [#{subfolder.split('_')[1].lower()}, #vectis_intel]
---

# {title}

"""
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(meta + content)
        
    return filename

# --- HELPER: SCHEDULE MAGI INTEGRATION ---
SHARED_DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../UTILS/schedule_magi/data/precog_schedules.json"))

def extract_shukatsu_schedule(content, context_title):
    """
    Uses LLM to extract JSON events from text, specifically looking for Job Hunting (Shukatsu) deadlines.
    """
    prompt = f"""You are a Schedule Extractor for a Job Hunter.
Analyze the text below and extract ANY dates related to:
1. Job Applications (ES Deadlines, Interviews)
2. Company Explanatory Sessions
3. Internship Deadlines

**Input**: {context_title}
**Text**: {content[:2000]}

Today is {datetime.now().strftime('%Y-%m-%d')}.

**Output Format (JSON only, no explanation)**:
[{{"Date": "YYYY-MM-DD", "Time": "HH:MM", "Event": "summary", "Type": "DEADLINE", "Priority": 10}}]
Return [] if no dates found."""
    try:
        # Use smart ollama if available
        if llm == "smart_ollama":
            res = ask_ollama(prompt)
        elif hasattr(llm, 'generate'):
            res = llm.generate(prompt)
        elif hasattr(llm, 'chat'):
            res = llm.chat(prompt)
        else:
            return []
            
        # Robust JSON Extraction
        import re
        clean_json = res.replace("```json", "").replace("```", "").strip()
        
        # Look for list pattern [...]
        match = re.search(r"(\[.*\])", clean_json.replace('\n', ' '), re.DOTALL)
        if match:
            clean_json = match.group(1)
        else:
             # Look for object pattern if single item { ... }
             match_obj = re.search(r"(\{.*\})", clean_json.replace('\n', ' '), re.DOTALL)
             if match_obj:
                 clean_json = f"[{match_obj.group(1)}]" # wrap in list
            
        events = json.loads(clean_json)
        return events if isinstance(events, list) else []
    except Exception as e:
        print(f"      [Schedule Extraction Error] {e}")
        return []

def register_schedule_to_magi(event_data):
    """
    Appends a single event to the shared schedule JSON.
    """
    try:
        os.makedirs(os.path.dirname(SHARED_DATA_FILE), exist_ok=True)
        existing = []
        if os.path.exists(SHARED_DATA_FILE):
             try:
                 with open(SHARED_DATA_FILE, 'r', encoding='utf-8') as f:
                     existing = json.load(f)
             except: pass
        
        for ex in existing:
            if ex.get('Date') == event_data.get('Date') and ex.get('Event') == event_data.get('Event'):
                return 
        
        existing.append(event_data)
        
        with open(SHARED_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
        
        _append_to_markdown_calendar(event_data)
            
    except Exception as e:
        print(f"Magi Sync Error: {e}")

def _append_to_markdown_calendar(event):
    log_path = os.path.abspath(os.path.join(BASE_DIR, "../../..", "OBSIDIAN_WRITING/BOOKSHELF/00_Schedule_Log.md"))
    try:
        line = f"- [ ] **{event['Date']}** {event['Time']} : {event['Type']} - {event['Event']}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except: pass

# --- AUTO PILOT LOGIC ---
COMMAND_FILE = os.path.join(os.path.dirname(BASE_DIR), "../../EGO_COMMAND.txt")

def start_auto_pilot():
    """
    Hands-Free Continuous Intelligence Cycle (Infinite).
    """
    SCAN_INTERVAL_MIN = 30
    DISPLAY_INTERVAL_MIN = 1 
    
    last_patrol_time = 0 # Force immediate patrol
    found_items = []
    
    while True:
        current_time = time.time()
        
        # === 1. PATROL CHECK ===
        if current_time - last_patrol_time > (SCAN_INTERVAL_MIN * 60):
            print("\n\n🔄 === AUTO-PATROL CYCLE INITIATED ===")
            try:
                # Decide mode based on some probability OR global setting?
                # For now, Auto Pilot defaults to Standard, but we can make it Chaos if listed in Command.
                # Actually, let's keep it Standard for Auto unless configured.
                # But wait, the user wants to DESTROY bias.
                # Let's make Auto Pilot run CHAOS mode 50% of the time or if specified?
                # For safety, let's default to standard unless start_auto_pilot has an arg.
                # Let's check `sys.argv` here too.
                is_chaos = "--chaos" in sys.argv
                found_items = do_patrol(auto_launch=True, return_items=True, chaos_mode=is_chaos)
            except Exception as e:
                print(f"CRITICAL ERROR in do_patrol: {e}")
                found_items = []
            
            last_patrol_time = time.time()

            if not found_items:
                 try:
                    nodes = universe_manager.data.get("nodes", [])
                    if nodes:
                        import random
                        samples = random.sample(nodes, min(len(nodes), 5))
                        found_items = [{"type": "universe_node", "title": n.get("title"), "source": "Universe", "data": n} for n in samples]
                        print(f"   (Re-analyzing {len(found_items)} Universe Memory Nodes...)")
                 except: pass

        # === 2. DEEP DIVE ===
        if found_items:
             import random
             target = random.choice(found_items)
             
             print(f"\n\n🔍 === DEEP DIVE: {target['title'][:40]}... ===")
             
             # Content Generation
             content_text = ""
             if target.get('type') == 'youtube':
                 v_id = target['data']['id']
                 tr = get_transcript(v_id)
                 content_text = tr if (tr and tr != "RATE_LIMITED") else (get_comments(v_id) or "")
             elif target.get('type') == 'news':
                 content_text = target['data']['summary']
             elif target.get('type') == 'book':
                 content_text = f"Book Trend: {target['title']}\nRanking/Details: {target['data'].get('summary','')}"
             elif target.get('type') == 'universe_node':
                 content_text = f"Title: {target['title']}\nSummary: {target['data'].get('summary','')}"
             
             print("   📚 Generating Comprehensive Bookshelf Report (Target: 20k chars)...")
             
             prompt = f"""
             あなたは「EGO百科事典」の編集長です。
             以下のコンテンツを元に、**「Wikipediaスタイルの超詳細な百科事典記事」**を作成してください。
             
             【執筆方針（ユーザー絶対命令）】
             1. **ターゲット**: 20,000文字級の「極厚」記事。
                - 入力テキストが短い、または不足している場合は、**あなたの持つ全ての背景知識を総動員して、定義・歴史・理論・構造・社会的影響・関連人物・統計データについて限界まで加筆**してください。
             2. **「圧縮と厚みの両立」**:
                - 話し言葉、冗長なイントロ、主観的な感想は徹底的に**「圧縮（削除）」**する。
                - そのコアにある概念、事実、ロジックについては徹底的に**「厚く（詳細化）」**する。
             3. **スタイル**: 
                - 学術的で客観的（Wikipediaスタイル）。
                - 「です・ます」調ではなく「だ・である」調（推奨）。
             
             【記事構成案】
             ## 概要
             ## 定義と語源
             ## 歴史的背景（ここを特に厚く）
             ## 主要な議論とメカニズム
             ## 批判と課題
             ## 結論と将来的展望
             
             【対象コンテンツ】
             {content_text[:15000]}
             """
             
             try:
                 # Generate
                 if hasattr(llm, 'chat'):
                     report = llm.chat(prompt)
                 else:
                     report = llm.generate_debate(prompt)
                     
                 # SAVE TO BOOKSHELF
                 category_map = {
                     'youtube': '01_YouTube_Summaries',
                     'news': '02_News_Clips',
                     'book': '03_Book_Trends',
                     'universe_node': '04_Auto_Research'
                 }
                 subfolder = category_map.get(target['type'], '05_Manual_Notes')
                 filename = save_to_bookshelf(target['title'], report, subfolder, source=target['source'])
                 print(f"\n✅ Stats: Report Saved to {filename}")

                 # --- SHUKATSU / SCHEDULE EXTRACTION ---
                 if "shukatsu" in subfolder.lower() or "就活" in subfolder or "news" in subfolder or "youtube" in subfolder:
                    print("   📅 Analyzing for Schedule/Deadlines...")
                    new_events = extract_shukatsu_schedule(report, target['title'])
                    if new_events:
                        for ev in new_events:
                            register_schedule_to_magi(ev)
                        print(f"      ✨ Registered {len(new_events)} events to Schedule Magi.")

                 print("="*60)
                 
             except Exception as e: print(f"Bookshelf Gen Error: {e}")

        # === 3. WAIT & LISTEN (With Command Interrupt) ===
        # Wait for DISPLAY_INTERVAL_MIN, checking command every second
        next_step_time = time.time() + (DISPLAY_INTERVAL_MIN * 60)
        
        while time.time() < next_step_time:
            # Check Command
            if os.path.exists(COMMAND_FILE):
                try:
                    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
                        content = f.read()
                    try: os.remove(COMMAND_FILE)
                    except: pass

                    if "AUTO_MODE: ON" in content:
                        print("\n      [COMMAND LINK] 🚀 AUTO-MODE ACTIVATE SIGNAL RECEIVED.")

                    lines = content.splitlines()
                    cmd = ""
                    for line in lines:
                        if line.strip() and not line.startswith("#") and ":" not in line: 
                            cmd = line.strip(); break
                    
                    if cmd:
                        print(f"\n⚡ COMMAND: {cmd}")
                        if "PATROL" in cmd:
                            last_patrol_time = 0 
                except Exception as e:
                    print(f"      [COMMAND LINK] Error: {e}")

            remaining = int(next_step_time - time.time())
            print(f"   Next Analysis in {remaining}s | Patrol in {int((SCAN_INTERVAL_MIN*60 - (time.time()-last_patrol_time))/60)}m...", end="\r")
            time.sleep(1)

# --- CLI Main Loop ---

def main():
    if "--auto-universe" in sys.argv:
        start_auto_pilot()
        # This function never returns, keeping the app alive indefinitely
    
    # Compatibility with manual launch
    elif "--patrol" in sys.argv:
        do_patrol(auto_launch=False, chaos_mode=("--chaos" in sys.argv))

    # Chaos flag for menu
    chaos_active = "--chaos" in sys.argv
        
    while True:
        mode_str = "CHAOS" if chaos_active else "STD"
        print(f"\n📺 === EGO INTELLIGENCE CLI (v2.7 {mode_str}) ===")
        print("0.  ⚡ Check All (Manual Patrol)")
        print("00. 🤖 Auto-Patrol (Hands-Free Mode)")
        print(f"C.  🌀 Toggle Chaos Mode (Current: {mode_str})")
        # ... (rest of menu) ...
        print("1.  YouTube Channels")
        print("2.  Enter Channel ID")
        print("3.  View Memos")
        print("4.  🌌 View Universe Stats")
        print("5.  📰 News Digest")
        print("Q.  Quit")
        
        choice = input("\nSelect > ").strip().lower()
        
        if choice == 'q':
            sys.exit(0)
        elif choice == 'c':
            chaos_active = not chaos_active
            print(f"   🌀 Chaos Mode set to: {chaos_active}")
        elif choice == '0':
            do_patrol(auto_launch=False, chaos_mode=chaos_active)
        elif choice == '00':
            # Restart auto pilot with new flag state? 
            # Actually start_auto_pilot checks sys.argv, so we might need to patch it or just pass arg.
            # But start_auto_pilot() doesn't take args in current def.
            # Modified above to check sys.argv. We should hack sys.argv if we toggle in menu.
            if chaos_active and "--chaos" not in sys.argv: sys.argv.append("--chaos")
            elif not chaos_active and "--chaos" in sys.argv: sys.argv.remove("--chaos")
            start_auto_pilot()
        elif choice == '5':
            # ... (Existing News Logic) ...
            print("\n📰 === NEWS SOURCES ===")
            for k,v in NEWS_SOURCES.items(): print(f"{k}: {v[0]}")
            sel = input("Select Source > ").strip()
            if sel in NEWS_SOURCES:
                handle_news_source(NEWS_SOURCES[sel])
            else:
                print("Invalid source.")

        elif choice == '1':
            # ... (Existing YouTube Logic) ...
            print("\n--- Presets ---")
            for k, v in PRESETS.items():
                print(f"{k}: {v[0]}")
            p_sel = input("Select Preset > ").strip()
            if p_sel in PRESETS:
                process_channel(PRESETS[p_sel][1])
                
        elif choice == '2':
            cid = input("Enter Channel ID (UC...) > ").strip()
            if cid: process_channel(cid)
                
        elif choice == '3':
            view_memos()
            
        elif choice == '4':
             u = universe_manager.data
             nodes = u.get('nodes', [])
             links = u.get('links', [])
             print(f"\n🌌 [EGO UNIVERSE]")
             print(f"Total Stars (Nodes): {len(nodes)}")
             print(f"Gravity Lines (Links): {len(links)}")
             input("Press Enter to continue...")





    


def get_comments(video_id: str) -> str | None:
    """
    Fetch top comments from YouTube video as a fallback context.
    
    【REASONING】
    When transcripts are missing, user comments often contain:
    - Timestamps with summaries
    - Key takeaways
    - Names of mentioned figures
    - Corrections/Context
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {'getcomments': True, 'skip_download': True, 'quiet': True, 'no_warnings': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            if not comments: return None
            return "\n".join([f"Comment {i+1}: {c.get('text', '')}" for i, c in enumerate(comments[:20])])
    except Exception as e:
        print(f"      (Comment Fetch Error: {e})")
        return None


def summarize_text(text, mode="youtube"):
    label = "動画内容" if mode == "youtube" else "記事内容"
    try:
        prompt = f"""
        【指令: EGO情報パッケージング（{label}解析）】
        以下の{label}を5つのレイヤーに分けて出力してください。
        
        ---EGO_SEPARATOR---

        【パート1: 圧縮ファイルヘッダー (Compressed View)】
        - **漢文的・ログ的圧縮文体**で記述すること。
        - 助詞（〜は、〜が）を極限まで削ぎ落とし、名詞と動詞で構成された「高密度な3行」にすること。
        - 例: "AI進化加速 / 雇用市場激変 / 適応必須"

        ---EGO_SEPARATOR---

        【パート2: 解凍データ (Decompressed Content)】
        - 「Logic Flow（論理展開）」をステップ・バイ・ステップで記述。
        - 「Insight Crystals（洞察）」として、表面的な情報ではなく「なぜそうなるか」の構造を記述。

        ---EGO_SEPARATOR---

        【パート3: Deep Dive (Intellectual Figures)】
        - 言及された重要人物、技術、理論、書籍名を特定し、解説を加える。
        - 固有名詞は可能な限り抽出すること。

        ---EGO_SEPARATOR---

        【パート4: 関連知識・用語解説 (Context Buffer)】
        - 専門用語や背景知識の補足。

        ---EGO_SEPARATOR---

        【パート5: アクション戦略 (Strategy)】
        - 出版就活や自己研鑽において、この情報をどう武器にするか。

        ## 対象テキスト (抜粋)
        {text[:15000]}
        """
        res_text = llm.generate(prompt)
        return res_text
    except Exception as e:
        return f"Error: {e}"

def process_news_item(item):
    title = item['title']
    link = item['link']
    desc = item['summary']
    
    # Clean HTML roughly
    clean_desc = re.sub('<[^<]+?>', '', html.unescape(desc))
    
    print(f"\n📰 {title}")
    print(f"   {clean_desc[:200]}...")
    
    # Use link hash as rough ID
    nid = link[-11:] if len(link)>11 else "news_item"
    
    print("\n🤖 Generating Article Summary...")
    summary_text = summarize_text(f"Title: {title}\nContent: {clean_desc}", mode="news")
    display_summary(summary_text)

    while True:
        print("\n[NEWS ACTIONS]")
        print("U: 🌌 Launch to Universe")
        print("B: Back")
        act = input("> ").strip().lower()
        
        if act == 'b': break
        elif act == 'u':
            print("\n🌌 Architect is reading the article...")
            existing_nodes = universe_manager.get_node_summaries()
            result = architect.generate_universe_node(f"{title}\n{clean_desc}", title, existing_nodes)
            if "error" in result:
                print(f"   💥 Launch Failure: {result['error']}")
            else:
                try:
                    meta = result["node_metadata"]
                    links = result["gravity_links"]
                    nid, ntitle = universe_manager.add_node(meta, links)
                    print(f"\n   🌟 STAR BORN: [{nid}] {ntitle}")
                    print(f"      Group: {meta.get('group')}")
                    print(f"      Importance: {meta.get('importance_score')}/10")
                    print(f"      Gravity Links: {len(links)} connections established.")
                except Exception as e:
                    print(f"   💥 Data Parsing Error: {e}")


def handle_news_source(source_tuple):
    name, url = source_tuple
    print(f"Fetching {name}...")
    ftitle, items = get_rss_feed(url)
    if not items:
        print(f"❌ Failed to fetch feed.")
        return
        
    for i, item in enumerate(items[:5]):
        print(f"[{i+1}] {item['title']}")
    
    while True:
        nsel = input("\nSelect Article [1-5] / (B)ack > ").strip()
        if nsel.lower() == 'b': break
        try:
            idx = int(nsel)-1
            if 0 <= idx < len(items[:5]): process_news_item(items[idx])
        except ValueError: pass

def launch_to_universe(title, content, source_type="general", interactive=False):
    """
    Core Antigravity Logic: Analyze content -> Generate Node -> Save to Universe.
    """
    print(f"\n   🚀 Launching to Universe: {title[:40]}...")
    
    # 1. Get Existing Context
    existing_nodes = universe_manager.get_node_summaries()
    
    # 2. Architect Analysis
    result = architect.generate_universe_node(content, title, existing_nodes)
    
    # 3. Handle Result
    if "error" in result:
        print(f"   💥 Launch Failure: {result['error']}")
        return False
    else:
        try:
            meta = result["node_metadata"]
            links = result["gravity_links"]
            nid, ntitle = universe_manager.add_node(meta, links)
            
            # Check if duplicate was detected
            if nid is None:
                print(f"      ⏭️  SKIPPED: Duplicate content")
                return False
            
            print(f"      🌟 STAR BORN: [{nid}] {ntitle}")
            print(f"         Group: {meta.get('group')}")
            print(f"         Gravity: {len(links)} links.")
            
            # --- SHUKATSU TASK INTEGRATION ---
            shukatsu_task = result.get("shukatsu_task", {})
            if shukatsu_task.get("detected") is True:
                 try:
                     task_name = shukatsu_task.get("task_name")
                     task_date = shukatsu_task.get("date")
                     priority = shukatsu_task.get("priority", 5)
                     
                     if task_name and task_date and task_date != "null":
                         print(f"      💼 SHUKATSU ITEM DETECTED: {task_name} -> {task_date}")
                         
                         # Update Calendar JSON
                         CAL_FILE = os.path.abspath(os.path.join(BASE_DIR, "../schedule_magi/precog_schedules.json"))
                         # Ensure Path (Fallback if relative path is messy)
                         if not os.path.exists(CAL_FILE):
                              CAL_FILE = os.path.join(DATA_DIR, "../../data/precog_schedules.json")
                         
                         cal_data = []
                         if os.path.exists(CAL_FILE):
                             with open(CAL_FILE, "r", encoding="utf-8") as f:
                                 cal_data = json.load(f)
                                 
                         new_entry = {
                             "Date": task_date,
                             "Time": "09:00", # Default start
                             "Event": f"[就活] {task_name}",
                             "Type": "JOB",
                             "Priority": priority,
                             "Status": "Pending"
                         }
                         
                         # Deduplicate simple check
                         is_dup = any(d.get("Date") == task_date and d.get("Event") == new_entry["Event"] for d in cal_data)
                         if not is_dup:
                             cal_data.append(new_entry)
                             with open(CAL_FILE, "w", encoding="utf-8") as f:
                                 json.dump(cal_data, f, ensure_ascii=False, indent=4)
                             print(f"         ✅ Added to Calendar: {task_date}")
                         else:
                             print(f"         ℹ️  Already in Calendar.")
                             
                 except Exception as cal_err:
                     print(f"         ⚠️ Calendar Sync Failed: {cal_err}")
            
            return True
        except Exception as e:
            print(f"   💥 Data Parsing Error: {e}")
            return False



# --- CLI Main Loop ---




def process_channel(channel_id):
    print(f"\n📡 Fetching feed for {channel_id}...")
    title, videos = get_channel_feed(channel_id)
    
    if not videos or not isinstance(videos, list):
        print(f"❌ Failed to fetch: {title or 'Unknown'} ({videos if isinstance(videos, str) else 'No data'})")
        return

    print(f"\n📺 CHANNEL: {title}")
    for i, v in enumerate(videos):
        print(f"[{i+1}] {v['title']} ({v['published']})")
    
    while True:
        sel = input("\nSelect Video [1-15] / (B)ack > ").strip().lower()
        if sel == 'b':
            break
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(videos):
                process_video(videos[idx])
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input.")

def process_video(video):
    vid = video['id']
    title = video['title']
    
    # Check cache
    memos = load_memos()
    existing = memos.get(vid)
    summary_text = ""
    transcript_cache = "" # Keep transcript for Universe injection
    
    print(f"\n📽️ {title}")
    
    if existing:
        print("✅ Found existing summary.")
        summary_text = existing['summary']
        display_summary(summary_text)
        # Try to re-fetch transcript if needed for universe? 
        # Ideally we should strictly cache transcript too, but for now we might fetch again if user wants Universe.
    else:
        print("🤖 Generating summary... (This may take a moment)")
        transcript = get_transcript(vid)
        transcript_cache = transcript # Save
        
        if transcript == "RATE_LIMITED":
            summary_text = summarize_video_direct(vid, title)
        elif transcript:
            summary_text = summarize_text(transcript)
        else:
            # Fallback: Try comments
            print("💬 No transcript. Trying top comments for context...")
            comments = get_comments(vid)
            if comments:
                summary_text = summarize_text(f"【COMMENTS CONTEXT】\n{comments}")
            else:
                print("❌ No context (transcript/comments) available for this video.")
                return
            
        display_summary(summary_text)
        
        # Auto-save
        save_memo(vid, title, summary_text)

    # Note taking & Actions
    while True:
        print("\n[ACTIONS]")
        print("D: Decompress (Deep Read)")
        print("N: Note")
        print("U: 🌌 Launch to Universe (Antigravity)")
        print("J: JobHQ Export")
        print("B: Back")
        
        act = input("> ").strip().lower()
        
        if act == 'b':
            break
        elif act == 'd':
            parts = summary_text.split("---EGO_SEPARATOR---")
            if len(parts) >= 2: # Changed from 3 to 2 based on diff
                print("\n📖 === DECOMPRESSED VIEW ===")
                print(textwrap.fill(parts[2].strip(), width=80))
            else:
                print(summary_text) # Fallback
        elif act == 'n':
            note = input("Write Note > ")
            save_memo(vid, title, summary_text, note)
        elif act == 'j':
            # Job Export
            memo_data = load_memos().get(vid, {})
            current_note = memo_data.get('note', '')
            export_to_kcard(vid, title, summary_text, current_note)
        elif act == 'u':
            print("\n🌌 Preparing simple rocket...")
            # Need transcript
            tx = transcript_cache
            if not tx or len(tx) < 100:
                print("   Re-fetching transcript for deep analysis...")
                tx = get_transcript(vid)
                
            if not tx or tx == "RATE_LIMITED" or len(tx) < 100:
                print("❌ Cannot launch: No high-quality transcript available.")
                continue
                
            print("   🔭 Architect is observing the universe...")
            existing_nodes = universe_manager.get_node_summaries()
            
            print("   🚀 3... 2... 1... Launching!")
            result = architect.generate_universe_node(tx, title, existing_nodes)
            
            if "error" in result:
                print(f"   💥 Launch Failure: {result['error']}")
            else:
                try:
                    meta = result["node_metadata"]
                    links = result["gravity_links"]
                    # Add to universe
                    nid, ntitle = universe_manager.add_node(meta, links)
                    print(f"\n   🌟 STAR BORN: [{nid}] {ntitle}")
                    print(f"      Group: {meta.get('group')}")
                    print(f"      Importance: {meta.get('importance_score')}/10")
                    print(f"      Gravity Links: {len(links)} connections established.")
                except Exception as e:
                    print(f"   💥 Data Parsing Error: {e}")

def display_summary(text):
    parts = text.split("---EGO_SEPARATOR---")
    print("\n📦 === COMPRESSED HEADER ===")
    if len(parts) >= 2: # Changed from 3 to 2 based on diff
        # Show compressed part
        print(parts[1].strip())
    else:
        # Fallback simple show
        print(text[:300] + "...")

def view_memos():
    memos = load_memos()
    print(f"\n📝 Saved Memos: {len(memos)}")
    for k, v in memos.items():
        print(f"- {v['title']} ({v['timestamp']})")
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Handle command line arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if "--continuous" in args or "patrol" in args:
        # RANDOM CONTINUOUS PATROL - No menu, direct collection
        print("🔄 RANDOM CONTINUOUS PATROL MODE")
        print("   Collecting from ALL genres automatically...")
        print("   Press Ctrl+C to stop.\n")
        
        chaos_mode = "--chaos" in args or "chaos" in args
        
        cycle = 1
        while True:
            try:
                # Alternate between standard and chaos modes for variety
                use_chaos = chaos_mode or (cycle % 2 == 0)  # Every other cycle uses chaos
                mode_str = "CHAOS" if use_chaos else "STANDARD"
                print(f"\n🌀 ===[ CYCLE {cycle} | MODE: {mode_str} ]===")
                
                do_patrol(auto_launch=True, chaos_mode=use_chaos)
                
                print(f"\n💤 Cycle {cycle} complete. Sleeping 60 seconds...")
                cycle += 1
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n🛑 Patrol Stopped by User.")
                break
            except Exception as e:
                print(f"⚠️ Error in patrol loop: {e}")
                relay.report(e, context="Continuous Patrol Loop")
                time.sleep(10)
                
    elif "--auto" in args:
        print("\n⚠️ NOTICE: Old Auto-mode moved to 'watcher_youtube.py'.")
        print("Redirecting to main.")
        main()
    elif "--auto-universe" in args:
        # User requested immediate Auto-Patrol
        do_patrol(auto_launch=True)
    elif "--quiet" in args:
        # Silent auto patrol (single run)
        do_patrol(auto_launch=True, chaos_mode=False)
    else:
        main()

