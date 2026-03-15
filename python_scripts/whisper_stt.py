"""
Whisper Speech-to-Text (リアルタイム風)
========================================
マイクから音声を録音 → Whisperで高精度テキスト化。
Voskより圧倒的に精度が高い。

使い方:
  python whisper_stt.py               # デフォルト: smallモデル, 5秒チャンク
  python whisper_stt.py --model medium # より高精度
  python whisper_stt.py --chunk 10     # 10秒ごとに認識
  python whisper_stt.py --once         # 1回だけ録音して認識（Enterで停止）
"""

import os
import sys
import argparse
import tempfile
import wave
import json
import datetime

try:
    import pyaudio
except ImportError:
    print("ERROR: pyaudio が必要です。 pip install pyaudio")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("ERROR: openai-whisper が必要です。 pip install openai-whisper")
    sys.exit(1)

# ──────────────────────── 設定 ────────────────────────

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_FRAMES = 1024

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "whisper_results.txt")

# ──────────────────────── 関数 ────────────────────────

def record_chunk(stream, duration_sec):
    """指定秒数の音声を録音してバイト列で返す"""
    frames = []
    num_reads = int(SAMPLE_RATE / CHUNK_FRAMES * duration_sec)
    for _ in range(num_reads):
        data = stream.read(CHUNK_FRAMES, exception_on_overflow=False)
        frames.append(data)
    return b"".join(frames)


def record_until_enter(stream):
    """Enterキーが押されるまで録音"""
    import threading

    frames = []
    stop_flag = threading.Event()

    def wait_for_enter():
        input()  # Enter待ち
        stop_flag.set()

    t = threading.Thread(target=wait_for_enter, daemon=True)
    t.start()

    print("🎤 録音中... (Enterで停止)")
    while not stop_flag.is_set():
        data = stream.read(CHUNK_FRAMES, exception_on_overflow=False)
        frames.append(data)

    return b"".join(frames)


def save_wav(audio_bytes, filepath):
    """バイト列をWAVファイルに保存"""
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_bytes)


def transcribe(model, wav_path):
    """WhisperでWAVファイルを文字起こし"""
    result = model.transcribe(
        wav_path,
        language="ja",
        fp16=False,  # CPU使用時はFalse
    )
    return result["text"].strip()


# ──────────────────────── メイン ────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Whisper Speech-to-Text")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisperモデルサイズ (default: small)")
    parser.add_argument("--chunk", type=int, default=5,
                        help="連続モードの録音チャンク秒数 (default: 5)")
    parser.add_argument("--once", action="store_true",
                        help="1回だけ録音 (Enterで停止)")
    args = parser.parse_args()

    # モデルロード
    print(f"📦 Whisperモデル '{args.model}' をロード中...")
    model = whisper.load_model(args.model)
    print(f"✅ モデルロード完了!")

    # PyAudio初期化
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_FRAMES)

    print(f"📝 認識結果は {OUTPUT_FILE} に書き込まれます")
    print("=" * 60)

    tmp_wav = os.path.join(tempfile.gettempdir(), "whisper_stt_chunk.wav")

    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f_out.write(f"\n--- セッション開始: {timestamp} ---\n")
            f_out.flush()

            if args.once:
                # ワンショットモード
                audio = record_until_enter(stream)
                save_wav(audio, tmp_wav)
                print("🔄 認識中...")
                text = transcribe(model, tmp_wav)
                if text:
                    print(f"📝 結果: {text}")
                    f_out.write(f"{text}\n")
                    f_out.flush()
                else:
                    print("（音声が検出されませんでした）")
            else:
                # 連続モード
                print(f"🎤 {args.chunk}秒ごとに音声認識します (Ctrl+C で終了)")
                print()
                while True:
                    print(f"🎤 録音中 ({args.chunk}秒)...", end="", flush=True)
                    audio = record_chunk(stream, args.chunk)
                    save_wav(audio, tmp_wav)
                    print(" 🔄 認識中...", end="", flush=True)
                    text = transcribe(model, tmp_wav)
                    if text:
                        print(f"\r📝 {text}" + " " * 30)
                        f_out.write(f"{text}\n")
                        f_out.flush()
                    else:
                        print("\r（無音）" + " " * 40)

    except KeyboardInterrupt:
        print("\n\n🛑 音声認識を終了します。")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        # 一時ファイル削除
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)
        print(f"💾 結果は {OUTPUT_FILE} に保存されています。")


if __name__ == "__main__":
    main()
