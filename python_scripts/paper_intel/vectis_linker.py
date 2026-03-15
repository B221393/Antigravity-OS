from pathlib import Path
from datetime import datetime

class VectisLinker:
    """解析結果をVECTIS OSのナレッジベースに統合するクラス"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.research_dir = self.base_dir / "VECTIS_SYSTEM_FILES" / "KNOWLEDGE" / "RESEARCH"
        self.intel_log_path = self.base_dir / "VECTIS_SYSTEM_FILES" / "CAREER" / "STRATEGIC_INTEL_LOG.md"

    def link(self, summary: str, paper_info: dict) -> str:
        """要約を保存し、ログにリンクを追加する"""
        
        # 1. 詳細MDファイルの作成
        today = datetime.now().strftime("%Y%m%d")
        safe_title = "".join([c for c in paper_info['title'][:50] if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_')
        file_name = f"{today}_{paper_info['id'].replace('/', '_')}_{safe_title}.md"
        node_path = self.research_dir / file_name
        
        # ヘッダー情報の付与
        full_node_content = f"""---
Title: {paper_info['title']}
ID: {paper_info['id']}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Link: {paper_info['abs_url']}
---

{summary}
"""
        with open(node_path, "w", encoding="utf-8") as f:
            f.write(full_node_content)
        
        # 2. STRATEGIC_INTEL_LOG.md への追記
        log_entry = f"""
## [{datetime.now().strftime("%Y-%m-%d")}] Paper Intel: {paper_info['title']}
- **ID**: arXiv:{paper_info['id']}
- **Summary**: {summary.split('## 1. Background')[1].split('## 2. Methods')[0].strip()[:200]}...
- **Node**: [Link to Detail](../../KNOWLEDGE/RESEARCH/{file_name})
"""
        with open(self.intel_log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        return str(node_path)

if __name__ == "__main__":
    # 単体テスト
    linker = VectisLinker()
    print("Linker initialized.")
