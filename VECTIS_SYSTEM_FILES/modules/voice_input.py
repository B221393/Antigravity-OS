import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from groq import Groq
import os
import threading
import queue

class VoiceAgent:
    def __init__(self, groq_api_key):
        self.groq_client = None
        if groq_api_key:
            self.groq_client = Groq(api_key=groq_api_key)
        else:
            print("VoiceAgent: Groq API Key not provided. Transcription will be disabled.")
        
        self.fs = 44100  # Sample rate
        self.filename = "command.wav"
        self.recording = False
        self.audio_data = []
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if self.recording:
            self.audio_data.append(indata.copy())

    def start_recording(self):
        """Starts recording audio in a non-blocking way."""
        if self.recording:
            return
        
        print(">> Recording started...")
        self.recording = True
        self.audio_data = []
        self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self._audio_callback)
        self.stream.start()

    def stop_recording(self):
        """Stops recording and saves the audio to a file."""
        if not self.recording:
            return None
        
        print(">> Recording stopped.")
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if not self.audio_data:
            return None
            
        audio_array = np.concatenate(self.audio_data, axis=0)
        wav.write(self.filename, self.fs, audio_array)
        return self.filename

    def record_audio(self, duration=5):
        """Records audio for a fixed duration (Legacy/Sync)."""
        print(f"Recording for {duration} seconds... Speak now!")
        recording = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1)
        sd.wait()
        wav.write(self.filename, self.fs, recording)
        return self.filename

    def transcribe_audio(self, filename):
        """Transcribes audio file using Groq Whisper API."""
        if not self.groq_client:
            print("Transcription skipped: Groq client not initialized.")
            return ""
            
        if not filename or not os.path.exists(filename):
            return ""
        
        print("Transcribing...")
        try:
            with open(filename, "rb") as file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(filename, file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            return transcription
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
