"""
Voice-to-Clipboard (Push-to-Talk)
==================================
スペースキーを押している間に録音 → 離したらWhisperで認識 → クリップボードに自動コピー。
Gemini CLIやどんなテキストボックスにも Ctrl+V で貼り付けられる。

使い方:
  管理者権限でターミナルを開き:
  python voice_to_clipboard.py
  python voice_to_clipboard.py --model medium   # より高精度
  python voice_to_clipboard.py --key ctrl+shift+space  # ホットキー変更

操作:
  スペースキー長押し → 録音開始
  スペースキー離す → 認識 → クリップボードにコピー
  Ctrl+C で終了
"""

import os
import sys
import argparse
import tempfile
import wave
import threading

try:
    import pyaudio
except ImportError:
    print("ERROR: pip install pyaudio")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("ERROR: pip install openai-whisper")
    sys.exit(1)

try:
    import keyboard
except ImportError:
    print("ERROR: pip install keyboard")
    sys.exit(1)

try:
    import pyperclip
except ImportError:
    print("ERROR: pip install pyperclip")
    sys.exit(1)


# ──────────────── 設定 ────────────────

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_FRAMES = 1024

# ──────────────── クラス ────────────────

class VoiceToClipboard:
    def __init__(self, model_name="small", hotkey="space"):
        self.hotkey = hotkey
        self.recording = False
        self.frames = []
        self.p = None
        self.stream = None
        self.tmp_wav = os.path.join(tempfile.gettempdir(), "vtc_recording.wav")

        print(f"📦 Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print(f"✅ モデルロード完了!")

    def start(self):
        """メインループ開始"""
        self.p = pyaudio.PyAudio()

        print()
        print("=" * 50)
        print(f"🎤 Voice-to-Clipboard 準備完了!")
        print(f"   [{self.hotkey}] を押している間 → 録音")
        print(f"   離す → 認識 → クリップボードにコピー")
        print(f"   Ctrl+C で終了")
        print("=" * 50)
        print()

        # ホットキー登録
        keyboard.on_press_key(self.hotkey, self._on_key_down, suppress=True)
        keyboard.on_release_key(self.hotkey, self._on_key_up, suppress=True)

        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()

    def _on_key_down(self, event):
        """キー押下 → 録音開始"""
        if self.recording:
            return  # 既に録音中

        self.recording = True
        self.frames = []

        # マイクストリーム開始
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_FRAMES
        )

        print("🔴 録音中...", end="", flush=True)

        # 録音スレッド開始
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

    def _record_loop(self):
        """録音ループ（別スレッド）"""
        while self.recording:
            try:
                data = self.stream.read(CHUNK_FRAMES, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                break

    def _on_key_up(self, event):
        """キー離す → 録音停止 → 認識 → クリップボード"""
        if not self.recording:
            return

        self.recording = False

        # ストリーム停止
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if not self.frames:
            print(" (空)")
            return

        print(f" ⏹ 停止 ({len(self.frames) * CHUNK_FRAMES / SAMPLE_RATE:.1f}秒)")

        # WAV保存
        audio_data = b"".join(self.frames)
        with wave.open(self.tmp_wav, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)

        # Whisper認識（別スレッドで）
        threading.Thread(target=self._transcribe, daemon=True).start()

    def _transcribe(self):
        """Whisperで認識 → クリップボード"""
        print("   🔄 認識中...", end="", flush=True)

        try:
            result = self.model.transcribe(
                self.tmp_wav,
                language="ja",
                fp16=False,
            )
            text = result["text"].strip()

            if text:
                pyperclip.copy(text)
                print(f"\r   📋 コピー完了: {text}")
                print(f"   → Ctrl+V で貼り付けてください")
                print()
            else:
                print("\r   （音声が検出されませんでした）")
                print()
        except Exception as e:
            print(f"\r   ❌ エラー: {e}")
            print()

    def _cleanup(self):
        """終了処理"""
        print("\n🛑 終了します。")
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()
        if os.path.exists(self.tmp_wav):
            os.remove(self.tmp_wav)
        keyboard.unhook_all()


# ──────────────── メイン ────────────────

def main():
    parser = argparse.ArgumentParser(description="Voice-to-Clipboard (Push-to-Talk)")
    parser.add_argument("--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisperモデル (default: small)")
    parser.add_argument("--key", default="space",
                        help="録音トリガーキー (default: space)")
    args = parser.parse_args()

    vtc = VoiceToClipboard(model_name=args.model, hotkey=args.key)
    vtc.start()


if __name__ == "__main__":
    main()
