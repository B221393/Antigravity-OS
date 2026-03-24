
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import sys
import random

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def get_random_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_mynavi_data():
    """マイナビ2027からランキングとイベント情報を取得 (Direct Scrape)"""
    print(f"📡 [MyNavi] Scanning official site...", end="\n")
    items = []
    base_url = "https://job.mynavi.jp"
    
    # 1. Top Page for Rankings/Pickup
    try:
        url = "https://job.mynavi.jp/2027/"
        req = urllib.request.Request(url, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            
            # Rankings: Look for sections with "ランキング"
            for section in soup.find_all(['div', 'section', 'dl', 'ul']):
                text = section.get_text()
                if "ランキング" in text and len(text) < 1000:
                     links = section.find_all('a')
                     for a in links:
                         if 'corpinfo' in a.get('href', ''):
                             items.append({
                                 'title': f"[MyNavi Rank] {a.get_text(strip=True)}",
                                 'link': urllib.parse.urljoin(base_url, a['href']),
                                 'summary': "マイナビ アクセスランキング掲載企業",
                                 'source': "MyNavi Ranking",
                                 'image_url': ""
                             })
    except Exception as e:
        print(f"   [MyNavi Top Error] {e}")

    # 2. Event Page (Focus: Kansai/General)
    try:
        url_evt = "https://job.mynavi.jp/conts/2027/event/index.html"
        req = urllib.request.Request(url_evt, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            
            # Grab Event Links
            for a in soup.find_all('a'):
                txt = a.get_text(strip=True)
                href = a.get('href', '')
                if "event" in href and len(txt) > 5:
                    is_relevant = any(k in txt for k in ["関西", "大阪", "神戸", "兵庫", "東京", "EXPO", "就職博"])
                    if is_relevant or "合同" in txt or "EXPO" in txt or "インターン" in txt:
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
