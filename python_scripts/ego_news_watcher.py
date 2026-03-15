"""
EGO News Watcher (Company Intelligence Agent)
==============================================
ターゲット企業の最新ニュースをGoogle Newsから自動収集し、EGO OSのログに記録する。
面接前の「最近の気になるニュース」対策を自動化。
"""

import os
import sys
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# ──────────────── 設定 ────────────────

# 監視対象キーワード
KEYWORDS = [
    "株式会社BREXA",
    "株式会社メイテック",
    "株式会社SHIFT",
    "サイボウズ株式会社",
    "製造業 DX",
    "ロボット SIer"
]

# 保存先ファイル
LOG_DIR = Path(r"C:\Users\Yuto\desktop\app\VECTIS_SYSTEM_FILES\documents\Personal_Logs")
NEWS_LOG_FILE = LOG_DIR / "NEWS_LOG.md"

# ──────────────── クラス ────────────────

class EgoNewsWatcher:
    def __init__(self):
        if not LOG_DIR.exists():
            LOG_DIR.mkdir(parents=True, exist_ok=True)

    def fetch_news(self, query):
        """Google News RSS からニュースを取得"""
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
        
        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            articles = []
            for item in root.findall(".//item")[:3]: # 各キーワード最新3件
                title = item.find("title").text
                link = item.find("link").text
                pub_date = item.find("pubDate").text
                articles.append({"title": title, "link": link, "date": pub_date})
            return articles
        except Exception as e:
            print(f"   [!] '{query}' の取得に失敗: {e}")
            return []

    def run(self):
        print(f"🚀 EGO News Watcher: 起動 (ターゲット: {len(KEYWORDS)}件)")
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        new_entries = [f"
# 📰 Daily News Intelligence ({timestamp})
"]
        
        for kw in KEYWORDS:
            print(f"   🔍 '{kw}' をリサーチ中...")
            articles = self.fetch_news(kw)
            if articles:
                new_entries.append(f"## {kw}")
                for art in articles:
                    new_entries.append(f"*   **[{art['title']}]({art['link']})**")
                    new_entries.append(f"    *   公開日: {art['date']}")
            else:
                new_entries.append(f"## {kw}
*   （本日、新しいニュースは見つかりませんでした）")

        # ファイルに書き込み
        content = "
".join(new_entries)
        try:
            if not NEWS_LOG_FILE.exists():
                with open(NEWS_LOG_FILE, "w", encoding="utf-8") as f:
                    f.write("# EGO NEWS INTELLIGENCE LOG
")
            
            with open(NEWS_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(content)
            
            print(f"
✅ リサーチ完了: {NEWS_LOG_FILE} に記録しました。")
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")

if __name__ == "__main__":
    watcher = EgoNewsWatcher()
    watcher.run()
