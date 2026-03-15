"""
EGO Voice Router v3 (Strategic Coach Mode)
==========================================
音声入力から「リサーチ」「タスク」「アイデア」に加え、
「面接練習（自動添削）」機能を呼び出す。

追加コマンド:
「練習、[質問名]」 -> 自分の回答を録音・文字起こしし、回答集と比較するための準備を行う。
"""

import os
import sys
import wave
import tempfile
import threading
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# 依存ライブラリ
try:
    import pyaudio
    import whisper
    import keyboard
    import pyperclip
except ImportError:
    print("MISSING LIBRARY: pip install pyaudio openai-whisper keyboard pyperclip")
    sys.exit(1)

# ──────────────── 設定 ────────────────

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_FRAMES = 1024

BASE_DIR = Path(r"C:\Users\Yuto\desktop\app\VECTIS_SYSTEM_FILES")
TASKS_FILE = BASE_DIR / "documents" / "notes" / "tasks.md"
IDEAS_FILE = BASE_DIR / "IDEAS_LOG.md"
LOG_FILE = BASE_DIR / "USER_REQUEST_LOG.md"
RESEARCH_DIR = BASE_DIR / "documents" / "research"
ANSWERS_FILE = BASE_DIR / "documents" / "2026-02-18_Brexa_Interview_Answers.md"
COACH_LOG_FILE = BASE_DIR / "documents" / "research" / "INTERVIEW_COACH_LOG.md"

# ──────────────── クラス ────────────────

class EgoVoiceRouterV3:
    def __init__(self, model_name="small", hotkey="space"):
        self.hotkey = hotkey
        self.recording = False
        self.frames = []
        self.p = None
        self.stream = None
        self.tmp_wav = os.path.join(tempfile.gettempdir(), "ego_voice_v3.wav")

        print(f"📦 EGO Agent: Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print(f"✅ システムオンライン。戦略的コーチングモード有効。")

    def start(self):
        self.p = pyaudio.PyAudio()
        print("\n" + "="*50)
        print("🎙️ EGO Voice Router v3 (Strategic Coach)")
        print(f"   [{self.hotkey}] 長押しでコマンド入力")
        print("   例: 「練習、自己紹介」「リサーチ、メイテック」")
        print("="*50 + "\n")

        keyboard.on_press_key(self.hotkey, self._on_key_down, suppress=True)
        keyboard.on_release_key(self.hotkey, self._on_key_up, suppress=True)

        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt: pass
        finally: self._cleanup()

    def _on_key_down(self, event):
        if self.recording: return
        self.recording = True
        self.frames = []
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_FRAMES)
        print("🔴 録音中...", end="", flush=True)
        threading.Thread(target=self._record_loop, daemon=True).start()

    def _record_loop(self):
        while self.recording:
            try: self.frames.append(self.stream.read(CHUNK_FRAMES, exception_on_overflow=False))
            except: break

    def _on_key_up(self, event):
        if not self.recording: return
        self.recording = False
        if self.stream: self.stream.stop_stream(); self.stream.close(); self.stream = None
        print(f" ⏹ 停止")
        audio_data = b"".join(self.frames)
        with wave.open(self.tmp_wav, 'wb') as wf:
            wf.setnchannels(CHANNELS); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE); wf.writeframes(audio_data)
        threading.Thread(target=self._transcribe_and_route, daemon=True).start()

    def _transcribe_and_route(self):
        print("   🔄 解析中...", end="", flush=True)
        try:
            result = self.model.transcribe(self.tmp_wav, language="ja", fp16=False)
            text = result["text"].strip()
            if not text: return
            self._execute_action(text)
        except Exception as e: print(f"\r   ❌ エラー: {e}")

    def _execute_action(self, text):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. 面接練習モード
        if text.startswith("練習"):
            q_name = text.replace("練習", "").lstrip("、, ").strip()
            print(f"\r   🎤 練習記録中: {q_name}")
            
            entry = f"\n# 🥊 Interview Practice: {q_name} ({timestamp})\n"
            entry += f"## あなたの回答:\n{text}\n"
            entry += f"\n> [AIへの指示]: 以下の回答を '{ANSWERS_FILE}' の内容と比較し、\n"
            entry += f"> 「結論ファーストか」「BREXA理念への言及」「具体性」の観点で添削してください。\n"
            
            self._append_to_file(COACH_LOG_FILE, entry)
            msg = f"✅ 練習記録完了: {COACH_LOG_FILE} に保存しました。"

        # 2. リサーチ・コマンド
        elif any(text.startswith(k) for kw in ["リサーチ", "ニュース"] for k in [kw]):
            query = text.replace("リサーチ", "").replace("ニュース", "").lstrip("、, ").strip()
            print(f"\r   🔍 '{query}' を即時リサーチ中...")
            results = self._fetch_news(query)
            header = f"\n# 🔍 Research: {query} ({timestamp})\n"
            self._append_to_file(RESEARCH_DIR / "DYNAMIC_RESEARCH.md", header + "\n".join(results) + "\n")
            msg = f"✅ リサーチ完了: {query}"

        # 3. タスク・コマンド
        elif text.startswith("タスク"):
            content = text.replace("タスク", "", 1).lstrip("、, ").strip()
            self._append_to_file(TASKS_FILE, f"\n- [ ] {content} (音声: {timestamp})")
            msg = f"✅ Task登録: {content}"

        # 4. アイデア・コマンド
        elif text.startswith("アイデア"):
            content = text.replace("アイデア", "", 1).lstrip("、, ").strip()
            self._append_to_file(IDEAS_FILE, f"\n\n## 💡 Idea ({timestamp})\n{content}\n")
            msg = f"💡 Idea保存: {content}"

        # 5. デフォルト (ログ)
        else:
            self._append_to_file(LOG_FILE, f"\n- {timestamp}: {text}")
            msg = f"📝 Log保存: {text}"

        print(f"\r   {msg}")
        pyperclip.copy(text)

    def _fetch_news(self, query):
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            with urllib.request.urlopen(url) as response:
                root = ET.fromstring(response.read())
            return [f"*   **[{item.find('title').text}]({item.find('link').text})** ({item.find('pubDate').text})" for item in root.findall(".//item")[:5]]
        except: return ["リサーチエラー"]

    def _append_to_file(self, file_path, content):
        if not file_path.parent.exists(): file_path.parent.mkdir(parents=True)
        with open(file_path, "a", encoding="utf-8") as f: f.write(content)

    def _cleanup(self):
        print("\n🛑 終了。")
        if self.p: self.p.terminate()
        if os.path.exists(self.tmp_wav): os.remove(self.tmp_wav)
        keyboard.unhook_all()

if __name__ == "__main__":
    EgoVoiceRouterV3().start()
