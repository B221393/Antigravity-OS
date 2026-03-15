import sounddevice as sd
from scipy.io.wavfile import write
import datetime
import os
import threading

def record_audio():
    fs = 44100  # サンプリングレート
    print("--- 音声録音開始 ---")
    print("録音中... 終了するには Enter キーを押してください。")
    
    recording = []
    stop_event = threading.Event()

    def callback(indata, frames, time, status):
        recording.append(indata.copy())

    # 録音ストリームの開始
    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input() # Enterキー待機
    
    import numpy as np
    audio_data = np.concatenate(recording, axis=0)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audio_practice_{timestamp}.wav"
    write(filename, fs, audio_data)
    
    print(f"--- 録音終了 ---")
    print(f"保存先: {filename}")

if __name__ == "__main__":
    record_audio()
