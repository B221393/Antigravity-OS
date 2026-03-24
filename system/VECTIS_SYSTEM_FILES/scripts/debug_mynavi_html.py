
import urllib.request
from bs4 import BeautifulSoup
import sys

# Windows stdout encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

url = "https://job.mynavi.jp/2027/"
req = urllib.request.Request(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})

try:
    with urllib.request.urlopen(req) as res:
        soup = BeautifulSoup(res.read(), 'html.parser')
        
    print("=== Extracting Likely Lists ===")
    
    # Try generic classes common in MyNavi (guesswork -> verification)
    # Usually they use semantic tags or divs with 'box' 'ranking' etc.
    
    # 1. Look for headings
    headings = soup.find_all(['h2', 'h3'])
    for h in headings[:10]:
        print(f"Heading: {h.get_text(strip=True)}")
        # Check next sibling
        # sibling = h.find_next_sibling()
        # if sibling: print(f"  Sibling tag: {sibling.name}")

    # 2. Look for links with 'corpinfo' (Company pages)
    corp_links = soup.find_all('a', href=True)
    count = 0
    print("\n=== Corp Links Sample ===")
    for a in corp_links:
        if 'corpinfo' in a['href'] and count < 5:
            print(f"Link: {a.get_text(strip=True)} -> {a['href']}")
            count += 1
            
    # 3. Look for "Event" links
    print("\n=== Event Links Sample ===")
    count = 0
    for a in corp_links:
        if 'event' in a['href'] and count < 5:
            print(f"Event: {a.get_text(strip=True)} -> {a['href']}")
            count += 1

except Exception as e:
    print(f"Error: {e}")
