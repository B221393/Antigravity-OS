import warnings
# Suppress Gemini SDK deprecation warning globally
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import os
import time
import threading
import queue
from dotenv import load_dotenv
from modules.blogger import BloggerAgent
from modules.vision_action import VisionAgent, ActionAgent
from modules.researcher import ResearchAgent
from modules.voice_input import VoiceAgent

# Load environment variables
load_dotenv()

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

    def _voice_listener_thread(self):
        """Background thread that continuously listens for commands."""
        print(">> [Background] Voice Listener Started. Speak anytime.")
        while True:
            # Listening duration
            audio_file = self.voice.record_audio(duration=8) 
            command = self.voice.transcribe_audio(audio_file)
            
            # Filter noise / Fillers
            ignore_list = [".", "。", "...", "abc", "えっと", "あのー", "んー", "あ", "うん"]
            if not command or len(command.strip()) < 2 or command.strip() in ignore_list:
                # print(".", end="", flush=True) # Minimize noise logs
                continue

            print(f"\n[Voice Detected]: {command}")
            print(">> Queued for execution.")
            self.execution_queue.put(command)
            time.sleep(0.5)

    def run_parallel_voice_loop(self):
        """Main loop that executes commands from the queue while listener runs in background."""
        print("\n=== VECTIS PARALLEL MODE (Threaded) ===")
        print("Listening in background... (You can speak while I work)")
        print("Say 'Exit' or '終了' to stop.")

        # Start Listener Thread
        listener = threading.Thread(target=self._voice_listener_thread, daemon=True)
        listener.start()

        try:
            while True:
                try:
                    # Wait for command (blocking w/ timeout to allow checking for exit)
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
                    continue
                    
        except KeyboardInterrupt:
            print("\nStopped by user.")

    def chain_execute(self, instructions):
        print(f"[CHAIN MODE] Processing: {instructions}")
        steps_raw = self.researcher.generate_steps(instructions)
        print(f"\n[PLAN]\n{steps_raw}\n")
        
        # Simple parsing and execution
        steps = steps_raw.split("\n")
        results = []
        for step in steps:
            if not step.strip() or ":" not in step: continue
            print(f"Executing: {step}")
            res = self.execute_command(step)
            results.append(res)
        
        return results

    def execute_command(self, user_instruction):
        print(f"Executing: {user_instruction}")
        
        # 0. Intent Classification (Simple Heuristics)
        # Keywords for specialized modes
        if "カードにして" in user_instruction or "カード化" in user_instruction:
            return self._handle_card_generation(user_instruction)
            
        if "ホロデッキ" in user_instruction or "holodeck" in user_instruction.lower():
            return self._handle_holodeck(user_instruction)
            
        # 0.5 Special Mode: "Browse & Analyze" (Open Site + Extract Info)
        # e.g., "Mynaviを開いてES内容をリスト化して"
        if ("開いて" in user_instruction or "open" in user_instruction.lower()) and \
           ("リスト" in user_instruction or "教えて" in user_instruction or "list" in user_instruction.lower() or "抽出" in user_instruction or "一覧" in user_instruction):
            print(">> Mode: BROWSE & ANALYZE")
            
            # ... (Browse Logic) ...
            # 1. Find URL
            search_q = f"URL for: {user_instruction}"
            # Ask LLM to extract the *target site name* first.
            target_site_extraction_prompt = f"Extract the target website name from this command: '{user_instruction}'. Return ONLY the name."
            target_site = self.researcher._call_llm(target_site_extraction_prompt).strip()
            
            # Use ResearchAgent to find the URL textually first.
            url_prompt = f"Find the official URL for: {target_site}. Return ONLY the URL."
            target_url = self.researcher._call_llm(url_prompt).strip()
            
            if "http" not in target_url:
                target_url = f"https://www.google.com/search?q={target_site}"
            
            print(f"Target URL: {target_url}")
            action_log.append(f"Identified Target URL: {target_url}")

            # 2. Open Browser (Action)
            self.action.fast_open(target_url)
            action_log.append(f"Opened URL: {target_url}")
            
            # 3. Fetch Content (Background)
            print("Fetching page content...")
            content = self.researcher.fetch_url(target_url)
            
            # 4. Extract Info
            print("Extracting information...")
            extraction_result = self.researcher.extract_info(content, user_instruction)
            print(f"Analysis Result:\n{extraction_result}")
            
            summary = f"【BROWSE & ANALYZE】\nTarget: {target_site} ({target_url})\n\n{extraction_result}"
            
            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=["Fetched " + target_url],
                actions=action_log,
                output=summary,
                reflection="Executed in Browse & Analyze mode."
            )
            
            # --- AUTO CARD GENERATION ---
            try:
                from apps.knowledge_cards.engine import CardEngine
                ce = CardEngine()
                card_data = self.researcher.generate_card_data(target_site, extraction_result)
                if card_data:
                    ce.save_kcard(card_data)
                    print(f"★ Knowledge Card Acquired: {card_data['title']} ({card_data['rarity']})")
            except Exception as e:
                pass
            # ----------------------------
            
            return summary

        # 0.8 Special Mode: "Vector Mapping"
        # e.g., "就活の軸でマップを作って", "ファイルの関係性を見せて"
        if "マップ" in user_instruction or "地図" in user_instruction or "関係" in user_instruction or "ベクトル" in user_instruction or "位置" in user_instruction:
            return self._handle_mapping(user_instruction)

        # 0.9 API Usage Check
        if user_instruction.lower() in ["api", "usage", "cost", "使用量", "料金", "いくら", "円", "money"]:
            from modules.api_tracker import APITracker
            return APITracker().get_report()

        # 0.99 Onishi Practice Mode
        if "練習" in user_instruction or "practice" in user_instruction.lower() or "大西" in user_instruction:
            return self._handle_practice(user_instruction)

        # 0.999 Ideation App (Interactive Map)
        if "アイデア" in user_instruction or "整理" in user_instruction or "brainstorm" in user_instruction.lower():
            return self._handle_ideation(user_instruction)

        # Keywords for search/research (Broadened)
        search_keywords = ["検索", "調べて", "research", "search", "教えて", "とは", "news", "ニュース", "について"]
        is_search = any(k in user_instruction for k in search_keywords)

        # Keywords for search/research (Broadened)
        search_keywords = ["検索", "調べて", "research", "search", "教えて", "とは", "news", "ニュース", "について"]
        is_search = any(k in user_instruction for k in search_keywords)
        
        summary = ""
        action_log = []
        research_log = []
        
        # 1. Researching Phase (if intent matches)
        if is_search:
            print(">> Mode: RESEARCH (Deep)")
            
            # Use Deep Research (Real-time Search)
            summary = self.researcher.deep_research(user_instruction)
            
            print(f"Research Summary: {summary[:100]}...")
            research_log.append(f"Deep Research on: {user_instruction}")
            research_log.append(f"Summary: {summary[:100]}...")
            action_log.append(f"Researched: {user_instruction}")
            
            # Save summary if asked
            if "まとめて" in user_instruction or "保存" in user_instruction:
                self.researcher.save_summary_to_file(summary)
                action_log.append("Exported summary.")
            
            # --- AUTO CARD GENERATION ---
            # "Life is a Game": Convert research into a loot drop (Card)
            try:
                from apps.knowledge_cards.engine import CardEngine
                ce = CardEngine()
                card_data = self.researcher.generate_card_data(user_instruction, summary)
                if card_data:
                    ce.save_kcard(card_data)
                    print(f"★ Knowledge Card Acquired: {card_data['title']} ({card_data['rarity']})")
                    action_log.append(f"Card Drop: {card_data['title']}")
            except Exception as e:
                print(f"[Warn] Card drop failed: {e}")
            # ----------------------------

            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=research_log,
                actions=action_log,
                output=summary,
                reflection="Executed in deep research mode."
            )
            return summary

        # 2. Vision/Action Phase (Default fallback for PC operation)
        print(">> Mode: VISION/ACTION")
        screenshot = self.vision.capture_screen()
        action_log.append("Captured screen state.")
        
        if self.vision.model:
            print("Decision: Identifying target...")
            target_data = self.vision.identify_ui(user_instruction, screenshot)
            
            if "x" in target_data and "y" in target_data:
                label = target_data.get('label', 'target')
                print(f"Target found: {label} at ({target_data['x']}, {target_data['y']})")
                action_log.append(f"Detected {label} via Vision Reasoning.")
                self.action.click(target_data['x'], target_data['y'])
                action_log.append(f"Clicked {label}.")
            else:
                print("Vision: Direct path/Search fallback.")
                # self.action.fast_open("https://www.google.com/search?q=" + user_instruction.replace(" ", "+"))
                # action_log.append("Opened browser via Fast Path fallback.")
                print("No target found. (Skipping fallback to avoid chaos)")

        # 3. Blogging Phase
        self.blogger.log_entry(
            user_instruction=user_instruction,
            research_process=research_log, # Will be empty if not research mode
            actions=action_log,
            output=summary, # Will be empty if not research mode
            reflection="Executed in autonomous loop (Vision/Action)."
        )
        
        return summary

    def _handle_card_generation(self, user_instruction):
        print(f"[DEBUG] Card generation triggered")
        action_log = []
        try:
            from card_engine import CardEngine
            engine = CardEngine()
            # We need content. If just a command, maybe run a quick research?
            # For simplicity, we ask LLM to generate content from the topic.
            summary = self.researcher.summarize_results(user_instruction, "Generate Card Content")
            card_data = self.researcher.generate_card_data(user_instruction, summary)
            if card_data:
                engine.save_kcard(card_data)
                action_log.append(f"Card Created: {card_data['title']}")
                print(f"Card Created: {card_data['title']}")
                self.blogger.log_entry(
                    user_instruction=user_instruction,
                    research_process=[],
                    actions=action_log,
                    output=f"Card Created: {card_data['title']}",
                    reflection="Card generation executed."
                )
                return f"Card Created: {card_data['title']}"
        except Exception as e:
            print(f"[DEBUG] Card generation error: {e}")
            action_log.append(f"Card generation error: {e}")
            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=[],
                actions=action_log,
                output=f"Card generation error: {e}",
                reflection="Card generation failed."
            )
        return None

    def _handle_holodeck(self, user_instruction):
        print(f"[DEBUG] Holodeck triggered")
        action_log = []
        try:
            from modules.holodeck import HolodeckEngine
            from card_engine import CardEngine
            ce = CardEngine()
            holodeck = HolodeckEngine(self.researcher, ce)
            h_data = holodeck.generate_multidimensional_ideas(user_instruction)
            if h_data:
                holodeck.save_session(h_data)
                holodeck.export_ideas_as_cards(h_data)
                summary = f"【HOLODECK ANALYSIS】\n{h_data['summary']}\n\nTop Idea: {h_data['ideas'][0]['title']}"
                print(summary)
                action_log.append("Holodeck insights generated.")
                self.blogger.log_entry(
                    user_instruction=user_instruction,
                    research_process=[],
                    actions=action_log,
                    output=summary,
                    reflection="Holodeck analysis executed."
                )
                return summary
        except Exception as e:
            print(f"[DEBUG] Holodeck error: {e}")
            action_log.append(f"Holodeck error: {e}")
            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=[],
                actions=action_log,
                output=f"Holodeck error: {e}",
                reflection="Holodeck analysis failed."
            )
        return None

    def _handle_mapping(self, user_instruction):
        print(f"[DEBUG] Vector Mapping triggered")
        action_log = []
        try:
            from apps.knowledge_cards.mapper import KnowledgeMapper
            mapper = KnowledgeMapper(self.researcher)
            
            print("Generating Vector Map...")
            result = mapper.generate_map(user_instruction)
            print(result)
            
            action_log.append(f"Generated Vector Map for: {user_instruction}")
            
            summary = f"【VECTOR MAPPING】\nVisualization created based on: {user_instruction}\nResult: {result}"
            self.blogger.log_entry(
                user_instruction=user_instruction,
                research_process=[],
                actions=action_log,
                output=summary,
                reflection="Generated knowledge vector map."
            )
            return summary
            
        except Exception as e:
            print(f"[DEBUG] Mapping error: {e}")
            return f"Mapping Error: {e}"

        except Exception as e:
            print(f"[DEBUG] Mapping error: {e}")
            return f"Mapping Error: {e}"

    def _handle_practice(self, user_instruction):
        print(">> Launching Onishi Layout Trainer...")
        try:
            from apps.onishi.trainer import OnishiTrainer
            trainer = OnishiTrainer()
            trainer.run()
            return "Practice session finished."
        except Exception as e:
            return f"Practice Error: {e}"

        except Exception as e:
            return f"Practice Error: {e}"

    def _handle_ideation(self, user_instruction):
        print(">> Launching Job Hunting Ideation Space...")
        try:
            from apps.job_hunting.ideation_app import IdeationApp
            app = IdeationApp()
            app.run()
            return "Ideation session finished."
        except Exception as e:
            return f"Ideation Error: {e}"

    def run_remote_loop(self):
        """Monitor command_queue.json for remote commands."""
        command_file = "command_queue.json"
        print("\n=== VECTIS REMOTE BRIDGE MODE: ACTIVE ===")
        print("Waiting for commands from mobile...")
        last_timestamp = ""
        try:
            while True:
                if os.path.exists(command_file):
                    try:
                        with open(command_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        current_timestamp = data.get("timestamp")
                        if current_timestamp != last_timestamp:
                            command = data.get("command")
                            print(f"\n[REMOTE]: {command}")
                            self.execution_queue.put(command) # Reuse queue
                            last_timestamp = current_timestamp
                    except: pass
                
                # Check for queue items (Unified handling)
                try:
                    cmd = self.execution_queue.get(timeout=0.1)
                    if cmd:
                        self.execute_command(cmd)
                        self.execution_queue.task_done()
                except queue.Empty:
                    pass
                    
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped.")

    def run_chat_loop(self):
        """Infinite loop for text chat (Standard Input for IME support)."""
        print(f"\n=== VECTIS CHAT MODE: ACTIVE ===")
        print("Type your command and press Enter.")
        print("Say 'Exit' or '終了' to stop.")
        
        try:
            while True:
                try:
                    command = input("\n[USER]: ").strip()
                except EOFError:
                    break
                    
                if not command:
                    continue
                    
                if command.lower() in ["exit", "終了"]:
                    print("Exiting Chat Mode.")
                    break
                    
                self.execute_command(command)
                
        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    orch = SecretaryOrchestrator()
    print("Select Mode:")
    print("[1] Voice Mode (Parallel)")
    print("[2] Chat Mode")
    print("[3] Remote Mode (Mobile Bridge)")
    choice = input("Choice [1/2/3]: ").strip()
    if choice == "2":
        orch.run_chat_loop()
    elif choice == "3":
        orch.run_remote_loop()
    else:
        orch.run_parallel_voice_loop()
