import subprocess
import threading
import os

def speak(text):
    """
    Speaks text using Windows built-in TTS (PowerShell/System.Speech).
    Runs in a separate thread to prevent blocking the UI.
    """
    if not text: return

    # Clean text for PowerShell command line safety
    # PowerShell uses backtick ` for escape, but double quotes need careful handling
    # We will replace double quotes with single quotes for simplicity in the speech string
    safe_text = text.replace('"', "'").replace("\n", " ").replace("\r", "")
    
    # PowerShell command to speak
    # We use -EncodedCommand ideally, but simple string passing is often enough for simple TTS
    # Let's use a simpler approach: creating a temporary VBS script or just direct PS
    
    # Direct PS Approach
    # Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('TEXT')
    
    def run_speech():
        try:
            # Chunking because command line has length limits
            chunk_size = 500
            chunks = [safe_text[i:i+chunk_size] for i in range(0, len(safe_text), chunk_size)]
            
            for chunk in chunks:
                ps_command = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SelectVoiceByHints('Male'); $s.Speak(\\\"{chunk}\\\")"
                subprocess.run(["powershell", "-Command", ps_command], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            print(f"TTS Error: {e}")

    threading.Thread(target=run_speech, daemon=True).start()
