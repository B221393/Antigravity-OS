import os
import sounddevice as sd
import numpy as np
import whisper
import pyperclip
import pyautogui
import time
import keyboard # Already installed by Antigravity
import winsound  # Built-in for Windows Sound Feedback

# --- SETTINGS ---
WHISPER_MODEL = "base"
SAMPLE_RATE = 16000
PUSH_BUTTON = 'alt' # PTT Key (Alt)

def beep_start():
    winsound.Beep(880, 100) # Higher A tone

def beep_stop():
    winsound.Beep(440, 100) # Lower A tone

def record_ptt(fs=SAMPLE_RATE):
    # Wait for the key press to start
    keyboard.wait(PUSH_BUTTON)
    
    # Visual Feedback is hard with no window, so use Sound
    beep_start()
    
    recorded_data = []
    
    # Stream for arbitrary duration
    def callback(indata, frames, time, status):
        recorded_data.append(indata.copy())
        
    with sd.InputStream(samplerate=fs, channels=1, dtype='float32', callback=callback):
        while keyboard.is_pressed(PUSH_BUTTON):
            time.sleep(0.01)
            
    beep_stop()
    if not recorded_data:
        return None
        
    return np.concatenate(recorded_data, axis=0).flatten()

def transcribe_whisper(audio_data):
    # Load model only once
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_data)
    return result["text"].strip()

def type_text(text):
    if not text:
        return
    
    # Formula for reliability
    pyautogui.press('esc')
    time.sleep(0.1)
    pyperclip.copy(text)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')

def main():
    while True:
        try:
            audio = record_ptt()
            if audio is not None and len(audio) > 1600:
                text = transcribe_whisper(audio)
                if text:
                    type_text(text)
        except Exception as e:
            # Silent logging?
            # os.system(f'echo Error: {e} >> error_log.txt')
            time.sleep(1)

if __name__ == "__main__":
    main()
