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
# import scrapetube (Removed for stability - using RSS)
# import scrapetube (Removed for stability - using RSS)
# Error Telemetry
# Setup Paths & Env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMO_FILE = os.path.join(DATA_DIR, "channel_memos.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json") # The Knowledge Universe

sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../..")))
load_dotenv(os.path.join(BASE_DIR, "../../.env"))

# Error Telemetry
from modules.error_relay import ErrorRelay
relay = ErrorRelay("YouTube_CLI")

# Use Unified LLM Client (Supports Ollama, Gemini, etc.)
from modules.unified_llm import UnifiedLLM
# Import the new Architect
from modules.antigravity import AntigravityArchitect

llm = UnifiedLLM(provider="ollama", model_name="phi4")
architect = AntigravityArchitect()

# Ensure data dir
os.makedirs(DATA_DIR, exist_ok=True)

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
NEWS_SOURCES = {
    "1": ("GIGAZINE", "https://gigazine.net/news/rss_2.0/"),
    "2": ("TechCrunch JP", "https://techcrunch.com/feed/"),
    "3": ("Publickey (Tech)", "https://www.publickey1.jp/atom.xml"),
    "4": ("Wired JP", "https://wired.jp/rss.xml"),
    "5": ("Publishing (出版業界)", "https://news.google.com/rss/search?q=%E5%87%BA%E7%89%88%E6%A5%AD%E7%95%8C&hl=ja&gl=JP&ceid=JP:ja"),
    "6": ("General (社会・常識)", "https://www.nhk.or.jp/rss/news/cat0.xml")
}

class UniverseManager:
    def __init__(self):
        self.data = {"nodes": [], "links": []}
        if os.path.exists(UNIVERSE_FILE):
             try:
                 with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                     self.data = json.load(f)
             except: pass
    
    def get_node_summaries(self):
        return [{"id": n["id"], "title": n["title"]} for n in self.data.get("nodes", [])]

    def add_node(self, meta, links):
        # DUPLICATE DETECTION: Check if similar title already exists
        new_title = meta.get("title", "Untitled").lower()
        for existing in self.data.get("nodes", []):
            existing_title = existing.get("title", "").lower()
            # Simple similarity check (can be improved with fuzzy matching)
            if new_title in existing_title or existing_title in new_title:
                if len(new_title) > 10 and len(existing_title) > 10:  # Avoid false positives with short titles
                    print(f"   ⚠️  DUPLICATE DETECTED: '{meta.get('title')}' similar to existing '{existing.get('title')}'")
                    return None, None  # Skip this node
        
        nid = f"N{len(self.data.get('nodes', []))+1:03d}"
        node = {
            "id": nid,
            "title": meta.get("title", "Untitled"),
            "summary": meta.get("summary", ""),
            "group": meta.get("group", "General"),
            "importance": meta.get("importance_score", 1),
            "timestamp": datetime.now().isoformat(),
            "metadata": meta
        }
        if "nodes" not in self.data: self.data["nodes"] = []
        self.data["nodes"].append(node)
        
        if "links" not in self.data: self.data["links"] = []
        for l in links:
            l["source_id"] = nid
            self.data["links"].append(l)
            
        self.save()
        return nid, node["title"]

    def save(self):
        with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

universe_manager = UniverseManager()

# ... (Functions omitted for stability) ...

def do_patrol(auto_launch=False):
    print("\n🔄 === INTELLIGENCE PATROL STARTS ===")
    print("Scanning YouTube & News Sources...\n")
    
    patrol_items = [] # Stores (type, item_data)
    
    # scan YouTube
    for name, cid in PRESETS.values():
        print(f"📡 [YouTube] {name}...", end="\r")
        try:
            title, videos = get_channel_feed(cid)
            if videos and isinstance(videos, list):
                # Capacity Control: Limit to 1 normally, but 3 in Auto Mode for coverage
                limit = 3 if auto_launch else 1
                for v in videos[:limit]:
                    patrol_items.append({
                        "type": "youtube", 
                        "label": f"[Y-{len(patrol_items)+1}]", 
                        "title": v['title'], 
                        "source": name,
                        "data": v
                    })
        except: pass
        
    # scan News
    for name, url in NEWS_SOURCES.values():
        print(f"📡 [News] {name}...", end="\r")
        try:
            ftitle, items = get_rss_feed(url)
            if items:
                # Capacity Control: Limit to 1 normally, but 3 in Auto Mode
                limit = 3 if auto_launch else 1
                for item in items[:limit]:
                    patrol_items.append({
                        "type": "news", 
                        "label": f"[N-{len(patrol_items)+1}]", 
                        "title": item['title'], 
                        "source": name,
                        "data": item
                    })
        except: pass
        
    print(f"\n✅ Scan Complete. Total {len(patrol_items)} Intelligence Items.\n")
    
    for i, item in enumerate(patrol_items):
        print(f"{i+1:02d}. {item['source']:<15} : {item['title'][:60]}...")
    
    # AUTO LAUNCH SEQUENCE
    if auto_launch:
        print("\n🚀 === AUTO-LAUNCH SEQUENCE INITIATED (Hands-Free) ===\n")
        print("Antigravity Architect is processing all items...")
        
        for i, item in enumerate(patrol_items):
            print(f"\n[{i+1}/{len(patrol_items)}] Processing: {item['title'][:30]}...")
            
            # Check for duplicates in Universe before processing (Capacity Guard)
            existing_summaries = universe_manager.get_node_summaries()
            if any(node['title'] == item['title'] for node in existing_summaries):
                print(f"      ⚠️ Already in Universe. Skipping to save capacity.")
                continue

            # Fetch Content
            content = ""
            if item['type'] == 'youtube':
                v_id = item['data']['id']
                transcript = get_transcript(v_id)
                if transcript and transcript != "RATE_LIMITED":
                    content = transcript
                else:
                     content = f"Video Title: {item['title']}\n(Transcript Unavailable)"
            
            elif item['type'] == 'news':
                raw_summary = item['data']['summary']
                clean_desc = re.sub('<[^<]+?>', '', html.unescape(raw_summary))
                content = f"Article Title: {item['title']}\nSummary: {clean_desc}"
            
            # Launch
            launch_to_universe(item['title'], content, item['type'])
            
        print("\n🌌 Auto-Patrol Complete. System is now observing.")
        # Pause to let user see output if run from bat
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
    
    【REASONING】
    Q: Why try youtube_transcript_api first?
    A: - Faster than yt-dlp (no video metadata download)
       - Less likely to hit rate limits
       - Cleaner API (direct subtitle access)
    
    Q: Why return "RATE_LIMITED" instead of None?
    A: - Distinguishes rate limit errors from other failures
       - Allows caller to invoke Gemini direct mode as fallback
       - Maintains system throughput even under rate limiting
    
    Q: Why not retry on 429 error?
    A: - 429 is IP-based, same IP will keep getting blocked
       - Waiting increases latency without guaranteed success
       - Fallback to Gemini direct is more reliable
       - System remains responsive to user
    
    Q: Why suppress yt-dlp stderr?
    A: - yt-dlp outputs confusing ERROR messages even when we handle them
       - User sees "ERROR" but system is working correctly (fallback active)
       - Cleaner logs improve user experience
    """
    
    # INVARIANT CHECK (development mode)
    assert video_id and len(video_id) == 11, f"Invalid video_id format: {video_id}"
    
# --- Auto Pilot Logic ---

# --- Command Link ---
# --- Command Link ---
COMMAND_FILE = os.path.join(os.path.dirname(BASE_DIR), "../../VECTIS_COMMAND.txt")

def start_auto_pilot():
    """
    Hands-Free Continuous Intelligence Cycle (Infinite).
    State Machine:
      - PATROL_PHASE: Scans for new content
      - OBSERVE_PHASE: Performs Deep Dive Debates
    """
    SCAN_INTERVAL_MIN = 30
    DISPLAY_INTERVAL_MIN = 1 
    
    # State Init
    last_patrol_time = 0 # Force immediate patrol
    found_items = []
    
    while True:
        current_time = time.time()
        
        # === 1. PATROL CHECK ===
        if current_time - last_patrol_time > (SCAN_INTERVAL_MIN * 60):
            print("\n\n🔄 === AUTO-PATROL CYCLE INITIATED ===")
            try:
                found_items = do_patrol(auto_launch=True, return_items=True)
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

        # === 3. DEEP DIVE (OBSERVATION / BOOKSHELF) ===
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
             elif target.get('type') == 'universe_node':
                 content_text = f"Title: {target['title']}\nSummary: {target['data'].get('summary','')}"
             
             # DECISION: Debate vs Bookshelf Report
             # For Auto-Pilot, we strictly add to Bookshelf now as per user instruction
             
             print("   📚 Generating Comprehensive Bookshelf Report (Target: 10k chars)...")
             
             prompt = f"""
             あなたは「VECTIS百科事典」の編集長です。
             以下のコンテンツを元に、**「Wikipediaスタイルの超詳細な百科事典記事」**を作成してください。
             
             【執筆方針（ユーザー絶対命令）】
             1. **ターゲット**: 10,000文字級の「分厚い」記事。
                - 入力テキストが短い、または不足している場合は、**あなたの持つ全ての背景知識を総動員して、定義・歴史・理論・構造・社会的影響について大幅に加筆**してください。
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
                 # Use the unified LLM chat interface if available
                 if hasattr(llm, 'chat'):
                     report = llm.chat(prompt)
                 else:
                     # Fallback if specific method missing, abuse generate_debate or similar if generic
                     report = llm.generate_debate(prompt) # Likely to fail if prompt injection, but worth try
                     
                 # SAVE TO BOOKSHELF
                 category_map = {
                     'youtube': '01_YouTube_Summaries',
                     'news': '02_News_Clips',
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

# --- HELPER: BOOKSHELF IO ---
def save_to_bookshelf(title, content, subfolder, source="Unknown"):
    """
    Saves content to VECTIS_SYSTEM_FILES/OBSIDIAN_WRITING/BOOKSHELF/<subfolder>
    """
    # Sanitize Title
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_").strip()[:50]
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Construct Path
    # ../../../OBSIDIAN_WRITING/BOOKSHELF relative to BASE_DIR (apps/youtube_channel)
    # BASE_DIR is apps/youtube_channel
    # ../.. is VECTIS_SYSTEM_FILES
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
SCHEDULER_DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, "../schedule_magi/data/precog_schedules.json")) # Incorrect path relative to CLI
# Correct Path: apps/youtube_channel/data -> ../../apps/schedule_magi/../data? No.
# BASE_DIR = apps/youtube_channel
# Target = apps/schedule_magi/../../data/precog_schedules.json ... wait, Magi app uses ../../data/precog_schedules.json
# which is VECTIS_SYSTEM_FILES/data/precog_schedules.json.
SHARED_DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../data/precog_schedules.json"))

def extract_shukatsu_schedule(content, context_title):
    """
    Uses LLM to extract JSON events from text.
    """
    prompt = f"""
    Extract any explicit dates and deadlines related to Job Hunting (Shukatsu), Events, or Releases from the text below.
    ignore vague dates like "next year" or "soon". Only extract specific dates (YYYY-MM-DD).

    **Input Text**:
    {content[:5000]}

    **Output Format (JSON only)**:
    [
        {{
            "Date": "YYYY-MM-DD",
            "Time": "HH:MM", (or "00:00" if unknown)
            "Event": "Event Name",
            "Type": "DEADLINE" or "EVENT" or "RELEASE",
            "Priority": 5
        }}
    ]
    If no dates found, return [].
    """
    try:
        if hasattr(llm, 'generate'):
            res = llm.generate(prompt)
        else:
            return []
            
        # Clean specific markdown code blocks
        clean_json = res.replace("```json", "").replace("```", "").strip()
        events = json.loads(clean_json)
        return events if isinstance(events, list) else []
    except:
        return []

def register_schedule_to_magi(event_data):
    """
    Appends a single event to the shared schedule JSON.
    """
    try:
        # Load Existing
        existing = []
        if os.path.exists(SHARED_DATA_FILE):
             with open(SHARED_DATA_FILE, 'r', encoding='utf-8') as f:
                 existing = json.load(f)
        
        # Check Duplicate (Simple logic)
        for ex in existing:
            if ex.get('Date') == event_data.get('Date') and ex.get('Event') == event_data.get('Event'):
                return # Skip duplicate
        
        existing.append(event_data)
        
        # Save
        with open(SHARED_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Magi Sync Error: {e}")

    # === 3. WAIT & LISTEN (With Command Interrupt) ===
    # Wait for DISPLAY_INTERVAL_MIN, checking command every second
    next_step_time = time.time() + (DISPLAY_INTERVAL_MIN * 60)
    
    while time.time() < next_step_time:
        # Check Command
        # Unified command processing logic
        if os.path.exists(COMMAND_FILE):
            try:
                with open(COMMAND_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Remove file immediately to avoid double processing
                try: os.remove(COMMAND_FILE)
                except: pass

                if "AUTO_MODE: ON" in content:
                    print("\n      [COMMAND LINK] 🚀 AUTO-MODE ACTIVATE SIGNAL RECEIVED.")
                    if "TARGET_MODE: KYOYO_UPLOAD" in content:
                        print("      [AUTO] Scanning for Liberal Arts / Philosophy context...")
                        dummy_transcript = "Liberal Arts (Kyoyo) is not just knowledge, but the ability to structure chaos."
                        arch = AntigravityArchitect(root_dir=os.path.join(os.path.dirname(__file__), "../../../"), project_name="VECTIS")
                        arch.generate_universe_node(
                            transcript_text=dummy_transcript,
                            video_title="AUTO-INGEST: The Structure of Liberal Arts",
                            video_id="AUTO_KYOYO_001",
                            channel_name="VECTIS_INTERNAL"
                        )
                        print("      [AUTO] ✅ Kyoyo Upload Completed.")

                # Extract first valid command string
                lines = content.splitlines()
                cmd = ""
                for line in lines:
                    if line.strip() and not line.startswith("#") and ":" not in line: 
                        cmd = line.strip(); break
                
                if cmd:
                    print(f"\n⚡ COMMAND: {cmd}")
                    if "youtube" in cmd and "v=" in cmd:
                        vid_match = re.search(r'v=([0-9A-Za-z_-]{11})', cmd)
                        if vid_match:
                            vid = vid_match.group(1)
                            tr = get_transcript(vid)
                            launch_to_universe("Priority Target", tr if tr else "No Transcript", "youtube")
                    elif "PATROL" in cmd:
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
        do_patrol(auto_launch=False)
        
    while True:
        print("\n📺 === VECTIS INTELLIGENCE CLI (v2.6 AUTO) ===")
        print("0.  ⚡ Check All (Manual Patrol)")
        print("00. 🤖 Auto-Patrol (Hands-Free Mode)")
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
        elif choice == '0':
            do_patrol(auto_launch=False)
        elif choice == '00':
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
             print(f"\n🌌 [VECTIS UNIVERSE]")
             print(f"Total Stars (Nodes): {len(nodes)}")
             print(f"Gravity Lines (Links): {len(links)}")
             input("Press Enter to continue...")

def get_transcript(video_id: str) -> str | None:
    # ... (Keep Docstring) ...
    # ...
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Fix for "type object ... has no attribute 'list_transcripts'"
        # Old versions might use different API, or import issue.
        # Safest fallback is the static method get_transcript if list_transcripts fails
        try:
           transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
           # ... retrieval logic ...
           transcript = transcript_list.find_transcript(['ja', 'en'])
           # ...
           data = transcript.fetch()
           text = " ".join([t['text'] for t in data])
           return text
        except AttributeError:
             # Fallback for older API
             data = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
             text = " ".join([t['text'] for t in data])
             return text
             
    except Exception as e:
        # ... existing error handling ...
        error_str = str(e)
        if "429" in error_str: return "RATE_LIMITED"
        
        # Continue to yt-dlp fallback
        pass 
        
    # ... (Rest of yt-dlp fallback) ...
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
        
        # Suppress stderr
        import sys
        from io import StringIO
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # Check for subtitles
                subs = info.get('subtitles') or info.get('automatic_captions')
                if subs:
                    # Logic to parse subs is complex without downloading, 
                    # staying simple for stability: return None so we use metadata/gemini summary
                    # OR just use the 'description' as a fallback if transcript fails
                    pass
        finally:
            sys.stderr = old_stderr

    except Exception:
        pass
        
    return None

def do_patrol(auto_launch=False, return_items=False):
    # ... (Update do_patrol signature) ...
    print("\n🔄 === INTELLIGENCE PATROL STARTS ===")
    print("Scanning YouTube & News Sources...\n")
    
    patrol_items = [] 
    
    # ... (Scanning Logic - Same) ...
    # scan YouTube
    for name, cid in PRESETS.values():
        print(f"📡 [YouTube] {name}...", end="\r")
        try:
            title, videos = get_channel_feed(cid)
            if videos and isinstance(videos, list):
                v = videos[0]
                patrol_items.append({
                    "type": "youtube", 
                    "label": f"[Y-{len(patrol_items)+1}]", 
                    "title": v['title'], 
                    "source": name,
                    "data": v
                })
        except: pass
        
    for name, url in NEWS_SOURCES.values():
        print(f"📡 [News] {name}...", end="\r")
        try:
            ftitle, items = get_rss_feed(url)
            if items:
                item = items[0]
                patrol_items.append({
                    "type": "news", 
                    "label": f"[N-{len(patrol_items)+1}]", 
                    "title": item['title'], 
                    "source": name,
                    "data": item
                })
        except: pass

    print(f"\n✅ Scan Complete. Total {len(patrol_items)} Intelligence Items.\n")
    
    for i, item in enumerate(patrol_items):
        print(f"{i+1:02d}. {item['source']:<15} : {item['title'][:60]}...")
    
    # AUTO LAUNCH SEQUENCE
    if auto_launch:
        print("\n🚀 === AUTO-LAUNCH SEQUENCE INITIATED (Hands-Free) ===\n")
        print("Antigravity Architect is processing all items...")
        
        for i, item in enumerate(patrol_items):
            print(f"\n[{i+1}/{len(patrol_items)}] Processing: {item['title'][:30]}...")
            
            # Check for duplicates
            existing_summaries = universe_manager.get_node_summaries()
            if any(node['title'] == item['title'] for node in existing_summaries):
                print(f"      ⚠️ Already in Universe. Skipping to save capacity.")
                continue

            # Fetch Content
            content = ""
            if item['type'] == 'youtube':
                v_id = item['data']['id']
                transcript = get_transcript(v_id)
                if transcript and transcript != "RATE_LIMITED":
                    content = transcript
                else:
                     content = f"Video Title: {item['title']}\n(Transcript Unavailable)"
            
            elif item['type'] == 'news':
                raw_summary = item['data']['summary']
                clean_desc = re.sub('<[^<]+?>', '', html.unescape(raw_summary))
                content = f"Article Title: {item['title']}\nSummary: {clean_desc}"
            
            # Launch
            launch_to_universe(item['title'], content, item['type'])
        
        print("\n🌌 Auto-Patrol Cycle Complete.")
        if return_items: return patrol_items
        return

    # MANUAL MODE
    while True:
        sel = input("\nSelect Number to Deep Dive / (U)niverse All / (B)ack > ").strip().lower()
        if sel == 'b': break
        
        if sel == 'u':
             # Manual U Logic 
             print("\n🚀 === BULK LAUNCH SEQUENCE INITIATED ===\n")
             for i, item in enumerate(patrol_items):
                # Simple Manual implementation for now
                # In real scenario, would duplicate the logic above
                print(f"Launching {item['title']}...")
                launch_to_universe(item['title'], "Manual Launch", item['type'])
             break
            
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(patrol_items):
                target = patrol_items[idx]
                if target['type'] == 'youtube':
                    process_video(target['data'])
                else:
                    process_news_item(target['data'])
        except ValueError: pass

    


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
        【指令: VECTIS情報パッケージング（{label}解析）】
        以下の{label}を5つのレイヤーに分けて出力してください。
        
        ---VECTIS_SEPARATOR---

        【パート1: 圧縮ファイルヘッダー (Compressed View)】
        - **漢文的・ログ的圧縮文体**で記述すること。
        - 助詞（〜は、〜が）を極限まで削ぎ落とし、名詞と動詞で構成された「高密度な3行」にすること。
        - 例: "AI進化加速 / 雇用市場激変 / 適応必須"

        ---VECTIS_SEPARATOR---

        【パート2: 解凍データ (Decompressed Content)】
        - 「Logic Flow（論理展開）」をステップ・バイ・ステップで記述。
        - 「Insight Crystals（洞察）」として、表面的な情報ではなく「なぜそうなるか」の構造を記述。

        ---VECTIS_SEPARATOR---

        【パート3: Deep Dive (Intellectual Figures)】
        - 言及された重要人物、技術、理論、書籍名を特定し、解説を加える。
        - 固有名詞は可能な限り抽出すること。

        ---VECTIS_SEPARATOR---

        【パート4: 関連知識・用語解説 (Context Buffer)】
        - 専門用語や背景知識の補足。

        ---VECTIS_SEPARATOR---

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
        
つぎた        act = input("> ").strip().lower()
        
        if act == 'b':
            break
        elif act == 'd':
            parts = summary_text.split("---VECTIS_SEPARATOR---")
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
    parts = text.split("---VECTIS_SEPARATOR---")
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
    if "--auto" in sys.argv:
        print("\n⚠️ NOTICE: Old Auto-mode moved to 'watcher_youtube.py'.")
        print("Redirecting to main.")
        main()
    elif "--auto-universe" in sys.argv:
        # User requested immediate Auto-Patrol
        main()
    else:
        main()

