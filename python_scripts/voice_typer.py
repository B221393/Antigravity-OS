"""
Voice Typer v2 - 音声で直接テキスト入力
========================================
管理者権限不要！ ffmpegも不要！

F8キーを押している間に録音 → 離したらWhisperで認識 → アクティブなウィンドウに自動貼り付け。
Gemini CLI、VS Code、ブラウザ、どこでも使える。

使い方:
  python voice_typer.py               # デフォルト: smallモデル, F8キー
  python voice_typer.py --model base  # 軽量・高速
  python voice_typer.py --model medium # より高精度
  python voice_typer.py --key f10     # F10キーに変更

操作:
  F8 長押し → 録音開始
  F8 離す   → 認識 → テキスト自動入力
  Ctrl+C    → 終了
"""

import os
import sys
import argparse
import tempfile
import wave
import struct
import threading
import time
import ctypes
import ctypes.wintypes

import numpy as np

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
    from pynput import keyboard as pynput_kb
except ImportError:
    print("ERROR: pip install pynput")
    sys.exit(1)


# ──────────────── 設定 ────────────────

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_FRAMES = 1024


# ──────────────── ffmpegバイパス: WAV → numpy float32 ────────────────

def load_wav_as_float32(wav_path):
    """WAVファイルをnumpy float32配列として読み込む（ffmpeg不要）"""
    with wave.open(wav_path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    # 16bit PCM → float32 [-1.0, 1.0]
    if sampwidth == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")

    # ステレオ → モノラル
    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)

    # Whisperは30秒パディングが必要（内部でやるが念のため）
    return audio


# ──────────────── Windows クリップボード ────────────────

def _setup_clipboard_api():
    """64bit Windows 対応: ctypes API の型定義を正しく設定"""
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # 64bit ポインター対応（これがないとポインター切り捨てでクラッシュ）
    kernel32.GlobalAlloc.argtypes = [ctypes.wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p

    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p

    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.wintypes.BOOL

    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.restype = ctypes.c_void_p

    user32.OpenClipboard.argtypes = [ctypes.wintypes.HWND]
    user32.OpenClipboard.restype = ctypes.wintypes.BOOL

    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = ctypes.wintypes.BOOL

    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = ctypes.wintypes.BOOL

    user32.SetClipboardData.argtypes = [ctypes.wintypes.UINT, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p

    return kernel32, user32

# 起動時に一度だけ設定
_kernel32, _user32 = _setup_clipboard_api()


def set_clipboard_text(text):
    """ctypes で直接Windows APIを呼びクリップボードに設定"""
    CF_UNICODETEXT = 13

    # リトライ付き（他アプリがクリップボードを掴んでいる場合がある）
    for attempt in range(3):
        if _user32.OpenClipboard(None):
            break
        time.sleep(0.1)
    else:
        # ctypes 失敗 → PowerShell フォールバック
        return _clipboard_fallback(text)

    try:
        _user32.EmptyClipboard()

        # UTF-16エンコード（null終端）
        data = text.encode('utf-16-le') + b'\x00\x00'
        h_mem = _kernel32.GlobalAlloc(0x0042, len(data))  # GMEM_MOVEABLE | GMEM_ZEROINIT
        if not h_mem:
            return _clipboard_fallback(text)

        ptr = _kernel32.GlobalLock(h_mem)
        if not ptr:
            _kernel32.GlobalFree(h_mem)
            return _clipboard_fallback(text)

        ctypes.memmove(ptr, data, len(data))
        _kernel32.GlobalUnlock(h_mem)

        result = _user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        return bool(result)
    except Exception:
        return _clipboard_fallback(text)
    finally:
        _user32.CloseClipboard()


def _clipboard_fallback(text):
    """PowerShell フォールバック"""
    try:
        import subprocess as sp
        escaped = text.replace("'", "''")
        sp.run(
            ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{escaped}'"],
            capture_output=True, timeout=5, check=True
        )
        return True
    except Exception:
        return False


def simulate_ctrl_v():
    """ctypes で Ctrl+V をシミュレート（keyboardライブラリ不要）"""
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002

    user32 = ctypes.windll.user32

    # Ctrl 押す
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.02)
    # V 押す
    user32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.02)
    # V 離す
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    # Ctrl 離す
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


# ──────────────── ユーザー辞書 ────────────────

class UserDictionary:
    """認識結果を辞書で補正する"""

    def __init__(self, dict_path=None):
        self.replacements = {}
        if dict_path is None:
            dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_typer_dict.txt")
        self.dict_path = dict_path
        self._load()

    def _load(self):
        """辞書ファイルを読み込む"""
        if not os.path.exists(self.dict_path):
            # サンプル辞書を生成
            self._create_sample()
            return

        with open(self.dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) == 2:
                    self.replacements[parts[0]] = parts[1]

        if self.replacements:
            print(f"📖 辞書ロード: {len(self.replacements)} 件")

    def _create_sample(self):
        """サンプル辞書ファイルを作成"""
        sample = """# Voice Typer ユーザー辞書
# フォーマット: 認識されやすい誤り<TAB>正しい表記
# 例:
# ベクティス\tVECTIS
# じぇみに\tGemini
# パイソン\tPython
# ささとる\tサポートする
"""
        with open(self.dict_path, 'w', encoding='utf-8') as f:
            f.write(sample)
        print(f"📖 サンプル辞書を作成: {self.dict_path}")

    def apply(self, text):
        """辞書の置換を適用"""
        for wrong, correct in self.replacements.items():
            text = text.replace(wrong, correct)
        return text


# ──────────────── メインクラス ────────────────

class VoiceTyper:
    def __init__(self, model_name="small", hotkey="f8"):
        self.hotkey = hotkey
        self.hotkey_vk = self._parse_hotkey(hotkey)
        self.recording = False
        self.frames = []
        self.p = None
        self.stream = None
        self.processing = False
        self.tmp_wav = os.path.join(tempfile.gettempdir(), "voice_typer_rec.wav")

        # ユーザー辞書
        self.dictionary = UserDictionary()

        print(f"📦 Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print(f"✅ モデルロード完了!")

    def _parse_hotkey(self, key_str):
        """ホットキー文字列をpynputのKeyオブジェクトに変換"""
        key_map = {
            'f1': pynput_kb.Key.f1, 'f2': pynput_kb.Key.f2,
            'f3': pynput_kb.Key.f3, 'f4': pynput_kb.Key.f4,
            'f5': pynput_kb.Key.f5, 'f6': pynput_kb.Key.f6,
            'f7': pynput_kb.Key.f7, 'f8': pynput_kb.Key.f8,
            'f9': pynput_kb.Key.f9, 'f10': pynput_kb.Key.f10,
            'f11': pynput_kb.Key.f11, 'f12': pynput_kb.Key.f12,
        }
        return key_map.get(key_str.lower(), pynput_kb.Key.f9)

    def start(self):
        """メインループ開始"""
        self.p = pyaudio.PyAudio()

        print()
        print("╔══════════════════════════════════════════════╗")
        print("║  🎤 Voice Typer v2 - 管理者権限不要          ║")
        print(f"║  [{self.hotkey.upper()}] 長押し → 録音                   ║")
        print("║  離す → 認識 → テキスト自動入力              ║")
        print("║  Ctrl+C → 終了                               ║")
        print("╚══════════════════════════════════════════════╝")
        print()
        print(f"💡 辞書ファイル: voice_typer_dict.txt を編集してカスタム変換を追加")
        print()

        # pynput リスナー（管理者権限不要）
        with pynput_kb.Listener(
            on_press=self._on_key_down,
            on_release=self._on_key_up
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                pass
            finally:
                self._cleanup()

    def _on_key_down(self, key):
        """キー押下 → 録音開始"""
        if key != self.hotkey_vk:
            return
        if self.recording or self.processing:
            return

        self.recording = True
        self.frames = []

        try:
            self.stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_FRAMES
            )
        except Exception as e:
            print(f"❌ マイクエラー: {e}")
            self.recording = False
            return

        print("🔴 録音中...", end="", flush=True)

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

    def _on_key_up(self, key):
        """キー離す → 録音停止 → 認識 → 貼り付け"""
        if key != self.hotkey_vk:
            return
        if not self.recording:
            return

        self.recording = False
        self.processing = True

        # ストリーム停止
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if not self.frames:
            print(" (空)")
            self.processing = False
            return

        duration = len(self.frames) * CHUNK_FRAMES / SAMPLE_RATE
        print(f" ⏹ ({duration:.1f}秒)")

        # 短すぎる録音は無視
        if duration < 0.3:
            print("   (短すぎます)")
            self.processing = False
            return

        # WAV保存
        audio_data = b"".join(self.frames)
        with wave.open(self.tmp_wav, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)

        # Whisper認識（別スレッドで）
        threading.Thread(target=self._transcribe_and_type, daemon=True).start()

    def _transcribe_and_type(self):
        """Whisperで認識 → クリップボード経由で貼り付け"""
        print("   🔄 認識中...", end="", flush=True)

        try:
            # ★ ffmpegバイパス: WAVをnumpy配列で直接読み込む
            audio_np = load_wav_as_float32(self.tmp_wav)

            # Whisper に numpy 配列を直接渡す（ffmpeg 呼び出しをスキップ）
            result = self.model.transcribe(
                audio_np,
                language="ja",
                fp16=False,
            )
            text = result["text"].strip()

            # ユーザー辞書で補正
            text = self.dictionary.apply(text)

            if text:
                print(f"\r   ✅ 「{text}」")

                # 少し待ってから貼り付け
                time.sleep(0.3)

                # ctypes で直接クリップボード操作（PowerShell/subprocess 不要）
                if set_clipboard_text(text):
                    time.sleep(0.1)
                    simulate_ctrl_v()
                    print(f"   ⌨️  入力完了!")
                else:
                    print(f"   ❌ クリップボードへのコピーに失敗しました")
            else:
                print("\r   （音声未検出）        ")
        except Exception as e:
            print(f"\r   ❌ エラー: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.processing = False
            print()

    def _cleanup(self):
        """終了処理"""
        print("\n🛑 Voice Typer を終了します。")
        self.recording = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
        if self.p:
            self.p.terminate()
        if os.path.exists(self.tmp_wav):
            os.remove(self.tmp_wav)


# ──────────────── メイン ────────────────

def main():
    parser = argparse.ArgumentParser(description="Voice Typer v2 - 音声直接入力（管理者権限不要）")
    parser.add_argument("--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisperモデル (default: small)")
    parser.add_argument("--key", default="f8",
                        help="録音トリガーキー (default: f8)")
    args = parser.parse_args()

    vt = VoiceTyper(model_name=args.model, hotkey=args.key)
    vt.start()


if __name__ == "__main__":
    main()
