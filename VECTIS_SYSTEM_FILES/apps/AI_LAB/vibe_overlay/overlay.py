import sys
import os
import json
import time
import keyboard
import threading
import psutil
if sys.platform == "win32":
    import win32gui
    import win32process
    import win32con
    import win32api
    import ctypes

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPalette

# =================================================================================
# Configuration
# =================================================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 450
FONT_FAMILY = "Segoe UI"
KEY_SIZE = 60
GAP = 4

# Colors - GHOST TRANSPARENT (Almost Invisible)
BG_COLOR = "rgba(0, 0, 0, 1)" # 1/255 opacity
KEY_BG_DEFAULT = "rgba(0, 0, 0, 5)" # 5/255 opacity
KEY_BG_ACTIVE = "rgba(0, 120, 215, 80)" # Active keys slightly visible
KEY_TEXT_COLOR = "rgba(255, 255, 255, 50)" # Faint text
DESC_TEXT_COLOR = "rgba(0, 255, 255, 80)" # Faint desc

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shortcuts.json")

# =================================================================================
# Keyboard Layout Data (Staggered)
# =================================================================================
# Tuple structure: (KeyName, WidthMultipler)
KEYBOARD_ROWS = [
    # Row 0: F-Keys
    [("Esc", 1.0), ("F1", 1.0), ("F2", 1.0), ("F3", 1.0), ("F4", 1.0), ("F5", 1.0), ("F6", 1.0), ("F7", 1.0), ("F8", 1.0), ("F9", 1.0), ("F10", 1.0), ("F11", 1.0), ("F12", 1.0)],
    # Row 1: Numbers
    [("`", 1.0), ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0), ("5", 1.0), ("6", 1.0), ("7", 1.0), ("8", 1.0), ("9", 1.0), ("0", 1.0), ("-", 1.0), ("=", 1.0), ("Back", 2.0)],
    # Row 2: QWERTY (Tab 1.5)
    [("Tab", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0), ("T", 1.0), ("Y", 1.0), ("U", 1.0), ("I", 1.0), ("O", 1.0), ("P", 1.0), ("[", 1.0), ("]", 1.0), ("\\", 1.5)],
    # Row 3: ASDF (Caps 1.75)
    [("Caps", 1.75), ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0), ("G", 1.0), ("H", 1.0), ("J", 1.0), ("K", 1.0), ("L", 1.0), (";", 1.0), ("'", 1.0), ("Enter", 2.25)],
    # Row 4: ZXCV (Shift 2.25)
    [("Shift", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0), ("B", 1.0), ("N", 1.0), ("M", 1.0), (",", 1.0), (".", 1.0), ("/", 1.0), ("Shift", 2.75)],
    # Row 5: Space (Ctrl 1.25)
    [("Ctrl", 1.25), ("Win", 1.25), ("Alt", 1.25), ("Space", 6.25), ("Alt", 1.25), ("Win", 1.25), ("Menu", 1.25), ("Ctrl", 1.25)]
]

# =================================================================================
# Logic
# =================================================================================

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        if sys.platform == "win32":
            self.set_click_through()

        # Data
        self.shortcuts_db = {}
        self.registered_hotkeys = [] 
        self.load_config()
        self.register_global_hotkeys()
        
        self.current_context = "default"
        self.active_modifiers = set()
        
        # UI
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._center_bottom()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(GAP)
        
        # Header (Context Info)
        self.header_label = QLabel("SYSTEM")
        self.header_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        self.header_label.setStyleSheet(f"color: #FFFFFF; background-color: {KEY_BG_DEFAULT}; padding: 4px; border-radius: 4px;")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.header_label)

        # Keyboard Container
        self.keys_widgets = {} 
        self.build_keyboard()

        # Timers
        self.context_timer = QTimer()
        self.context_timer.timeout.connect(self.check_active_window)
        self.context_timer.start(1000)

        self.modifier_timer = QTimer()
        self.modifier_timer.timeout.connect(self.check_modifiers)
        self.modifier_timer.start(50)

    def set_click_through(self):
        hwnd = int(self.winId())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    def _center_bottom(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 20
        self.move(x, y)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.shortcuts_db = json.load(f)
            except:
                self.shortcuts_db = {}

    def register_global_hotkeys(self):
        try:
            for hk in self.registered_hotkeys:
                keyboard.remove_hotkey(hk)
        except:
            pass
        self.registered_hotkeys = []

        defaults = self.shortcuts_db.get("default", {}).get("shortcuts", [])
        for s in defaults:
            if "command" not in s: continue
            
            keys = s["keys"]
            cmd = s["command"]
            try:
                hk = keyboard.add_hotkey(keys, lambda c=cmd: os.system(f'start "" "{c}"'))
                self.registered_hotkeys.append(hk)
                print(f"[Overlay] Registered launcher: {keys} -> {cmd}")
            except Exception as e:
                print(f"[Overlay] Failed to register {keys}: {e}")

    def build_keyboard(self):
        for row_idx, row_data in enumerate(KEYBOARD_ROWS):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(GAP)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            for key, width_mult in row_data:
                w = int(KEY_SIZE * width_mult)
                container = QFrame()
                container.setFixedSize(w, KEY_SIZE)
                
                layout = QVBoxLayout(container)
                layout.setContentsMargins(2, 2, 2, 2)
                layout.setSpacing(0)
                
                lbl_key = QLabel(key)
                lbl_key.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
                lbl_key.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_key.setStyleSheet("color: #AAAAAA;")
                
                lbl_desc = QLabel("")
                lbl_desc.setFont(QFont(FONT_FAMILY, 8))
                lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_desc.setStyleSheet(f"color: {DESC_TEXT_COLOR};")
                lbl_desc.setWordWrap(False)

                layout.addWidget(lbl_key)
                layout.addWidget(lbl_desc)

                self.keys_widgets[key] = {
                    "widget": container,
                    "key_lbl": lbl_key,
                    "desc_lbl": lbl_desc,
                    "default_bg": KEY_BG_DEFAULT
                }
                
                row_layout.addWidget(container)
            
            row_layout.addStretch()
            self.main_layout.addLayout(row_layout)

    def check_modifiers(self):
        mods = set()
        if keyboard.is_pressed('ctrl'): mods.add("Ctrl")
        if keyboard.is_pressed('alt'): mods.add("Alt")
        if keyboard.is_pressed('shift'): mods.add("Shift")
        if keyboard.is_pressed('windows'): mods.add("Win")
        
        if mods != self.active_modifiers:
            self.active_modifiers = mods
            self.update_key_display()

    def check_active_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            proc = psutil.Process(pid)
            proc_name = proc.name().lower()
            title = win32gui.GetWindowText(hwnd)
            
            new_context = "default"
            match_name = "SYSTEM"
            
            for key, conf in self.shortcuts_db.items():
                if key == "default": continue
                
                p_match = False
                if "process" in conf:
                    for p in conf["process"]:
                        if p.lower() in proc_name:
                            p_match = True
                            break
                
                t_match = False
                if "title_keyword" in conf:
                    for k in conf["title_keyword"]:
                        if k.lower() in title.lower():
                            t_match = True
                            break
                
                if p_match or t_match:
                    new_context = key
                    match_name = conf.get("name", key.upper())
                    break
            
            self.header_label.setText(f"[{match_name}]")
            
            if new_context != self.current_context:
                self.current_context = new_context
                self.update_key_display()

        except Exception as e:
            pass

    def update_key_display(self):
        for key, w in self.keys_widgets.items():
            w["widget"].setStyleSheet(f"background-color: {w['default_bg']}; border-radius: 4px;")
            w["desc_lbl"].setText("")
            if key in self.active_modifiers:
                w["widget"].setStyleSheet(f"background-color: {KEY_BG_ACTIVE}; border-radius: 4px;")

        context_data = self.shortcuts_db.get(self.current_context, self.shortcuts_db.get("default"))
        if not context_data: return
        shortcuts = context_data.get("shortcuts", [])
        
        for s in shortcuts:
            keys = s["keys"]
            desc = s["desc"]
            parts = [p.strip() for p in keys.split("+")]
            trigger_key = parts[-1]
            required_mods = set(parts[:-1])
            
            layout_key = self.map_key_to_layout(trigger_key)
            if not layout_key or layout_key not in self.keys_widgets: continue

            norm_active = set()
            for m in self.active_modifiers:
                if m == "Win": norm_active.add("Win")
                else: norm_active.add(m)

            norm_req_mods = set()
            for m in required_mods:
                if m.lower() in ["ctrl", "control"]: norm_req_mods.add("Ctrl")
                elif m.lower() in ["alt"]: norm_req_mods.add("Alt")
                elif m.lower() in ["shift"]: norm_req_mods.add("Shift")
                elif m.lower() in ["win", "windows", "meta"]: norm_req_mods.add("Win")
                else: norm_req_mods.add(m)
            
            if norm_req_mods == self.active_modifiers:
                self.keys_widgets[layout_key]["desc_lbl"].setText(desc)
                self.keys_widgets[layout_key]["widget"].setStyleSheet(f"background-color: #333333; border: 1px solid {DESC_TEXT_COLOR}; border-radius: 4px;")

    def map_key_to_layout(self, key_str):
        k = key_str.upper()
        # Direct Map
        for row in KEYBOARD_ROWS:
            for key, _ in row:
                if key.upper() == k: return key
        
        if key_str.lower() in ["esc", "escape"]: return "Esc"
        if key_str.lower() in ["ent", "return"]: return "Enter"
        if key_str.lower() in ["del", "delete"]: return "Back"
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec())
