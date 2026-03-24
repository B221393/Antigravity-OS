import requests
from bs4 import BeautifulSoup
import json
import os

NEWS_URL = "https://news.kddi.com/kddi/corporate/newsrelease/2026/index.html"
CACHE_PATH = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data\kddi_intelligence_cache.json"

def update_kddi_news():
    print(f"Fetching KDDI news from {NEWS_URL}...")
    try:
        # User-agent to avoid blocks
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(NEWS_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch news: Status {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # KDDI's news list structure (heuristic based on common patterns)
        news_items = soup.select('.news-list-item') or soup.select('.list h4')
        
        updates = []
        for item in news_items[:5]: # Get latest 5
            text = item.get_text().strip()
            updates.append(text)
            print(f"Found: {text}")

        # Update cache
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            cache['intelligence_updates'] = updates
            
            with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            print("Cache updated.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_kddi_news()
