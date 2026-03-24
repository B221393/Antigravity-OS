
import threading
import time
import random

# Optional dependencies
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

class VectisVoice:
    """
    VECTIS Standard Voice Module.
    Provides easy access to Microphone Input (SR) and Text-to-Speech (TTS).
    Designed to be plugged into any VECTIS App.
    """
    def __init__(self, callback_function=None):
        self.available = VOICE_AVAILABLE
        self.callback = callback_function
        self.listening = False
        self.thread = None
        self.stop_event = threading.Event()
        
        if self.available:
            # 1. Setup Mic
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 1000
            
            # 2. Setup TTS
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            self._set_voice()
        else:
            print("[VectisVoice] Audio libs missing. Install Check: pip install SpeechRecognition pyttsx3 pyaudio")

    def _set_voice(self):
        try:
            voices = self.engine.getProperty('voices')
            for v in voices:
                if "Haruka" in v.name or "Zira" in v.name:
                    self.engine.setProperty('voice', v.id)
                    break
        except: pass

    def start_listening_loop(self):
        """Starts the background listener thread."""
        if not self.available: return
        if self.thread and self.thread.is_alive(): return

        self.listening = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        print("[VectisVoice] Ear Activated.")

    def stop_listening(self):
        self.listening = False
        self.stop_event.set()
        print("[VectisVoice] Ear Deactivated.")

    def set_callback(self, cb):
        """Update the function to call when text is heard."""
        self.callback = cb

    def speak(self, text):
        """TTS Output (Blocking or Threaded depending on implementation, here blocking is default for simplicity)"""
        if not self.available: return
        try:
            # Run in separate short thread to not block UI
            threading.Thread(target=self._speak_worker, args=(text,), daemon=True).start()
        except: pass

    def _speak_worker(self, text):
        try:
            # Re-init engine in thread provided loop if needed, but pyttsx3 usually needs main loop interaction.
            # Caution: pyttsx3 is finicky with threads. 
            # A safer approach for simple apps is just queuing or running quickly.
            # We will use the existing engine instance but safeguard it.
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[Voice Speak Err] {e}")

    def _worker(self):
        """Background listening loop."""
        while not self.stop_event.is_set():
            if not self.listening:
                time.sleep(1)
                continue
                
            try:
                # Use microphone
                with sr.Microphone() as source:
                    # Adjust for ambient noise occasionally?
                    # self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    try:
                        # Short timeout to keep check loop responsive
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                        text = self.recognizer.recognize_google(audio, language="ja-JP")
                        
                        if text and self.callback:
                            # Send text to main app
                            self.callback(text)
                            
                    except sr.WaitTimeoutError:
                        pass # Just silence
                    except sr.UnknownValueError:
                        pass # Unintelligible
                    except Exception as e:
                        # print(f"SR Error: {e}")
                        time.sleep(1)
                        
            except Exception as e:
                # print(f"Mic Error: {e}")
                time.sleep(1)
