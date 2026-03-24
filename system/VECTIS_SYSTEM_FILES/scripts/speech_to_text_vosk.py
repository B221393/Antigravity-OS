import os
import vosk
import pyaudio
import json

# モデルが配置されているパスを指定
# ダウンロードしたモデルをVECTIS_SYSTEM_FILES/vosk_model/vosk-model-small-ja-0.22 に配置した場合のパス
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', # go up to 'app'
    'VECTIS_SYSTEM_FILES',
    'vosk-model-small-ja-0.22', # Adjusted path
    'vosk-model-small-ja-0.22'  # Nested directory
)

# モデルパスが存在するか確認
if not os.path.exists(MODEL_PATH):
    print(f"Error: Vosk model not found at {MODEL_PATH}")
    print("Please download the model and extract it to the specified path.")
    print("Download from: https://alphacephei.com/vosk/models")
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

print("Vosk STT started. Speak into microphone (Ctrl+C to exit)")

try:
    while True:
        data = stream.read(8000) # 8000はフレーム数
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if result['text']:
                print("認識結果:", result['text'])
        else:
            # 部分的な認識結果を表示 (オプショナル)
            # partial_result = json.loads(rec.PartialResult())
            # if partial_result['partial']:
            #     print("認識中:", partial_result['partial'])
            pass
except KeyboardInterrupt:
    print("\n音声認識を停止します。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()