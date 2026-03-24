
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_mynavi_data():
    print(f"📡 [MyNavi] Scanning official site...", end="\n")
    items = []
    base_url = "https://job.mynavi.jp"
    
    # 1. Top Page for Rankings/Pickup
    try:
        url = "https://job.mynavi.jp/2027/"
        req = urllib.request.Request(url, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            
            # Optimized Ranking Search
            # Find text nodes containing "ランキング"
            targets = soup.find_all(string=re.compile("ランキング"))
            seen_links = set()
            
            for t in targets:
                # Go up to finding a container (limit parents to avoid whole body)
                container = t.find_parent(['div', 'section', 'ul', 'dl'])
                if container:
                     links = container.find_all('a')
                     for a in links:
                         href = a.get('href', '')
                         if 'corpinfo' in href and href not in seen_links:
                             items.append({
                                 'title': f"[MyNavi Rank] {a.get_text(strip=True)}",
                                 'link': urllib.parse.urljoin(base_url, href),
                                 'summary': "マイナビ アクセスランキング掲載企業",
                                 'source': "MyNavi Ranking",
                                 'image_url': ""
                             })
                             seen_links.add(href)
                             if len(items) > 10: break # Limit
                if len(items) > 10: break
    except Exception as e:
        print(f"   [MyNavi Top Error] {e}")

    # 2. Event Page
    try:
        url_evt = "https://job.mynavi.jp/conts/2027/event/index.html"
        req = urllib.request.Request(url_evt, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            
            for a in soup.find_all('a'):
                txt = a.get_text(strip=True)
                href = a.get('href', '')
                if "event" in href and len(txt) > 5:
                    # Generic broad catch for now to verify
                    if any(k in txt for k in ["関西", "兵庫", "東京", "EXPO"]):
                        items.append({
                             'title': f"[MyNavi Event] {txt}",
                             'link': urllib.parse.urljoin(base_url, href),
                             'summary': "マイナビ主催イベント情報",
                             'source': "MyNavi Event",
                             'image_url': ""
                         })
    except Exception as e:
         print(f"   [MyNavi Event Error] {e}")
         
    return items

if __name__ == "__main__":
    items = get_mynavi_data()
    print(f"\nFound {len(items)} items:")
    for item in items[:5]:
        print(f"- {item['title']} ({item['link']})")
