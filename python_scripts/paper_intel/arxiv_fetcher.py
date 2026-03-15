import requests
import xml.etree.ElementTree as ET
import time
from typing import List, Dict, Optional

ARXIV_API_URL = "http://export.arxiv.org/api/query"

class ArxivFetcher:
    """arXiv API から論文メタデータを取得するクラス"""

    def __init__(self, wait_time: int = 3):
        self.wait_time = wait_time
        self.last_request_time = 0.0

    def _wait_for_rate_limit(self):
        """arXiv APIの利用規約に従い、リクエスト間にディレイを設ける"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.wait_time:
            time.sleep(self.wait_time - elapsed)
        self.last_request_time = time.time()

    def _parse_entry(self, entry: ET.Element) -> Dict:
        """Atomフィードの1エントリをパースして辞書に変換する"""
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # arXiv ID の抽出 (例: http://arxiv.org/abs/2405.00001v1 -> 2405.00001v1)
        id_url = entry.find('atom:id', ns).text
        arxiv_id = id_url.split('/')[-1]

        # PDFリンクの抽出
        pdf_url = ""
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('title') == 'pdf':
                pdf_url = link.attrib.get('href', '')
            elif link.attrib.get('type') == 'application/pdf':
                pdf_url = link.attrib.get('href', '')

        return {
            "id": arxiv_id,
            "title": entry.find('atom:title', ns).text.strip().replace('\n', ' '),
            "summary": entry.find('atom:summary', ns).text.strip(),
            "authors": [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
            "published": entry.find('atom:published', ns).text,
            "pdf_url": pdf_url,
            "abs_url": id_url
        }

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        """キーワード検索を行い、メタデータのリストを返す"""
        self._wait_for_rate_limit()
        
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        response = requests.get(ARXIV_API_URL, params=params)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        return [self._parse_entry(e) for e in entries]

    def fetch_by_id(self, arxiv_id: str) -> Optional[Dict]:
        """特定のarXiv IDを指定してメタデータを取得する"""
        self._wait_for_rate_limit()
        
        params = {
            "id_list": arxiv_id
        }
        
        response = requests.get(ARXIV_API_URL, params=params)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entry = root.find('atom:entry', ns)
        
        if entry is not None:
            return self._parse_entry(entry)
        return None

if __name__ == "__main__":
    # 単体テスト
    fetcher = ArxivFetcher()
    print("Testing search...")
    results = fetcher.search("LLM Agents", limit=1)
    for res in results:
        print(f"Title: {res['title']}")
        print(f"ID: {res['id']}")
        print(f"URL: {res['pdf_url']}")
