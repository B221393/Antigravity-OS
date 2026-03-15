
import json
import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, DataTable, Label, Static, Input
from textual.binding import Binding

# Configuration
EGO_ROOT = Path(r"C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES")
UNIVERSE_FILE = EGO_ROOT / "data" / "universe.json"

class IntelligenceTUI(App):
    """EGO INTELLIGENCE HUB - TUI Edition"""

    CSS = """
    Screen {
        background: #0d0d0d;
    }
    
    #header_stats {
        height: 3;
        background: #1e1e1e;
        color: #00cc66;
        content-align: center middle;
        text-style: bold;
        border-bottom: heavy #4d4d4d;
    }

    DataTable {
        height: 1fr;
        background: #0d0d0d;
        color: #cccccc;
        border: none;
    }
    
    DataTable > .datatable--header {
        background: #252526;
        color: #007acc;
        text-style: bold;
    }
    
    DataTable > .datatable--cursor {
        background: #007acc;
        color: white;
    }

    Input {
        dock: bottom;
        margin: 1;
        background: #1e1e1e;
        color: white;
        border: heavy #4d4d4d;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_data", "Refresh"),
        Binding("/", "focus_search", "Search"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("🧠 EGO INTELLIGENCE NODE GRAPH", id="header_stats")
        yield DataTable(cursor_type="row")
        yield Input(placeholder="Search nodes... (Press / to focus)", id="search_box")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Label", "Type", "Info")
        self.load_data()

    def load_data(self, filter_text: str = ""):
        table = self.query_one(DataTable)
        table.clear()
        
        try:
            if UNIVERSE_FILE.exists():
                with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    nodes = data.get("nodes", [])
                    links = data.get("links", [])
                    
                    # Data Volume Visualization
                    vol_bar = "█" * (len(nodes) // 5)
                    storage_info = f"💾 STORAGE: {UNIVERSE_FILE}"
                    stats = f"NODES: {len(nodes)} | LINKS: {len(links)} | VOL: {vol_bar}"
                    
                    self.query_one("#header_stats").update(f"{storage_info}\n{stats}")

                    count = 0
                    for node in nodes:
                        n_id = str(node.get("id", ""))
                        n_label = str(node.get("label", ""))
                        n_type = str(node.get("type", "Unknown"))
                        n_info = str(node.get("info", ""))[:50] + "..."

                        if filter_text.lower() in n_label.lower() or filter_text.lower() in n_info.lower():
                            table.add_row(n_id, n_label, n_type, n_info)
                            count += 1
                            if count > 500: # Limit for performance
                                break
            else:
                self.query_one("#header_stats").update(f"💾 STORAGE: {UNIVERSE_FILE}\n⚠️ ERROR: File not found")
        except Exception as e:
            self.query_one("#header_stats").update(f"ERROR: {e}")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.load_data(event.value)

    def action_focus_search(self):
        self.query_one(Input).focus()

    def action_refresh_data(self):
        self.load_data(self.query_one(Input).value)

if __name__ == "__main__":
    app = IntelligenceTUI()
    app.run()
