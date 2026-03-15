import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

# Richを活用したUI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown

# 自作モジュールのインポート
from arxiv_fetcher import ArxivFetcher
from pdf_parser import PDFParser
from llm_analyzer import LLMAnalyzer
from vectis_linker import VectisLinker

# パスの設定
BASE_DIR = Path(__file__).parent.parent.parent
MEDIA_DIR = BASE_DIR / "_media" / "papers"
PDF_DIR = MEDIA_DIR / "pdf"
JSON_DIR = MEDIA_DIR / "json"

console = Console()

class AgenticUI:
    """動画 'Embracing: Designing Agentic UI' の思想を反映したターミナルUI"""

    @staticmethod
    def show_header():
        title = Text("VECTIS: Agentic Intelligence Pipeline", style="bold magenta")
        subtitle = Text("Embracing Knowledge via Gemini 2.5 Flash", style="italic cyan")
        console.print(Panel(title + "\n" + subtitle, expand=False, border_style="bright_blue"))

    @staticmethod
    def show_search_results(papers: List[Dict]):
        table = Table(title="🔍 Potential Knowledge Nodes (arXiv)", title_style="bold yellow", border_style="dim")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Published", style="green")
        
        for p in papers:
            table.add_row(p['id'], p['title'], p['published'][:10])
        
        console.print(table)

    @staticmethod
    def thought_stream(message: str, style: str = "italic dim white"):
        """エージェントの『内省（つぶやき）』を表示"""
        console.print(f"  [bold magenta]>[/bold magenta] [{style}]{message}[/{style}]")

    @staticmethod
    def show_insight(summary: str, title: str):
        """重要な知見をハイライト表示"""
        console.print(f"\n[bold green]💡 Core Insight Captured:[/bold green] [white]{title}[/white]")
        # 最初のセクション（Background）の一部を抜粋して表示
        try:
            insight = summary.split("## 1. Background")[1].split("## 2. Methods")[0].strip()
            console.print(Panel(Markdown(insight[:500] + "..."), title="Abstractive Integration", border_style="green"))
        except:
            pass

class PaperPipeline:
    def __init__(self):
        self.ui = AgenticUI()
        self.fetcher = ArxivFetcher()
        self.parser = PDFParser()
        self.analyzer = LLMAnalyzer(model_name="gemini-2.5-flash")
        self.linker = VectisLinker()

    def _get_cache_path(self, arxiv_id: str) -> Path:
        return JSON_DIR / f"{arxiv_id.replace('/', '_')}.json"

    def process_paper(self, arxiv_id: str, metadata: Optional[Dict] = None):
        """論文の取得、解析、統合のメインフロー（Agentic UI搭載）"""
        
        self.ui.thought_stream(f"Initiating neural link for ID: {arxiv_id}")
        
        cache_path = self._get_cache_path(arxiv_id)
        
        # 1. メタデータの取得
        with Status(f"[cyan]Accessing arXiv Node: {arxiv_id}...", spinner="earth") as status:
            if metadata:
                paper_info = metadata
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(paper_info, f, indent=4, ensure_ascii=False)
            elif cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    paper_info = json.load(f)
                self.ui.thought_stream("Local knowledge cache hit.")
            else:
                paper_info = self.fetcher.fetch_by_id(arxiv_id)
                if not paper_info:
                    console.print(f"[bold red]Error:[/bold red] Paper {arxiv_id} not found.")
                    return
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(paper_info, f, indent=4, ensure_ascii=False)
                self.ui.thought_stream("New node mapped from global network.")

        # 2. PDFのダウンロードとテキスト抽出
        from paper_pipeline import download_pdf  # 既存の関数を再利用
        
        with Status("[blue]Downloading PDF and constructing text stream...", spinner="dots") as status:
            pdf_path = download_pdf(paper_info['pdf_url'], paper_info['id'])
            if not pdf_path:
                return
            self.ui.thought_stream(f"Binary data acquired. Size: {pdf_path.stat().st_size / 1024:.1f} KB")
            
            text = self.parser.extract_text(pdf_path)
            if not text:
                return
            self.ui.thought_stream(f"Textual semantics extracted. Character count: {len(text)}")

        # 3. LLMによる要約生成 (思考の可視化)
        with Status("[magenta]Synthesizing intelligence via Gemini 2.5 Flash...", spinner="arc") as status:
            self.ui.thought_stream("Analyzing novelty and lateral links to VECTIS OS...")
            summary = self.analyzer.analyze(text, paper_info['title'])
            self.ui.thought_stream("Deep synthesis complete.")

        # 4. VECTIS OS への統合
        with Status("[green]Integrating into Strategic Intel Log...", spinner="bouncingBar") as status:
            node_path = self.linker.link(summary, paper_info)
            self.ui.thought_stream(f"Knowledge node anchored: {Path(node_path).name}")

        # 結果の要約表示
        self.ui.show_insight(summary, paper_info['title'])
        console.print(f"\n[bold green]✔ Neural integration successful.[/bold green]")
        console.print(f"[dim]Detail: {node_path}[/dim]")

def download_pdf(url: str, arxiv_id: str) -> Optional[Path]:
    """PDFをダウンロードして保存する（補助関数）"""
    import requests
    file_name = f"{arxiv_id.replace('/', '_')}.pdf"
    file_path = PDF_DIR / file_name
    if file_path.exists():
        return file_path
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return file_path
    except Exception as e:
        console.print(f"[red]Download failed:[/red] {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="VECTIS OS Paper Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_search = subparsers.add_parser("search", help="Search arXiv")
    parser_search.add_argument("query", type=str)
    parser_search.add_argument("--limit", type=int, default=1)

    parser_fetch = subparsers.add_parser("fetch", help="Fetch by ID")
    parser_fetch.add_argument("arxiv_id", type=str)

    args = parser.parse_args()
    pipeline = PaperPipeline()

    pipeline.ui.show_header()

    if args.command == "search":
        console.print(f"📡 Querying global network for: '[bold cyan]{args.query}[/bold cyan]' (Limit: {args.limit})")
        results = pipeline.fetcher.search(args.query, limit=args.limit)
        if not results:
            console.print("[yellow]No signals found.[/yellow]")
            return
        pipeline.ui.show_search_results(results)
        for paper in results:
            pipeline.process_paper(paper['id'], metadata=paper)
    elif args.command == "fetch":
        pipeline.process_paper(args.arxiv_id)

if __name__ == "__main__":
    main()
