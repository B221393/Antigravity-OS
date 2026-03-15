
import urllib.request
from bs4 import BeautifulSoup
import sys

# Windows stdout encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def fetch_and_parse(url):
    print(f"\n=== Fetching {url} ===")
    req = urllib.request.Request(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
    try:
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            return soup
    except Exception as e:
        print(f"Error: {e}")
        return None

# 1. Inspect Top Page Topics
soup = fetch_and_parse("https://job.mynavi.jp/2027/")
if soup:
    topics_h = soup.find(lambda tag: tag.name in ['h2', 'h3'] and "トピックス" in tag.get_text())
    if topics_h:
        print("Found Topics Heading. Inspecting siblings/children...")
        # Usually followed by a div or ul
        sibling = topics_h.find_next_sibling()
        if sibling:
            print(f"Next Sibling: {sibling.name} class={sibling.get('class')}")
            for a in sibling.find_all('a'):
                print(f"  Topic: {a.get_text(strip=True)} -> {a['href']}")
    else:
        print("Topics heading not found.")

# 2. Inspect Event Page
soup = fetch_and_parse("https://job.mynavi.jp/conts/2027/event/index.html")
if soup:
    print("=== Event Page Headlines ===")
    # Look for list of events. Usually 'h3' or 'a' with specific class.
    # Just print all links with 'event' in text or 'sched' in url?
    # Let's look for headings likely to be event titles
    for h in soup.find_all(['h3', 'h4'], limit=10):
        print(f"H: {h.get_text(strip=True)}")
    
    # Look for links
    print("--- Links ---")
    for a in soup.find_all('a', limit=30):
        txt = a.get_text(strip=True)
        if len(txt) > 5 and "イベント" in txt:
            print(f"Event Link: {txt} -> {a['href']}")
