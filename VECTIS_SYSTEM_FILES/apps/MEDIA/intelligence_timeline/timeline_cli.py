import os
import json
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.tree import Tree
from rich import box

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Try to find universe.json in standard location
UNIVERSE_PATH = os.path.abspath(os.path.join(BASE_DIR, "../youtube_channel/data/universe.json"))
# Fallback to absolute path if relative fails (e.g. running from different cwd)
if not os.path.exists(UNIVERSE_PATH):
    UNIVERSE_PATH = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\MEDIA\youtube_channel\data\universe.json"

console = Console()

# --- DATA ---
def load_universe():
    if not os.path.exists(UNIVERSE_PATH):
        console.print(f"[bold red]ERROR:[/bold red] Universe file not found at: {UNIVERSE_PATH}")
        return []
    
    try:
        with open(UNIVERSE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            nodes = data.get('nodes', [])
            # Normalize dates
            for n in nodes:
                try:
                    if 'timestamp' in n:
                        n['dt'] = datetime.fromisoformat(n['timestamp'].replace('Z', '+00:00'))
                    else:
                        n['dt'] = datetime.min
                except:
                    n['dt'] = datetime.min
            
            # Sort by date desc
            nodes.sort(key=lambda x: x['dt'], reverse=True)
            return nodes
    except Exception as e:
        console.print(f"[bold red]ERROR:[/bold red] Failed to load JSON: {e}")
        return []

NODES = load_universe()

# --- UI COMPONENTS ---
def print_header():
    console.clear()
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    
    title = Text("VECTIS INTELLIGENCE VIEWER", style="bold cyan")
    status = Text(f"NODES: {len(NODES)} | SYS: ONLINE", style="dim white")
    
    grid.add_row(title, status)
    console.print(Panel(grid, style="cyan", box=box.ROUNDED))

def view_timeline():
    print_header()
    console.print("[bold yellow]TIMELINE VIEW (Latest First)[/bold yellow]")
    
    table = Table(box=box.SIMPLE_HEAD, show_lines=True)
    table.add_column("ID", style="dim", width=8)
    table.add_column("Date", style="green", width=12)
    table.add_column("Category", style="magenta", width=15)
    table.add_column("Title", style="bold white")
    table.add_column("Imp", justify="right", width=4)

    # Simple pagination (show top 20)
    for n in NODES[:20]:
        date_str = n['dt'].strftime("%Y-%m-%d") if n['dt'] != datetime.min else "----"
        table.add_row(
            str(n.get('id', '?')),
            date_str,
            str(n.get('group', 'AVG')),
            str(n.get('title', 'No Title')),
            str(n.get('importance', '-'))
        )
    
    console.print(table)
    console.print("[dim]Showing recent 20 nodes...[/dim]")
    Prompt.ask("\nPress [bold]Enter[/bold] to return")

def view_clusters():
    print_header()
    console.print("[bold yellow]CLUSTER ANALYSIS[/bold yellow]")
    
    groups = {}
    for n in NODES:
        g = n.get('group', 'Uncategorized')
        if g not in groups: groups[g] = []
        groups[g].append(n)
    
    tree = Tree("Universe Clusters", style="cyan")
    
    for g_name, items in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        branch = tree.add(f"[bold magenta]{g_name}[/bold magenta] ({len(items)})")
        # Show top 3 recent in each cluster
        for n in items[:3]:
            branch.add(f"[dim]{n.get('id')}[/dim] {n.get('title')}")
        if len(items) > 3:
            branch.add(f"[dim]... +{len(items)-3} more[/dim]")
            
    console.print(tree)
    Prompt.ask("\nPress [bold]Enter[/bold] to return")

def search_nodes():
    print_header()
    query = Prompt.ask("[bold cyan]SEARCH QUERY[/bold cyan]").lower()
    if not query: return
    
    results = [
        n for n in NODES 
        if query in n.get('title', '').lower() or query in n.get('summary', '').lower()
    ]
    
    console.print(f"\n[bold]Found {len(results)} matches for '{query}'[/bold]")
    
    table = Table(box=box.SIMPLE)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    
    for n in results[:10]:
        table.add_row(n.get('id'), n.get('title'))
        
    console.print(table)
    if len(results) > 10:
        console.print(f"...and {len(results)-10} more.")
        
    nid = Prompt.ask("\nEnter [bold]Node ID[/bold] to inspect (or Enter to back)")
    if nid:
        inspect_node(nid)

def inspect_node(node_id=None):
    if not node_id:
        print_header()
        node_id = Prompt.ask("Enter [bold]Node ID[/bold]")
        
    target = next((n for n in NODES if str(n.get('id')) == str(node_id)), None)
    
    if not target:
        console.print(f"[red]Node '{node_id}' not found.[/red]")
        time.sleep(1)
        return

    print_header()
    
    # Header Info
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold cyan")
    grid.add_column(style="white")
    grid.add_row("ID:", str(target.get('id')))
    grid.add_row("DATE:", str(target.get('timestamp')))
    grid.add_row("GROUP:", f"[{target.get('group', 'AVG')}]")
    grid.add_row("IMPORTANCE:", str(target.get('importance', 5)) + "/10")
    
    console.print(Panel(grid, title=target.get('title'), style="white", border_style="cyan"))
    
    # Content
    summary = target.get('summary', '')
    full_text = target.get('full_text', '')
    
    if full_text:
        console.print(Panel(Markdown(full_text), title="FULL TEXT", border_style="green"))
    elif summary:
        console.print(Panel(Markdown(summary), title="SUMMARY", border_style="yellow"))
    else:
        console.print("[dim]No content content available.[/dim]")
        
    Prompt.ask("\nPress [bold]Enter[/bold] to return")

import sys
from rich.live import Live
from rich.spinner import Spinner

# --- DEEP RESEARCHER ---
try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

# Add modules path to sys.path to import UnifiedLLM
MODULES_PATH = os.path.abspath(os.path.join(BASE_DIR, "../youtube_channel"))
if MODULES_PATH not in sys.path:
    sys.path.append(MODULES_PATH)

try:
    from modules.unified_llm import UnifiedLLM
    # Use accurate model for research
    research_llm = UnifiedLLM(provider="ollama", model_name="gemma:2b") 
except ImportError:
    research_llm = None

class DeepResearcher:
    def __init__(self):
        self.ddgs = DDGS() if HAS_DDGS else None
        
    def perform_research(self, topic, k_depth=3):
        if not self.ddgs or not research_llm:
            return "[red]Error: duckduckgo-search or UnifiedLLM not available.[/red]"
            
        full_report = f"# Deep Research: {topic}\n\n"
        current_query = topic
        context = []
        
        console.print(f"\n[bold cyan]🚀 INITIATING DEEP RESEARCH (Depth: {k_depth})[/bold cyan]")
        console.print(f"Target: [yellow]{topic}[/yellow]\n")
        
        for i in range(k_depth):
            step_num = i + 1
            
            # 1. Search
            with Live(Spinner('dots', text=f"Step {step_num}/{k_depth}: Searching '{current_query}'..."), refresh_per_second=10):
                try:
                    results = list(self.ddgs.text(current_query, max_results=5))
                    search_summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                except Exception as e:
                    return f"[red]Search Error: {e}[/red]"

            # 2. Analyze & Reason
            with Live(Spinner('earth', text=f"Step {step_num}/{k_depth}: Analyzing & Calculating..."), refresh_per_second=10):
                prompt = f"""
                You are a "Deep Atomic Researcher". Your goal is to deconstruct any topic down to its fundamental "Atoms" (First Principles).
                
                TOPIC: {topic}
                CURRENT DEPTH: {step_num}/{k_depth}
                
                SEARCH RESULTS:
                {search_summary}
                
                PREVIOUS CONTEXT:
                {chr(10).join(context[-2:])}
                
                MANDATE:
                1. DO NOT stop at high-level explanations or analogies.
                2. DIG DEEPER. Look for:
                   - Mathematical Axioms / Formulas
                   - Source Code logic / Algorithms
                   - Physical / Chemical / Biological Foundations
                   - Historical Origin / Etymology
                3. If the search result is too superficial, criticize it and formulate a query to go deeper.
                
                OUTPUT FORMAT:
                ## Atomic Insight {step_num}
                (Explain the mechanism at the lowest possible level found so far. Use math/code blocks if applicable.)
                
                ## Next Query
                (A specific query to reach the next level of granularity. e.g. "mathematical proof of...", "source code implementation of...", "physical mechanism of...")
                """
                
                response = research_llm.invoke(prompt)
                
                # Parse
                parts = response.split("## Next Query")
                insight = parts[0].strip()
                next_query = parts[1].strip() if len(parts) > 1 else topic + " implementation details"
                
                # Clean up query
                next_query = next_query.replace('"', '').replace("'", "").split('\n')[0]
                
                full_report += f"{insight}\n\n---\n\n"
                context.append(insight)
                current_query = next_query
                
            console.print(f"[green]✔ Step {step_num} Complete.[/green] Next Target: [dim]{next_query}[/dim]")
            
        # Final Synthesis
        with Live(Spinner('line', text="Finalizing Report..."), refresh_per_second=10):
            final_prompt = f"""
            Synthesize a comprehensive report on "{topic}" based on the following research chain.
            Focus on First Principles, Mathematics (Complexity, Formulas), and Core Algorithms.
            
            RESEARCH CHAIN:
            {full_report}
            """
            final_output = research_llm.invoke(final_prompt)
            
        return final_output

researcher = DeepResearcher()

def run_deep_research():
    print_header()
    if not HAS_DDGS:
        console.print("[red]Deep Research requires 'duckduckgo-search'. Please install it.[/red]")
        Prompt.ask("Press Enter")
        return

    topic = Prompt.ask("[bold cyan]Enter Research Topic (Deep Atomic Scan)[/bold cyan]")
    if not topic: return
    
    k_val = IntPrompt.ask("[bold cyan]Enter Search Depth (k) [dim](Recommended: 4+)[/dim][/bold cyan]", default=4)
    
    result = researcher.perform_research(topic, k_depth=k_val)
    
    console.print(Panel(Markdown(result), title=f"ATOMIC RESEARCH: {topic}", border_style="green"))
    
    # Save option
    if Prompt.ask("Save this Knowledge Atom?", choices=["y", "n"], default="y") == "y":
        # Simplified save logic (Append to local list only for session)
        new_node = {
            'id': f"ATOM_{datetime.now().strftime('%H%M%S')}",
            'title': f"Atom: {topic}",
            'summary': result[:500] + "...",
            'full_text': result,
            'group': 'Atomic Research',
            'importance': 10,
            'dt': datetime.now(),
            'timestamp': datetime.now().isoformat()
        }
        NODES.insert(0, new_node)
        console.print("[green]Node Added to Session.[/green]")
        
    Prompt.ask("\nPress [bold]Enter[/bold] to return")

def run_chaos_mode():
    import random
    
    # Deep/Abstract topics for random selection
    CHAOS_SEEDS = [
        "Riemann Hypothesis", "P vs NP Problem", "Consciousness Hard Problem", 
        "Quantum Entanglement", "Navier-Stokes Equations", "Dark Energy",
        "Gödel's Incompleteness Theorems", "CRISPR-Cas9 Off-target effects",
        "Transformer Attention Entropy", "Information Geometry", "Free Will",
        "Bio-semiotics", "Panpsychism", "Strange Loops", "Category Theory",
        "Homotopy Type Theory", "Boltzmann Brains", "Fermi Paradox",
        "Technological Singularity", "Mirror Neurons", "Metamaterials",
        "Zero-Knowledge Proofs", "Neural Manifolds", "Langlands Program"
    ]
    
    while True:
        print_header()
        console.print("[bold magenta]🎲 CHAOS MODE INITIATED: SURRENDERING TO ENTROPY...[/bold magenta]\n")
        
        # 1. Select Topic
        if NODES and random.random() > 0.5:
             # 50% chance to dig deeper into existing knowledge
             source_node = random.choice(NODES)
             topic = f"Underlying axioms of {source_node.get('title')}"
        else:
             # 50% chance for new deep abstract topic
             topic = random.choice(CHAOS_SEEDS)
             
        # 2. Random Depth (3 to 6)
        depth = random.randint(3, 5)
        
        console.print(f"TARGET: [yellow]{topic}[/yellow]")
        console.print(f"DEPTH:  [cyan]{depth}[/cyan] layers")
        console.print("[dim]Auto-execution in 3 seconds... (Ctrl+C to stop)[/dim]")
        
        try:
            with Live(Spinner('noise'), refresh_per_second=10):
                import time
                time.sleep(3)
        except KeyboardInterrupt:
            return

        # 3. Execute
        result = researcher.perform_research(topic, k_depth=depth)
        
        console.print(Panel(Markdown(result), title=f"CHAOS RESULT: {topic}", border_style="magenta"))
        
        # Auto-save (Chaos feeds the universe)
        new_node = {
            'id': f"CHAOS_{datetime.now().strftime('%H%M%S')}",
            'title': f"Chaos: {topic}",
            'summary': result[:500] + "...",
            'full_text': result,
            'group': 'Chaos Research',
            'importance': 10,
            'dt': datetime.now(),
            'timestamp': datetime.now().isoformat()
        }
        NODES.insert(0, new_node)
        console.print("[magenta]Knowledge Atom Absorbed.[/magenta]")
        
        # Continue or Break?
        console.print("\n[dim]Press Enter for NEXT WAVE (or 'q' to quit)...[/dim]")
        if Prompt.ask("", default="") == 'q':
            break

        if Prompt.ask("", default="") == 'q':
            break

# --- CRAWL4AI INTEGRATION ---
try:
    from crawl4ai import AsyncWebCrawler
    HAS_CRAWL = True
except ImportError:
    HAS_CRAWL = False

def run_crawl_mode():
    if not HAS_CRAWL:
        console.print("[red]Crawl4AI not installed. Run 'pip install crawl4ai' and 'playwright install'.[/red]")
        Prompt.ask("Press Enter")
        return

    import asyncio
    
    url = Prompt.ask("[bold cyan]Enter URL to Crawl[/bold cyan]")
    if not url: return

    async def _crawl_task():
        console.print(f"[dim]Connecting to {url}...[/dim]")
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                res = await crawler.arun(url=url)
                return res.markdown
        except Exception as e:
            return f"Error: {e}"

    with Live(Spinner('bouncingBall', text="Crawling Target..."), refresh_per_second=10):
        try:
            markdown_content = asyncio.run(_crawl_task())
        except Exception as e:
            markdown_content = f"Execution Error: {e}"

    console.print(Panel(Markdown(markdown_content[:2000] + "\n\n...(truncated)"), title=f"CRAWL RESULT: {url}", border_style="green"))
    
    # Save option
    if Prompt.ask("Save extracted content?", choices=["y", "n"], default="y") == "y":
        title = Prompt.ask("Enter Title", default="Web Crawl Data")
        new_node = {
            'id': f"WEB_{datetime.now().strftime('%H%M%S')}",
            'title': title,
            'summary': markdown_content[:500],
            'full_text': markdown_content,
            'group': 'Web Data',
            'importance': 5,
            'dt': datetime.now(),
            'timestamp': datetime.now().isoformat()
        }
        NODES.insert(0, new_node)
        console.print("[green]Saved.[/green]")
    
    Prompt.ask("\nPress [bold]Enter[/bold] to return")

def main_menu():
    while True:
        print_header()
        console.print(Panel(
            "[1] 📅 TIMELINE View\n"
            "[2] 🌌 CLUSTER View\n"
            "[3] 🔍 SEARCH Nodes\n"
            "[4] 👁️ INSPECT Node ID\n"
            "[5] 🧠 DEEP ATOMIC RESEARCH\n"
            "[6] 🎲 CHAOS MODE (Random Loop)\n"
            "[7] 🕸️ WEB CRAWL READER (New!)\n"
            "[Q] 🚪 QUIT",
            title="MAIN MENU",
            border_style="cyan"
        ))
        
        choice = Prompt.ask("Select Option", choices=["1", "2", "3", "4", "5", "6", "7", "q", "Q"], default="7")
        
        if choice == "1": view_timeline()
        elif choice == "2": view_clusters()
        elif choice == "3": search_nodes()
        elif choice == "4": inspect_node()
        elif choice == "5": run_deep_research()
        elif choice == "6": run_chaos_mode()
        elif choice == "7": run_crawl_mode()
        elif choice.lower() == "q":
            console.print("System Shutdown...")
            break


if __name__ == "__main__":
    try:
        if "--chaos" in sys.argv:
            run_chaos_mode()
        else:
            main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]System Halted.[/bold red]")
