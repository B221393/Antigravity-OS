"""
VECTIS - MAGI Wiki Generator
============================
SEARCH機能用のWiki自動生成システム

Features:
- AI駆使での重複チェック
- 自動Wiki記事生成
- 検索履歴管理
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class WikiGenerator:
    """
    SEARCH用Wiki自動生成
    
    Invariants:
    - wiki_dbは常に有効なJSON
    - 重複エントリは作成しない
    """
    
    def __init__(self, wiki_db_path: Optional[str] = None):
        if wiki_db_path is None:
            base_dir = Path(__file__).parent.parent
            wiki_db_path = base_dir / "data" / "search_wiki.json"
        
        self.wiki_db_path = Path(wiki_db_path)
        self.wiki_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # LLM client (Unified)
        self.llm = None
        try:
            from modules.unified_llm import create_llm_client
            self.llm = create_llm_client()
        except ImportError:
            print("⚠️ Unified LLM not available. Wiki will be minimal.")
    
    def check_exists(self, query: str) -> bool:
        """
        既存Wikiエントリをチェック（AI判断）
        
        Reasoning:
        - 完全一致だけでなく、類似も検出
        - 「Apple」と「アップル」を同一視
        """
        wiki_data = self._load_wiki()
        query_lower = query.lower()
        
        # 完全一致チェック
        if query_lower in wiki_data:
            return True
        
        # AI類似度判定（オプション）
        if self.llm and len(wiki_data) > 0:
            try:
                existing_titles = list(wiki_data.keys())
                prompt = f"""
Check if "{query}" is semantically similar to any of these:
{', '.join(existing_titles[:10])}

Answer with ONLY "YES" or "NO".
If similar (e.g., "Apple" and "アップル"), say YES.
If different, say NO.
"""
                response = self.llm.generate(prompt, temperature=0.1, max_tokens=10)
                if "YES" in response.upper():
                    return True
            except:
                pass
        
        return False
    
    def create_wiki_entry(self, query: str) -> Dict[str, Any]:
        """
        Wiki記事を生成
        
        Returns:
        - 成功時: {"success": True, "entry": {...}}
        - 失敗時: {"success": False, "error": "..."}
        """
        # 既存チェック
        if self.check_exists(query):
            return {
                "success": False,
                "error": "Entry already exists",
                "entry": self._get_entry(query)
            }
        
        # AI生成
        if self.llm:
            try:
                wiki_content = self._generate_wiki_ai(query)
            except Exception as e:
                wiki_content = self._generate_wiki_fallback(query)
        else:
            wiki_content = self._generate_wiki_fallback(query)
        
        # 保存
        entry = {
            "title": query,
            "content": wiki_content,
            "created": datetime.now().isoformat(),
            "search_count": 1,
            "last_searched": datetime.now().isoformat()
        }
        
        self._save_entry(query.lower(), entry)
        
        return {
            "success": True,
            "entry": entry
        }
    
    def increment_search_count(self, query: str):
        """検索回数をカウント"""
        wiki_data = self._load_wiki()
        query_lower = query.lower()
        
        if query_lower in wiki_data:
            wiki_data[query_lower]["search_count"] += 1
            wiki_data[query_lower]["last_searched"] = datetime.now().isoformat()
            
            with open(self.wiki_db_path, 'w', encoding='utf-8') as f:
                json.dump(wiki_data, f, ensure_ascii=False, indent=2)
    
    def _generate_wiki_ai(self, query: str) -> str:
        """AI生成（Unified LLM）"""
        prompt = f"""
Create a concise Wikipedia-style article for: {query}

Format (Markdown):
# {query}

**概要**:
(2-3 sentences explaining what it is)

**重要ポイント**:
- Key point 1
- Key point 2
- Key point 3

**関連トピック**:
- Related 1
- Related 2

Keep it under 200 words. Be informative and accurate.
"""
        
        response = self.llm.generate(prompt, temperature=0.7, max_tokens=400)
        return response.strip()
    
    def _generate_wiki_fallback(self, query: str) -> str:
        """フォールバック生成（AIなし）"""
        return f"""# {query}

**概要**:
「{query}」について検索されました。

**メモ**:
- 検索日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- このエントリはプレースホルダーです

**アクション**:
詳細情報を追加してください。
"""
    
    def _load_wiki(self) -> Dict:
        """Wikiデータベース読み込み"""
        if self.wiki_db_path.exists():
            try:
                with open(self.wiki_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _get_entry(self, query: str) -> Optional[Dict]:
        """特定エントリ取得"""
        wiki_data = self._load_wiki()
        return wiki_data.get(query.lower())
    
    def _save_entry(self, key: str, entry: Dict):
        """エントリ保存"""
        wiki_data = self._load_wiki()
        wiki_data[key] = entry
        
        with open(self.wiki_db_path, 'w', encoding='utf-8') as f:
            json.dump(wiki_data, f, ensure_ascii=False, indent=2)


class InputHistory:
    """
    入力履歴管理（↑キー対応）
    
    Features:
    - 履歴保存
    - ↑/↓ナビゲーション
    - 永続化（オプション）
    """
    
    def __init__(self, max_size: int = 100, persistent: bool = False, history_file: str = None):
        self.max_size = max_size
        self.history = []
        self.current_index = -1
        self.persistent = persistent
        self.history_file = history_file
        
        if persistent and history_file:
            self._load_history()
    
    def add(self, text: str):
        """履歴に追加"""
        if text and (not self.history or self.history[-1] != text):
            self.history.append(text)
            if len(self.history) > self.max_size:
                self.history.pop(0)
            
            if self.persistent:
                self._save_history()
        
        self.current_index = -1  # Reset
    
    def get_previous(self, current_text: str = "") -> Optional[str]:
        """↑キー: 前の履歴"""
        if not self.history:
            return None
        
        if self.current_index == -1:
            self.current_index = len(self.history) - 1
        elif self.current_index > 0:
            self.current_index -= 1
        
        return self.history[self.current_index]
    
    def get_next(self) -> Optional[str]:
        """↓キー: 次の履歴"""
        if not self.history or self.current_index == -1:
            return ""
        
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        else:
            self.current_index = -1
            return ""
    
    def _load_history(self):
        """履歴ファイル読み込み"""
        if self.history_file and os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def _save_history(self):
        """履歴ファイル保存"""
        if self.history_file:
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ Failed to save history: {e}")


# === Convenience Functions ===

def create_wiki_for_search(query: str) -> Dict[str, Any]:
    """
    Factory function for quick Wiki creation
    
    Usage:
        result = create_wiki_for_search("Python")
        if result["success"]:
            print(result["entry"]["content"])
    """
    wiki_gen = WikiGenerator()
    return wiki_gen.create_wiki_entry(query)


if __name__ == "__main__":
    # Test
    print("=== MAGI Wiki Generator Test ===")
    
    result = create_wiki_for_search("Artificial Intelligence")
    print(f"\nSuccess: {result['success']}")
    if result['success']:
        print(f"\n{result['entry']['content']}")
