
"""
Liberal Arts Patrol (Deep Knowledge)
====================================
Targets specific intellectual sources: Philosophy, History, Science, and Social Structures.
Designed to run independently from the main Job Hunting Patrol.
"""
import os
import sys
import json
import time
import random
import urllib.request
import urllib.parse
from datetime import datetime
import xml.etree.ElementTree as ET

# Attempt to reuse functions from main patrol if available, otherwise redefine simplified versions
# Attempt to reuse functions from main patrol if available
base_data_path = None
for root_name in ["EGO_SYSTEM_FILES", "VECTIS_SYSTEM_FILES"]:
    possible_path = os.path.join(os.path.dirname(__file__), root_name, "apps/MEDIA/INTELLIGENCE_HUB")
    if os.path.exists(possible_path):
        sys.path.append(possible_path)
        base_data_path = os.path.join(possible_path, "data/shukatsu")
        break

OUTPUT_DIR = base_data_path if base_data_path else os.path.join(os.path.dirname(os.path.abspath(__file__)), "shukatsu_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Kiwix Bridge (EGO Expansion)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "VECTIS_SYSTEM_FILES/apps/MEDIA/kiwix"))
    from kiwix_bridge import KiwixBridge
    HAS_KIWIX = True
except ImportError:
    HAS_KIWIX = False

# Sources
LIBERAL_ARTS_SOURCES = {
    "83": ("National Geographic JP", "https://natgeo.nikkeibp.co.jp/rss/index.xml"),
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EGO_SYSTEM_FILES/apps/MEDIA/INTELLIGENCE_HUB/data/shukatsu") # Share same data dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_rss_feed(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        items = []
        all_items = root.findall('.//item') + root.findall('.//{http://www.w3.org/2005/Atom}entry')
        for entry in all_items[:10]:
             t = entry.find('title')
             title = t.text if t is not None else "No Title"
             l = entry.find('link')
             link = l.text if l is not None else ""
             items.append({'title': title, 'link': link, 'source': 'Liberal Arts'})
        return items
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    print("🏛️ === Liberal Arts & Deep Knowledge Patrol ===")
    print("   Focus: Philosophy, History, Science, Social Structure")
    
    while True:
        try:
            total_hits = 0
            for key, (name, url) in LIBERAL_ARTS_SOURCES.items():
                print(f"   Searching: {name}...", end="\r")
                items = get_rss_feed(url)
                
                # Save immediately if new
                for item in items:
                    # Simple check
                    # In a real scenario we'd check processed IDs, but for simplicity here we just print
                    pass
                
                if items:
                    print(f"   ✅ {name}: {len(items)} items found.")
                    
                    # [EGO EXPANSION] Kiwix Enrichment
                    if HAS_KIWIX:
                        kb = KiwixBridge()
                        if kb.is_active:
                            for item in items[:1]: # Check top item only to save time
                                # Simplistic keyword extraction (Title first word)
                                keyword = item['title'].split()[0] 
                                if len(keyword) > 3:
                                    res = kb.search(keyword)
                                    if res:
                                        print(f"      🥝 [EGO REF] Knowledge found in Local Wiki: {res['title']}")
                    
                    total_hits += len(items)
                time.sleep(2) # Polite delay
            
            print(f"\n   Cycle complete. Found {total_hits} potential intellectual artifacts.")
            print("   Waiting for next deep dive cycle (5 minutes)...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n   Patrol stopped.")
            break
        except Exception as e:
            print(f"   Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
