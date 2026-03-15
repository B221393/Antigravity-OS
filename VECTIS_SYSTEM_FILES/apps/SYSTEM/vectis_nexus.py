#!/usr/bin/env python3
"""VECTIS OS v6.1 - Simplified Dashboard"""

import json
import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Button, Label, Static, Input, Log
from textual.binding import Binding

# 設定
VECTIS_ROOT = Path(r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES")
UNIVERSE_FILE = VECTIS_ROOT / "data" / "universe.json"
DAEMON_LOG = VECTIS_ROOT / "apps" / "SYSTEM" / "river_daemon.log"


class HomeScreen(Screen):
    """ホーム - シンプルな4ボタン"""

    BINDINGS = [
        Binding("d", "go_discovery", "情報収集", show=True),
        Binding("s", "go_search", "検索", show=True),
        Binding("g", "go_games", "ゲーム", show=True),
        Binding("q", "quit_app", "終了", show=True),
    ]

    CSS = """
    HomeScreen {
        background: #0d1117;
        align: center middle;
    }
    
    #home_box {
        width: 60;
        height: 24;
        background: #161b22;
        border: round #30363d;
        padding: 1 2;
    }
    
    #title {
        text-align: center;
        color: #58a6ff;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #stats {
        text-align: center;
        color: #8b949e;
        margin-bottom: 1;
    }
    
    .menu_btn {
        width: 100%;
        height: 3;
        margin: 1 0;
    }
    
    #hint {
        text-align: center;
        color: #484f58;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="home_box"):
            yield Label("🚀 VECTIS OS v6.1", id="title")
            yield Label("読込中...", id="stats")
            yield Button("📊 [D] 情報収集", id="btn_discovery", classes="menu_btn", variant="primary")
            yield Button("🔍 [S] 知識検索", id="btn_search", classes="menu_btn", variant="success")
            yield Button("🎮 [G] ゲーム", id="btn_games", classes="menu_btn", variant="warning")
            yield Button("❌ [Q] 終了", id="btn_quit", classes="menu_btn", variant="error")
            yield Label("キーまたはクリックで選択", id="hint")
        yield Footer()

    def on_mount(self):
        self.app.title = "VECTIS OS v6.1"
        self._update_stats()

    def _update_stats(self):
        try:
            if UNIVERSE_FILE.exists():
                kb = UNIVERSE_FILE.stat().st_size / 1024
                with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                nodes = len(data.get("nodes", []))
                self.query_one("#stats").update(f"知識: {kb:.1f}KB ({nodes}件)")
            else:
                self.query_one("#stats").update("知識: 0KB (収集開始してください)")
        except:
            self.query_one("#stats").update("知識: 読込エラー")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "btn_discovery":
            self.app.push_screen("discovery")
        elif btn == "btn_search":
            self.app.push_screen("search")
        elif btn == "btn_games":
            self.app.push_screen("games")
        elif btn == "btn_quit":
            self.app.exit()

    def action_go_discovery(self):
        self.app.push_screen("discovery")

    def action_go_search(self):
        self.app.push_screen("search")

    def action_go_games(self):
        self.app.push_screen("games")

    def action_quit_app(self):
        self.app.exit()


class DiscoveryScreen(Screen):
    """情報収集画面 - 改善版"""

    BINDINGS = [Binding("escape", "go_back", "戻る", show=True)]

    CSS = """
    DiscoveryScreen { background: #0d1117; }
    #disc_title { text-align: center; background: #238636; color: white; padding: 1; }
    #disc_content { height: 1fr; padding: 1; }
    
    #status_panel {
        height: 6;
        background: #161b22;
        border: round #30363d;
        padding: 1;
        margin-bottom: 1;
    }
    
    .status_label { color: #8b949e; }
    .status_value { color: #58a6ff; text-style: bold; }
    
    #disc_log { height: 1fr; background: #0d1117; border: round #30363d; }
    .action_btn { margin: 1 0; width: 100%; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("🌊 情報収集 ([Esc]で戻る)", id="disc_title")
        with Container(id="disc_content"):
            # ステータスパネル
            with Container(id="status_panel"):
                yield Label("📡 デーモン状態:", classes="status_label")
                yield Label("確認中...", id="daemon_status", classes="status_value")
                yield Label("⏱️ 収集間隔:", classes="status_label")
                yield Label("--分", id="interval_display", classes="status_value")
            
            # ログ
            yield Log(id="disc_log")
            
            # アクションボタン
            yield Button("🚀 今すぐ収集開始", id="start_btn", variant="success", classes="action_btn")
            yield Button("🔄 ログ更新", id="refresh_btn", variant="primary", classes="action_btn")
            yield Button("← ホームに戻る", id="back_btn", variant="default", classes="action_btn")
        yield Footer()

    def on_mount(self):
        self._update_status()
        self._load_log()

    def _update_status(self):
        # デーモン状態チェック
        import subprocess
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True, text=True
            )
            if "python.exe" in result.stdout:
                self.query_one("#daemon_status").update("✅ 稼働中")
            else:
                self.query_one("#daemon_status").update("❌ 停止中")
        except:
            self.query_one("#daemon_status").update("確認失敗")
        
        # 間隔表示
        config_file = VECTIS_ROOT / "apps" / "SYSTEM" / "river_config.json"
        try:
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    import json
                    config = json.load(f)
                interval = config.get("interval_seconds", 300)
                self.query_one("#interval_display").update(f"{interval // 60}分ごと")
        except:
            pass

    def _load_log(self):
        log = self.query_one("#disc_log")
        log.clear()
        if DAEMON_LOG.exists():
            try:
                with open(DAEMON_LOG, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-20:]
                for line in lines:
                    log.write(line.strip())
            except:
                log.write("ログ読込エラー")
        else:
            log.write("📭 デーモンログがありません")
            log.write("")
            log.write("「今すぐ収集開始」を押すか、")
            log.write("デーモンを起動してください。")

    def on_button_pressed(self, event: Button.Pressed):
        btn = event.button.id
        if btn == "back_btn":
            self.app.pop_screen()
        elif btn == "start_btn":
            self._start_discovery()
        elif btn == "refresh_btn":
            self._update_status()
            self._load_log()
            self.query_one("#disc_log").write("🔄 更新しました")

    def _start_discovery(self):
        import asyncio
        log = self.query_one("#disc_log")
        log.write("🚀 収集開始リクエスト...")
        
        # river_flow.py を実行
        import subprocess
        script = VECTIS_ROOT / "apps" / "SYSTEM" / "river_flow.py"
        subprocess.Popen(
            ["python", str(script), "--discover"],
            cwd=str(VECTIS_ROOT),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        log.write("✅ 別ウィンドウで収集を開始しました")

    def action_go_back(self):
        self.app.pop_screen()



from textual.widgets import DataTable

class SearchScreen(Screen):
    """知識検索画面 - DataTable版"""

    BINDINGS = [Binding("escape", "go_back", "戻る", show=True)]

    CSS = """
    SearchScreen { background: #0d1117; }
    #search_title { text-align: center; background: #58a6ff; color: white; padding: 1; }
    #search_content { height: 1fr; padding: 1; }
    #search_table { height: 1fr; border: round #58a6ff; background: #161b22; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("🔍 知識検索 ([Esc]で戻る)", id="search_title")
        with Container(id="search_content"):
            yield Input(placeholder="キーワードを入力してEnter...", id="search_input")
            yield DataTable(id="search_table")
            yield Button("← 戻る", id="back_btn", variant="default")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#search_table")
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("ラベル", "タイプ", "詳細")
        self._show_all()

    def _show_all(self):
        table = self.query_one("#search_table")
        table.clear()
        try:
            if UNIVERSE_FILE.exists():
                with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                nodes = data.get("nodes", [])
                for node in nodes[:50]: # Show first 50
                    table.add_row(
                        node.get("label", "?"),
                        node.get("type", "不明"),
                        str(node.get("properties", {}))[:50]
                    )
            else:
                table.add_row("データがありません", "Discoveryを実行してください", "")
        except Exception as e:
            table.add_row("エラー", str(e), "")

    def on_input_submitted(self, event: Input.Submitted):
        q = event.value.lower()
        table = self.query_one("#search_table")
        table.clear()
        
        if not UNIVERSE_FILE.exists():
            table.add_row("データがありません", "", "")
            return
        
        with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for node in data.get("nodes", []):
            if q in node.get("label", "").lower() or q in str(node.get("properties", "")).lower():
                table.add_row(
                    node.get("label", "?"),
                    node.get("type", "不明"),
                    str(node.get("properties", {}))[:50]
                )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back_btn":
            self.app.pop_screen()

    def action_go_back(self):
        self.app.pop_screen()


class GamesScreen(Screen):
    """ゲーム選択"""

    BINDINGS = [Binding("escape", "go_back", "戻る", show=True)]

    CSS = """
    GamesScreen { background: #0d1117; align: center middle; }
    #games_box { width: 50; background: #161b22; border: round #e94560; padding: 2; }
    #games_title { text-align: center; color: #e94560; text-style: bold; margin-bottom: 1; }
    .game_btn { width: 100%; margin: 1 0; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="games_box"):
            yield Label("🎮 ゲーム選択", id="games_title")
            yield Button("🎯 DTキャノン", id="cannon", variant="error", classes="game_btn")
            yield Button("⌨️ タイピング", id="typing", variant="primary", classes="game_btn")
            yield Button("← 戻る", id="back", variant="default", classes="game_btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        btn = event.button.id
        if btn == "cannon":
            self.app.push_screen("cannon")
        elif btn == "typing":
            self.app.push_screen("typing")
        elif btn == "back":
            self.app.pop_screen()

    def action_go_back(self):
        self.app.pop_screen()


class CannonScreen(Screen):
    """DTキャノン"""

    BINDINGS = [
        Binding("escape", "go_back", "戻る", show=True),
        Binding("space", "fire", "発射", show=True),
    ]

    CSS = """
    CannonScreen { background: #1a1a2e; align: center middle; }
    #cannon_box { width: 45; height: 16; background: #16213e; border: heavy #e94560; padding: 1; }
    #cannon_title { text-align: center; color: #e94560; text-style: bold; }
    #target { text-align: center; color: white; margin: 1; }
    #stats { text-align: center; color: #00ff88; }
    #cannon_log { height: 4; margin: 1; }
    .cannon_btn { width: 100%; margin-top: 1; }
    """

    score = 0
    ammo = 5
    TARGETS = ["SNS通知", "自己不信", "バグ", "会議"]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="cannon_box"):
            yield Label("🎯 DTキャノン", id="cannon_title")
            yield Label("", id="target")
            yield Label("", id="stats")
            yield Log(id="cannon_log")
            yield Button("発射 [SPACE]", id="fire", variant="error", classes="cannon_btn")
            yield Button("リロード", id="reload", variant="primary", classes="cannon_btn")
            yield Button("← 戻る", id="back", variant="default", classes="cannon_btn")
        yield Footer()

    def on_mount(self):
        self._spawn()

    def _spawn(self):
        t = random.choice(self.TARGETS)
        self.query_one("#target").update(f"👾 ターゲット: {t}")
        self.query_one("#stats").update(f"弾: {self.ammo} | スコア: {self.score}")

    def action_fire(self):
        self._do_fire()

    def _do_fire(self):
        log = self.query_one("#cannon_log")
        if self.ammo > 0:
            self.ammo -= 1
            if random.random() > 0.3:
                self.score += 100
                log.write("💥 撃破!")
            else:
                log.write("💨 外れ")
            self._spawn()
        else:
            log.write("⚠️ 弾切れ")

    def on_button_pressed(self, event: Button.Pressed):
        btn = event.button.id
        if btn == "fire":
            self._do_fire()
        elif btn == "reload":
            self.ammo = 5
            self.query_one("#cannon_log").write("🔄 リロード")
            self._spawn()
        elif btn == "back":
            self.app.pop_screen()

    def action_go_back(self):
        self.app.pop_screen()


class TypingScreen(Screen):
    """タイピング"""

    BINDINGS = [Binding("escape", "go_back", "戻る", show=True)]

    CSS = """
    TypingScreen { background: #0d1117; align: center middle; }
    #typing_box { width: 50; height: 12; background: #161b22; border: round #58a6ff; padding: 2; }
    #typing_title { text-align: center; color: #58a6ff; text-style: bold; }
    #typing_target { text-align: center; color: white; margin: 1; }
    #typing_result { text-align: center; margin: 1; }
    """

    SENTENCES = ["hello", "world", "python", "vectis"]
    target = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="typing_box"):
            yield Label("⌨️ タイピング", id="typing_title")
            yield Static("", id="typing_target")
            yield Input(placeholder="入力...", id="typing_input")
            yield Label("", id="typing_result")
            yield Button("← 戻る", id="back", variant="default")
        yield Footer()

    def on_mount(self):
        self._next()

    def _next(self):
        self.target = random.choice(self.SENTENCES)
        self.query_one("#typing_target").update(f"入力: {self.target}")
        self.query_one("#typing_input").value = ""
        self.query_one("#typing_result").update("")

    def on_input_submitted(self, event: Input.Submitted):
        if event.value == self.target:
            self.query_one("#typing_result").update("✅ 正解!")
            self.set_timer(0.5, self._next)
        else:
            self.query_one("#typing_result").update("❌ 違う")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.app.pop_screen()

    def action_go_back(self):
        self.app.pop_screen()


class VectisOS(App):
    """VECTIS OS v6.1"""

    CSS = "Screen { background: #0d1117; }"

    SCREENS = {
        "home": HomeScreen,
        "discovery": DiscoveryScreen,
        "search": SearchScreen,
        "games": GamesScreen,
        "cannon": CannonScreen,
        "typing": TypingScreen,
    }

    def on_mount(self):
        self.push_screen("home")


if __name__ == "__main__":
    app = VectisOS()
    app.run()
