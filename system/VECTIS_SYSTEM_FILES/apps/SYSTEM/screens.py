
import json
import random
import asyncio
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Label, Input, Button, Static, Log
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive
from textual import work

# Configuration
VECTIS_ROOT = Path(r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES")
UNIVERSE_FILE = VECTIS_ROOT / "data" / "universe.json"

class HubScreen(Screen):
    """Integrated Intelligence Hub Screen"""
    
    BINDINGS = [("escape", "app.pop_screen", "Back to Nexus"), ("/", "focus_search", "Search")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("🧠 VECTIS INTELLIGENCE NODE GRAPH", id="hub_header", classes="header_box")
        yield DataTable(id="hub_table", cursor_type="row")
        yield Input(placeholder="Search nodes... (Press / to focus)", id="hub_search")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#hub_table")
        table.add_columns("ID", "Label", "Type", "Info")
        self.load_data()

    def load_data(self, filter_text: str = ""):
        table = self.query_one("#hub_table")
        table.clear()
        try:
            if UNIVERSE_FILE.exists():
                with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    nodes = data.get("nodes", [])
                    links = data.get("links", [])
                    
                # Stats update
                vol_bar = "█" * (len(nodes) // 5)
                self.query_one("#hub_header").update(
                    f"NODES: {len(nodes)} | LINKS: {len(links)} | VOL: {vol_bar}\n"
                    f"SOURCE: {UNIVERSE_FILE}"
                )

                count = 0
                for node in nodes:
                    n_label = str(node.get("label", ""))
                    n_info = str(node.get("info", ""))
                    if filter_text.lower() in n_label.lower() or filter_text.lower() in n_info.lower():
                        table.add_row(
                            str(node.get("id", "")),
                            n_label,
                            str(node.get("type", "Unknown")),
                            n_info[:50] + "...",
                        )
                        count += 1
                        if count > 500: break
            else:
                self.query_one("#hub_header").update("⚠️ DATABASE NOT FOUND (Run Discovery first)")
        except Exception as e:
            self.query_one("#hub_header").update(f"ERROR: {e}")

    def on_input_changed(self, event: Input.Changed):
        self.load_data(event.value)

    def action_focus_search(self):
        self.query_one("#hub_search").focus()


class GameScreen(Screen):
    """Integrated DT Cannon Screen"""
    
    BINDINGS = [("escape", "app.pop_screen", "Back to Nexus"), ("space", "fire_cannon", "FIRE")]
    
    ammo = reactive(10)
    score = reactive(0)
    current_target = reactive("Idle")

    CSS = """
    GameScreen {
        align: center middle;
        background: #111;
    }
    #game_container {
        width: 60;
        height: auto;
        border: heavy #00ff41;
        background: #001a05;
        padding: 2;
        text_align: center;
    }
    #target_display {
        height: 3;
        content-align: center middle;
        background: #222;
        color: red;
        text-style: bold;
        margin-bottom: 2;
    }
    #stats_display {
        color: #00ff41;
        margin-bottom: 2;
    }
    #log_display {
        height: 5;
        background: #000;
        color: #ddd;
        border: solid #00ff41;
    }
    .fire_btn {
        width: 100%;
        margin-top: 2;
        background: #880000;
        color: white;
    }
    """

    TARGETS = ["SNS Notification", "Self Doubt", "Buggy Code", "Useless Meeting", "Distraction"]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="game_container"):
            yield Label("🎯 DT CANNON: INTEGRATED", classes="header_box")
            yield Static("WAITING FOR TARGET...", id="target_display")
            yield Label(f"AMMO: {self.ammo} | SCORE: {self.score}", id="stats_display")
            yield Log(id="log_display")
            yield Button("FIRE CANNON [SPACE]", id="fire_btn", variant="error")
            yield Button("RELOAD [R]", id="reload_btn", variant="primary")
        yield Footer()

    def on_mount(self):
        self.spawn_target()

    def spawn_target(self):
        self.current_target = random.choice(self.TARGETS)
        self.query_one("#target_display").update(f"👾 HOSTILE: {self.current_target}")

    def watch_ammo(self, val):
        self.query_one("#stats_display").update(f"AMMO: {val} | SCORE: {self.score}")

    def watch_score(self, val):
        self.query_one("#stats_display").update(f"AMMO: {self.ammo} | SCORE: {val}")

    def action_fire_cannon(self):
        if self.ammo > 0:
            self.ammo -= 1
            log = self.query_one("#log_display")
            
            if random.random() > 0.2:
                self.score += 100
                log.write(f"💥 DESTROYED: {self.current_target}")
                self.spawn_target()
            else:
                log.write(f"💨 MISSED! {self.current_target} laughs.")
        else:
            self.query_one("#log_display").write("⚠️ CLICK RELOAD!")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "fire_btn":
            self.action_fire_cannon()
        elif event.button.id == "reload_btn":
            self.ammo = 10
            self.query_one("#log_display").write("🔄 RELOADED.")

class SpireScreen(Screen):
    """Integrated Knowledge Spire (Tower Defense)"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]
    
    health = reactive(100)
    current_q = reactive({})
    
    QUESTIONS = [
        {"q": "Linux list files cmd?", "a": "ls"},
        {"q": "Protocol for Web?", "a": "http"},
        {"q": "Python func keyword?", "a": "def"},
        {"q": "VECTIS OS core lang?", "a": "python"},
        {"q": "AI model name?", "a": "gemini"},
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="spire_container"):
            yield Label("🏰 KNOWLEDGE SPIRE", classes="header_box")
            yield Label(f"❤️ TOWER HEALTH: {self.health}", id="health_bar")
            yield Static("Ask...", id="q_display")
            yield Input(placeholder="Type Answer...", id="ans_input")
            yield Log(id="spire_log")
        yield Footer()

    def on_mount(self):
        self.next_question()

    def next_question(self):
        if self.health <= 0:
            self.query_one("#q_display").update("🔥 SPIRE FALLEN. GAME OVER.")
            return
        self.current_q = random.choice(self.QUESTIONS)
        self.query_one("#q_display").update(f"⚔️ ENEMY: {self.current_q['q']}")
        self.query_one("#ans_input").value = ""
        self.query_one("#ans_input").focus()

    def on_input_submitted(self, event: Input.Submitted):
        ans = event.value.lower().strip()
        correct = self.current_q["a"]
        log = self.query_one("#spire_log")
        
        if ans == correct:
            log.write(f"✨ BLOCKED! ({ans})")
            self.next_question()
        else:
            self.health -= 25
            log.write(f"💥 HIT! Correct: {correct}")
            self.query_one("#health_bar").update(f"❤️ TOWER HEALTH: {self.health}")
            self.next_question()

class TypingScreen(Screen):
    """Integrated Typing Speed Test"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]
    
    target_text = reactive("")
    start_time = 0.0
    
    SENTENCES = [
        "The quick brown fox jumps over the lazy dog.",
        "Python is the language of the future.",
        "VECTIS OS provides a unified terminal interface.",
        "Artificial Intelligence automates the mundane.",
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="typing_container"):
            yield Label("⌨️ NEURAL SYNC TEST", classes="header_box")
            yield Static("Press Enter to Start...", id="target_display")
            yield Input(placeholder="Type here...", id="type_input")
            yield Label("", id="result_display")
        yield Footer()

    def on_mount(self):
        self.next_round()

    def next_round(self):
        self.target_text = random.choice(self.SENTENCES)
        self.query_one("#target_display").update(f"[b]{self.target_text}[/b]")
        self.query_one("#type_input").value = ""
        self.query_one("#type_input").focus()
        self.start_time = asyncio.get_event_loop().time()

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value
        if text == self.target_text:
            end_time = asyncio.get_event_loop().time()
            duration = end_time - self.start_time
            wpm = (len(text) / 5) / (duration / 60)
            self.query_one("#result_display").update(f"🚀 SPEED: {wpm:.1f} WPM | TIME: {duration:.2f}s")
            self.set_timer(2.0, self.next_round)
        else:
            self.query_one("#result_display").update("❌ MISMATCH. TRY AGAIN.")
