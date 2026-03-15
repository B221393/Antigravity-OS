import os
import vosk
import pyaudio
import json
import sys

# モデルが配置されているパスを指定
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', # go up to 'app'
    'VECTIS_SYSTEM_FILES',
    'vosk-model-small-ja-0.22', # Adjusted path
    'vosk-model-small-ja-0.22'  # Nested directory
)

# 認識結果を保存するファイルパス
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vosk_results.txt")

# モデルパスが存在するか確認
if not os.path.exists(MODEL_PATH):
    sys.stdout.buffer.write(f"Error: Vosk model not found at {MODEL_PATH}\n".encode('utf-8'))
    sys.stdout.buffer.write("Please download the model and extract it to the specified path.\n".encode('utf-8'))
    sys.stdout.buffer.write("Download from: https://alphacephei.com/vosk/models\n".encode('utf-8'))
    exit(1)

# モデルの読み込み
model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000) # 16000はサンプリングレート (Hz)

# PyAudio設定
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000)

# --- Start of new logic ---
try:
    input("録音を開始するにはEnterキーを押してください...")
    sys.stdout.buffer.write("録音中です... 終了するには Ctrl+C を押してください。\n".encode('utf-8'))
    sys.stdout.buffer.write(f"認識結果は {OUTPUT_FILE} に書き込まれます。\n".encode('utf-8'))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        while True:
            data = stream.read(8000)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result['text']:
                    text = result['text']
                    f_out.write(f"{text}\n")
                    f_out.flush() # ファイルにすぐに書き出す
                    sys.stdout.buffer.write(f"認識結果: {text}\n".encode('utf-8')) # コンソールにも出力
            else:
                pass # Partial results can be noisy, so we skip them for now

except KeyboardInterrupt:
    sys.stdout.buffer.write("\n録音を終了し、最終結果を処理しています...\n".encode('utf-8'))
    # Process final recognition result
    final_result = json.loads(rec.FinalResult())
    if final_result['text']:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
            f_out.write(f"{final_result['text']}\n")
        sys.stdout.buffer.write(f"最終認識結果: {final_result['text']}\n".encode('utf-8'))
    sys.stdout.buffer.write("音声認識を停止します。\n".encode('utf-8'))

except Exception as e:
    sys.stdout.buffer.write(f"エラーが発生しました: {e}\n".encode('utf-8'))
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sys.stdout.buffer.write(f"結果は {OUTPUT_FILE} に保存されました。\n".encode('utf-8'))

# --- End of new logic ---
