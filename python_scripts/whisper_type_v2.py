import os
import sys
import time
import threading
import sounddevice as sd
import numpy as np
import requests
import json
from faster_whisper import WhisperModel
import pyperclip
import pyautogui
import keyboard
import winsound

# --- CONFIGURATION (V2.4 - SNAP & NATURAL) ---
MODEL_SIZE = "base"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
TOGGLE_KEY = "alt"
SAMPLE_RATE = 16000
OLLAMA_URL = "http://localhost:11434/api/generate"

# --- NATURAL PROMPT (Less AI-flavor, More Human-Refined) ---
NATURAL_PROMPT = """
以下の話言葉を、意味を変えずに「自然で知的な書き言葉」へ整理してください。
- 語尾の「えー」「あの」を消す。
- 「ANTIGRAVITY」「Qumi」などの固有名詞はそのまま活かす。
- 解説は一切不要。結果の文章のみを返せ。
- 3秒以内に終わらせるようにシンプルにまとめよ。
"""

is_recording = False
recorded_data = []

print(f"--- [VECTIS SNAP-VOICE V2.4] Starting... ---")

# initialize Whisper
try:
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
except Exception:
    sys.exit(1)

def play_sound(freq, duration):
    winsound.Beep(freq, duration) # Blocking beep is okay for clicks

def thinking_chirp():
    # Subtle "thinking" sound in background
    for _ in range(3):
        if not is_processing: break
        winsound.Beep(1200, 30)
        time.sleep(0.3)

is_processing = False

def refine_natural(raw_text):
    global is_processing
    is_processing = True
    # Start background chirp
    threading.Thread(target=thinking_chirp).start()
    
    prompt = f"{NATURAL_PROMPT}\n\n対象: {raw_text}"
    payload = {"model": "gemma:2b", "prompt": prompt, "stream": False}
    try:
        # 3 second timeout for high snappiness
        response = requests.post(OLLAMA_URL, json=payload, timeout=3.5)
        is_processing = False
        return response.json().get("response", raw_text).strip()
    except:
        is_processing = False
        return raw_text # If slow or error, give raw IMMEDIATELY

def type_text(text):
    if not text: return
    keyboard.release('alt')
    keyboard.release('ctrl')
    keyboard.release('shift')
    pyautogui.press('esc')
    time.sleep(0.1)
    pyperclip.copy(text)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')

def handle_toggle(event):
    global is_recording, recorded_data
    if event.event_type == 'down':
        if not is_recording:
            is_recording = True
            recorded_data = []
            play_sound(1000, 50)
            print("[LIVE] Recording...")
        else:
            is_recording = False
            play_sound(600, 50)
            print("[SYNC] Processing...")
            # Threading transcription for GUI responsiveness (even if console)
            threading.Thread(target=process_audio).start()

def process_audio():
    if not recorded_data: return
    audio = np.concatenate(recorded_data, axis=0).flatten()
    segments, _ = model.transcribe(audio, beam_size=5, language="ja", vad_filter=True)
    raw_text = "".join([s.text for s in segments]).strip()
    
    if raw_text:
        # Try to refine quickly
        refined = refine_natural(raw_text)
        type_text(refined)

def audio_callback(indata, frames, time, status):
    if is_recording:
        recorded_data.append(indata.copy())

def main():
    # Use keyboard.hook for more reliable toggle detection
    keyboard.on_press_key(TOGGLE_KEY, handle_toggle)
    print(f"--- READY (Alt Toggle) ---")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', callback=audio_callback):
        while True:
            time.sleep(0.1)

if __name__ == "__main__":
    main()
