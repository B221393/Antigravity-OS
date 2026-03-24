import requests
import urllib.parse
from bs4 import BeautifulSoup

# Config
KIWIX_HOST = "http://localhost:9000"

class KiwixBridge:
    def __init__(self, host=KIWIX_HOST):
        self.host = host
        self.is_active = self._check_connection()

    def _check_connection(self):
        try:
            requests.get(self.host, timeout=1)
            return True
        except:
            return False

    def search(self, query):
        """
        Search Kiwix for a term and return the top result URL and snippet.
        """
        if not self.is_active:
            return None

        # Kiwix Search URL pattern: /search?content=zim_name&pattern=query
        # Note: Since the ZIM name varies, we search across the root if possible or assuming single ZIM.
        # With kiwix-serve, standard search is often at /search?pattern=...
        
        try:
            search_url = f"{self.host}/search?pattern={urllib.parse.quote(query)}"
            res = requests.get(search_url, timeout=2)
            if res.status_code != 200:
                return None
            
            # Parse HTML result (Kiwix serve returns HTML list)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Look for first result link
            # Structure usually: <ul><li><a href="/content/...">Title</a></li></ul>
            first_link = soup.find('a', href=True)
            
            if first_link and "/content/" in first_link['href']:
                full_url = self.host + first_link['href']
                title = first_link.text.strip()
                return {"title": title, "url": full_url}
            
            return None

        except Exception as e:
            print(f"[KiwixBridge] Search error: {e}")
            return None

    def get_summary(self, page_url):
        """
        Fetch the abstract/summary from a Kiwix page.
        """
        if not self.is_active:
            return None
            
        try:
            res = requests.get(page_url, timeout=2)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Simple extraction: First paragraph
            # Wikipedia ZIMs usually have specific classes, but p is generic safe bet
            paras = soup.find_all('p')
            for p in paras:
                text = p.get_text().strip()
                if len(text) > 50: # valid paragraph
                    return text[:300] + "..." # Truncate
            
            return None
        except:
            return None

# Test
if __name__ == "__main__":
    kb = KiwixBridge()
    if kb.is_active:
        print("Kiwix is running.")
        res = kb.search("哲学")
        if res:
            print(f"Found: {res['title']}")
            print(kb.get_summary(res['url']))
    else:
        print("Kiwix is NOT running.")
