import os
import time
import threading
import queue
import json
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import pyautogui

# Add modules to path if needed
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from modules.blogger import BloggerAgent
from modules.vision_action import VisionAgent, ActionAgent
from modules.researcher import ResearchAgent
from modules.voice_input import VoiceAgent
import traceback
from datetime import datetime

# Load Env
load_dotenv(BASE_DIR / ".env")

class SecretaryOrchestrator:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # Use placeholder check
        if self.gemini_key == "your_gemini_api_key_here":
            self.gemini_key = None
            
        self.blogger = BloggerAgent()
        self.vision = VisionAgent(self.gemini_key)
        self.action = ActionAgent()
        self.researcher = ResearchAgent(self.gemini_key, self.groq_key)
        self.voice = VoiceAgent(self.groq_key)

        # Thread-safe queue for commands
        self.execution_queue = queue.Queue()

    def _setup_overlay(self):
        """Creates a minimal Tkinter overlay for recording feedback."""
        try:
            import tkinter as tk
            self.root = tk.Tk()
            self.root.withdraw() # Hide main window
            
            self.overlay = tk.Toplevel(self.root)
            self.overlay.withdraw()
            self.overlay.overrideredirect(True)
            self.overlay.attributes("-topmost", True)
            self.overlay.geometry("+20+20") # Top-left
            
            # Style
            label = tk.Label(
                self.overlay, 
                text="● 録音中... (Enterを離して完了)", 
                fg="white", 
                bg="#FF3366", 
                font=("Helvetica", 12, "bold"),
                padx=15, 
                pady=10
            )
            label.pack()
        except Exception as e:
            print(f"Overlay setup failed: {e}")

    def _show_overlay(self):
        if hasattr(self, 'overlay'):
            self.overlay.deiconify()
            self.root.update()

    def _hide_overlay(self):
        if hasattr(self, 'overlay'):
            self.overlay.withdraw()
            self.root.update()

    def _voice_listener_pynput(self):
        """Global key listener using pynput."""
        try:
            from pynput import keyboard
            
            self.is_enter_pressed = False
            
            def on_press(key):
                if key == keyboard.Key.enter and not self.is_enter_pressed:
                    self.is_enter_pressed = True
                    self.voice.start_recording()
                    self._show_overlay()

            def on_release(key):
                if key == keyboard.Key.enter:
                    self.is_enter_pressed = False
                    self._hide_overlay()
                    audio_file = self.voice.stop_recording()
                    if audio_file:
                        command = self.voice.transcribe_audio(audio_file)
                        if command and len(command.strip()) > 1:
                            print(f"\n[Voice Detected]: {command}")
                            self.execution_queue.put(command)

            print(">> [Background] Global Enter-Hold Listener Started.")
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        except ImportError:
            print("Error: pynput not installed. Voice listener disabled.")

    def run_parallel_voice_loop(self):
        """Main loop that executes commands from the queue while listener runs in background."""
        print("\n=== VECTIS HOLD-TO-TALK MODE ===")
        print("Hold [Enter] to speak commands.")
        print("Say 'Exit' or '終了' to stop.")

        self._setup_overlay()
        if not hasattr(self, 'root'):
            print("UI Loop failed to start. Falling back to command mode.")
            return

        # Start Listener Thread
        listener = threading.Thread(target=self._voice_listener_pynput, daemon=True)
        listener.start()

        try:
            while True:
                try:
                    # Wait for command
                    command = self.execution_queue.get(timeout=1.0)
                    if command:
                        cmd_lower = command.lower()
                        if "exit" in cmd_lower or "終了" in cmd_lower:
                            print("Exiting Secretary Mode.")
                            break
                        
                        self.execute_command(command)
                        self.execution_queue.task_done()
                        print("\n>> Ready for next command.\n")
                except queue.Empty:
                    # Keep Tkinter alive
                    self.root.update()
                    continue
                    
        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            self.root.destroy()

    def execute_command(self, user_instruction):
        print(f"Executing: {user_instruction}")
        
        action_log = []
        research_log = []
        summary = ""

        # 0. Intent Classification (Simple Heuristics)
        # Keywords for specialized modes
        if "カードにして" in user_instruction or "カード化" in user_instruction:
            return self._handle_card_generation(user_instruction)
            
        if "ホロデッキ" in user_instruction or "holodeck" in user_instruction.lower():
            return self._handle_holodeck(user_instruction)
            
        # 0.5 Special Mode: "Browse & Analyze" (Open Site + Extract Info)
        if ("開いて" in user_instruction or "open" in user_instruction.lower()) and \
           ("リスト" in user_instruction or "教えて" in user_instruction or "list" in user_instruction.lower() or "抽出" in user_instruction or "一覧" in user_instruction):
            print(">> Mode: BROWSE & ANALYZE")
            
            # 1. Extract Site Name
            target_site_extraction_prompt = f"Extract the target website name from this command: '{user_instruction}'. Return ONLY the name."
            target_site = self.researcher._call_llm(target_site_extraction_prompt).strip()
            
            # 2. Find URL
            url_prompt = f"Find the official URL for: {target_site}. Return ONLY the URL."
            target_url = self.researcher._call_llm(url_prompt).strip()
            
            if "http" not in target_url:
                target_url = f"https://www.google.com/search?q={target_site}"
            
            print(f"Target URL: {target_url}")
            action_log.append(f"Identified Target URL: {target_url}")

            # 3. Open Browser
            self.action.fast_open(target_url)
            action_log.append(f"Opened URL: {target_url}")
            
            # 4. Fetch & Extract
            print("Fetching page content...")
            content = self.researcher.fetch_url(target_url)
            print("Extracting information...")
            extraction_result = self.researcher.extract_info(content, user_instruction)
            
            summary = f"【BROWSE & ANALYZE】\nTarget: {target_site} ({target_url})\n\n{extraction_result}"
            
            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=["Fetched " + target_url],
                actions=action_log,
                output=summary,
                reflection="Executed in Browse & Analyze mode."
            )
            
            # AUTO CARD
            self._auto_drop_card(target_site, extraction_result)
            return summary

        # 0.8 Special Mode: "Vector Mapping"
        if any(k in user_instruction for k in ["マップ", "地図", "関係", "ベクトル", "位置"]):
            return self._handle_mapping(user_instruction)

        # 0.9 API Usage Check
        if any(k in user_instruction.lower() for k in ["api", "usage", "cost", "使用量", "料金", "いくら", "円", "money"]):
            from modules.api_tracker import APITracker
            return APITracker().get_report()

        # 2. Researching Phase (if intent matches)
        search_keywords = ["検索", "調べて", "research", "search", "教えて", "とは", "news", "ニュース", "について"]
        if any(k in user_instruction for k in search_keywords):
            print(">> Mode: RESEARCH (Deep)")
            summary = self.researcher.deep_research(user_instruction)
            
            research_log.append(f"Deep Research on: {user_instruction}")
            action_log.append(f"Researched: {user_instruction}")
            
            if any(k in user_instruction for k in ["まとめて", "保存"]):
                self.researcher.save_summary_to_file(summary)
                action_log.append("Exported summary.")
            
            self._auto_drop_card(user_instruction, summary)

            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=research_log,
                actions=action_log,
                output=summary,
                reflection="Executed in deep research mode."
            )
            return summary

        # 3. Vision/Action Phase (PC operation)
        print(">> Mode: VISION/ACTION")
        screenshot = self.vision.capture_screen()
        action_log.append("Captured screen state.")
        
        if self.vision.model:
            print("Decision: Identifying target...")
            target_data = self.vision.identify_ui(user_instruction, screenshot)
            
            if "x" in target_data and "y" in target_data:
                label = target_data.get('label', 'target')
                print(f"Target found: {label} at ({target_data['x']}, {target_data['y']})")
                action_log.append(f"Detected {label} via Vision.")
                self.action.click(target_data['x'], target_data['y'])
                action_log.append(f"Clicked {label}.")
            else:
                print("No UI target found.")
        
        self.blogger.log_entry(
            user_instruction=user_instruction,
            research_process=research_log,
            actions=action_log,
            output=summary,
            reflection="Executed in Vision/Action mode."
        )
        return summary

    def _auto_drop_card(self, topic, content):
        try:
            from apps.knowledge_cards.engine import CardEngine
            ce = CardEngine()
            card_data = self.researcher.generate_card_data(topic, content)
            if card_data:
                ce.save_kcard(card_data)
                print(f"★ Knowledge Card Acquired: {card_data['title']} ({card_data['rarity']})")
        except: pass

    def _handle_card_generation(self, user_instruction):
        print(f"[DEBUG] Card generation triggered")
        try:
            from apps.knowledge_cards.engine import CardEngine
            engine = CardEngine()
            summary = self.researcher.summarize_results(user_instruction, "Generate Card Content")
            card_data = self.researcher.generate_card_data(user_instruction, summary)
            if card_data:
                engine.save_kcard(card_data)
                self.blogger.log_entry(user_instruction, [], [f"Card Created: {card_data['title']}"], f"Card: {card_data['title']}", "Success")
                return f"Card Created: {card_data['title']}"
        except Exception as e:
            print(f"Card error: {e}")
        return None

    def _handle_holodeck(self, user_instruction):
        print(f"[DEBUG] Holodeck triggered")
        try:
            from modules.holodeck import HolodeckEngine
            from apps.knowledge_cards.engine import CardEngine
            holodeck = HolodeckEngine(self.researcher, CardEngine())
            h_data = holodeck.generate_multidimensional_ideas(user_instruction)
            if h_data:
                holodeck.save_session(h_data)
                holodeck.export_ideas_as_cards(h_data)
                return f"Holodeck Complete: {h_data['summary'][:100]}"
        except Exception as e:
            print(f"Holodeck error: {e}")
        return None

    def _handle_mapping(self, user_instruction):
        print(f"[DEBUG] Vector Mapping triggered")
        try:
            from apps.knowledge_cards.mapper import KnowledgeMapper
            mapper = KnowledgeMapper(self.researcher)
            result = mapper.generate_map(user_instruction)
            return f"Map Generated: {result}"
        except Exception as e:
            return f"Mapping Error: {e}"

    def run_autonomous_loop(self, goal):
        """
        Ralph-style Autonomous Loop (The 'Manus' Core).
        Continuous observation and action until goal is reached.
        """
        print(f"\n🚀 [VECTIS] INITIALIZING AUTONOMOUS MISSION")
        print(f"🎯 MISSION GOAL: {goal}")
        print(f"🕒 START TIME: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        max_steps = 20
        history = []
        
        for i in range(max_steps):
            print(f"\n🧠 [THINK] Step {i+1}/{max_steps}...")
            
            # 1. Observe
            screenshot_path = os.path.abspath(f"outputs/logs/auto_step_{i}.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            self.vision.capture_screen(screenshot_path)
            
            # 2. Reason
            res_x, res_y = pyautogui.size()
            prompt = f"""
            GOAL: {goal}
            CURRENT_STEP: {i+1}
            MAX_STEPS: {max_steps}
            
            Analyze the current screen and decide the next action. 
            The screen resolution is {res_x}x{res_y}. 
            ALWAYS return coordinates in the range of this resolution.
            
            [AVAILABLE ACTIONS]
            - CLICK(x, y): Click at coordinates.
            - TYPE(text): Type text. Ensure focal point is set before typing.
            - PRESS(key): Press a key (e.g. 'enter', 'tab', 'esc', 'win').
            - WAIT(seconds): Wait for a bit (e.g., 2, 5).
            - SEARCH(query): Open browser and search.
            - DONE: Goal is achieved. Return a final summary.
            - FAIL: Goal is impossible or stuck.
            
            [THINKING PROCESS]
            1. What do I see? (Apps, text, icons)
            2. What is the gap between current state and goal?
            3. What is the most reliable next step?
            
            Return ONLY a raw JSON object:
            {{
                "action": "CLICK" | "TYPE" | "PRESS" | "WAIT" | "SEARCH" | "DONE" | "FAIL",
                "param": "value_as_string",
                "x": integer_coord,
                "y": integer_coord,
                "thought": "Internal monologue about why this step",
                "summary": "Brief explanation for the user"
            }}
            """
            
            try:
                img = Image.open(screenshot_path)
                # Resize if profile is too large
                if img.width > 2000:
                    img = img.resize((img.width // 2, img.height // 2))
                
                response = self.vision.model.generate_content([prompt, img])
                res_text = response.text.strip()
                
                # Robust extraction
                json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
                if not json_match:
                    print(f"⚠️ [WARN] AI returned non-JSON response. Retrying step...")
                    continue
                    
                decision = json.loads(json_match.group(0))
                action = decision.get("action")
                thought = decision.get("thought", "Calculating...")
                user_feedback = decision.get("summary", "Executing action...")
                
                print(f"🔮 [PLAN] {user_feedback}")
                print(f"   ∟ {thought}")
                
                history.append(f"Step {i+1}: {user_feedback}")
                
                if action == "DONE":
                    print(f"\n✅ [MISSION COMPLETE] {decision.get('param', 'Goal Reached')}")
                    self.blogger.deep_reflect(goal, history)
                    break
                elif action == "FAIL":
                    print(f"\n❌ [MISSION FAILED] {decision.get('param', 'Reason unknown')}")
                    self.blogger.deep_reflect(goal, history)
                    break
                elif action == "CLICK":
                    target_x, target_y = decision['x'], decision['y']
                    print(f"👉 [ACTION] Clicking at ({target_x}, {target_y})")
                    self.action.click(target_x, target_y)
                elif action == "TYPE":
                    txt = decision['param']
                    print(f"⌨️ [ACTION] Typing: {txt}")
                    self.action.type_text(txt)
                elif action == "PRESS":
                    key = decision['param']
                    print(f"🔘 [ACTION] Pressing: {key}")
                    self.action.press_key(key)
                elif action == "WAIT":
                    sec = float(decision.get('param', 2))
                    print(f"⏳ [ACTION] Waiting {sec}s...")
                    time.sleep(sec)
                elif action == "SEARCH":
                    q = decision['param']
                    print(f"🔍 [ACTION] Searching for: {q}")
                    self.action.fast_open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
                
                time.sleep(2.0) # Stability wait
                
            except Exception as e:
                print(f"🚨 [ERROR] Step {i+1} failed: {e}")
                traceback.print_exc()
                history.append(f"Step {i+1}: AI Error - {e}")
                time.sleep(3.0)
        else:
            print("\n⏹️ [STOPPED] Max steps reached without completion.")
            self.blogger.deep_reflect(goal, history)

    def run_remote_loop(self):
        """Monitor command_queue.json for remote commands."""
        command_file = BASE_DIR / "command_queue.json"
        print(f"\n=== VECTIS REMOTE BRIDGE: {command_file} ===")
        last_timestamp = ""
        while True:
            if command_file.exists():
                try:
                    with open(command_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ts = data.get("timestamp")
                    if ts != last_timestamp:
                        cmd = data.get("command")
                        print(f"\n[REMOTE]: {cmd}")
                        self.execute_command(cmd)
                        last_timestamp = ts
                except: pass
            time.sleep(1.0)

    def run_chat_loop(self):
        print(f"\n=== VECTIS CHAT MODE ===")
        while True:
            try:
                cmd = input("\n[USER]: ").strip()
                if not cmd: continue
                if cmd.lower() in ["exit", "終了"]: break
                self.execute_command(cmd)
            except KeyboardInterrupt: break

if __name__ == "__main__":
    orch = SecretaryOrchestrator()
    print("\n--- VECTIS SECRETARY ORCHESTRATOR ---")
    print("[1] Voice Mode (Parallel)")
    print("[2] Chat Mode")
    print("[3] Remote Mode")
    print("[4] Autonomous Mode (Ralph Mode)")
    choice = input("Choice: ").strip()
    
    if choice == "2":
        orch.run_chat_loop()
    elif choice == "3":
        orch.run_remote_loop()
    elif choice == "4":
        goal = input("Enter Goal for Ralph Mode: ").strip()
        orch.run_autonomous_loop(goal)
    else:
        orch.run_parallel_voice_loop()
