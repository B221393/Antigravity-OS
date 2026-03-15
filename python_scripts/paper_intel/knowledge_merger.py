import os
import sqlite3
import numpy as np
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status

# .envの読み込み
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / "_config" / ".env")

# パスの設定
DB_PATH = BASE_DIR / "_media" / "papers" / "vectis_knowledge.db"
INTEL_LOG_PATH = BASE_DIR / "VECTIS_SYSTEM_FILES" / "CAREER" / "STRATEGIC_INTEL_LOG.md"

console = Console()

class KnowledgeMerger:
    """複数の知識ノードをマージ（統合）し、知性を成長させるエンジン"""

    def __init__(self, model_name: str = "gemini-2.5-flash", embed_model: str = "models/gemini-embedding-2-preview"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.embed_model = embed_model

    def _cosine_similarity(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def search_relevant_nodes(self, query: str, top_k: int = 3):
        """クエリに関連する知識をDBから複数抽出する"""
        # クエリのベクトル化
        result = genai.embed_content(
            model=self.embed_model,
            content=query,
            task_type="retrieval_query"
        )
        query_vec = np.array(result['embedding'], dtype=np.float32)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, content, embedding, source_path FROM knowledge")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for title, content, embedding_blob, source_path in rows:
            vec = np.frombuffer(embedding_blob, dtype=np.float32)
            score = self._cosine_similarity(query_vec, vec)
            results.append({
                "title": title,
                "content": content,
                "score": score,
                "path": source_path
            })

        # スコア順にソートして上位を返す
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def merge_to_strategy(self, query: str, nodes: list):
        """複数の知識ノードを一つの戦略的知性にマージする"""
        
        context = ""
        for i, node in enumerate(nodes):
            context += f"\n--- Node {i+1} (Source: {node['title']}) ---\n{node['content'][:4000]}\n"

        prompt = f"""
あなたは先進的なAIパートナー「Antigravity」です。
提供された複数の知識ノード（論文の要約やあなたの過去の思考ログ）を「マージ（結合・体系化）」し、
問いに対する一つの「高次元な戦略的回答」を日本語で生成してください。

【問い】: {query}

【提供された知識ノード】:
{context}

【出力フォーマット】:
# Strategic Merged Insight: {query}
Date: {datetime.now().strftime("%Y-%m-%d")}

## 1. Synthesis (統合された知見)
> 複数の知識から導き出される、共通項や新しい発見は何ですか？

## 2. Dynamic Linkage (知識の連鎖)
> 既存の「VECTIS OS」の思想（規律、現場、工夫）と、今回の論文の知見がどう結びつきましたか？

## 3. Evolutionary Action (進化のための行動)
> このマージされた知性を、明日からの行動やシステムの実装にどう活かしますか？

---
"""
        response = self.model.generate_content(prompt)
        return response.text

    def update_intel_log(self, merged_insight: str):
        """マージされた知見を戦略ログに追記する"""
        with open(INTEL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- MERGED INTELLIGENCE ---\n{merged_insight}\n")

def main(query: str):
    merger = KnowledgeMerger()
    
    with Status(f"[bold cyan]Merging knowledge for: '{query}'...", spinner="point") as status:
        # 1. 関連ノードの検索
        nodes = merger.search_relevant_nodes(query)
        if not nodes:
            console.print("[yellow]No relevant knowledge nodes found to merge.[/yellow]")
            return

        console.print(f"  [magenta]>[/magenta] Found {len(nodes)} relevant nodes in Vector Space.")
        for n in nodes:
            console.print(f"    - [dim]{n['title']} (Score: {n['score']:.4f})[/dim]")

        # 2. 合成（マージ）
        merged_insight = merger.merge_to_strategy(query, nodes)
        
        # 3. ログへの反映
        merger.update_intel_log(merged_insight)
        
    console.print(Panel(Markdown(merged_insight), title="🧠 Strategic Merged Result", border_style="bold magenta"))
    console.print(f"\n[bold green]✔ Knowledge successfully merged and archived in STRATEGIC_INTEL_LOG.md[/bold green]")

if __name__ == "__main__":
    import sys
    search_query = sys.argv[1] if len(sys.argv) > 1 else "エージェントとRAGの統合による知能の拡張"
    main(search_query)
