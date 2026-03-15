import os
import time
import datetime
import threading
import sounddevice as sd
import soundfile as sf
import pyautogui
import queue
import sys

# Configurations
LOG_DIR = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\data\SEMINAR_LOGS"
PID_FILE = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools\seminar_logger.pid"
SCREENSHOT_INTERVAL = 30  # Seconds
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2
AUDIO_SUBTYPE = 'PCM_24'

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_session_dir():
    now = datetime.datetime.now()
    session_name = now.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(LOG_DIR, session_name)
    ensure_dir(path)
    return path

def capture_screenshots(session_path, stop_event):
    print("Screenshot thread started.")
    while not stop_event.is_set():
        try:
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            filename = f"screen_{timestamp}.png"
            filepath = os.path.join(session_path, filename)
            
            # Take screenshot
            sc = pyautogui.screenshot()
            sc.save(filepath)
            print(f"Captured: {filename}")
            
            time.sleep(SCREENSHOT_INTERVAL)
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            time.sleep(5)

def record_audio(session_path, stop_event):
    print("Audio recording thread started.")
    filename = os.path.join(session_path, "audio_log.wav")
    
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(indata.copy())

    try:
        with sf.SoundFile(filename, mode='x', samplerate=AUDIO_SAMPLE_RATE,
                          channels=AUDIO_CHANNELS, subtype=AUDIO_SUBTYPE) as file:
            with sd.InputStream(samplerate=AUDIO_SAMPLE_RATE, channels=AUDIO_CHANNELS, callback=callback):
                while not stop_event.is_set():
                    file.write(q.get())
                
                # Flush remaining data
                while not q.empty():
                    file.write(q.get())

    except Exception as e:
        print(f"Error recording audio: {e}")

def main():
    print("=== Seminar Logger Started ===")
    
    # Write PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    print(f"PID: {os.getpid()}")
    print(f"Logs will be saved to: {LOG_DIR}")
    
    session_path = get_session_dir()
    print(f"Current Session: {session_path}")
    
    stop_event = threading.Event()
    
    # Start Threads
    screen_thread = threading.Thread(target=capture_screenshots, args=(session_path, stop_event))
    audio_thread = threading.Thread(target=record_audio, args=(session_path, stop_event))
    
    screen_thread.start()
    audio_thread.start()
    
    print("Recording... Press Ctrl+C or use stop_seminar_log.bat to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping recording (KeyboardInterrupt)...")
    finally:
        stop_event.set()
        screen_thread.join()
        audio_thread.join()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        print("Recording stopped. Data saved.")

if __name__ == "__main__":
    main()
