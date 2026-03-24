import sys
import os
import time

# Add system path to find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

try:
    from modules.voice_output import speak
except ImportError:
    # Fallback if run from wrong dir
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "VECTIS_SYSTEM_FILES")))
    from modules.voice_output import speak

print(">> VECTIS AUDIO & LOGIC TEST")
print(">> Emulating YouTube Summary + Decompression + Voice...")

speak("VECTIS System Check. Launching YouTube Compression Protocol.")
time.sleep(4)

# Sample Data (Mocking the result of Summarize)
compressed = """
[CORE STRUCTURE]
1. AI Agentic workflows effectively surpass zero-shot prompting.
2. VECTIS system employs 'information packaging' to optimize cognition.
3. The 'Human-in-the-loop' architecture ensures context retention.
"""

print(f"\n[Compressed View]\n{compressed}")
speak("Reading Compressed Data.")
time.sleep(2)
speak(compressed)

# Simulating User Click "Extract"
print("\n>> User clicked [EXTRACT]")
speak("Decompressing Logic Flow.")
time.sleep(2)

decompressed = """
[LOGIC FLOW]
1. ISSUE: Traditional LLM usage is limited by context window and lack of persistence.
2. SOLUTION: Implementing a local file-based OS (VECTIS) allows for infinite memory and recurring workflows.
3. CONCLUSION: The ultimate compression is not summarizing text, but crystallizing 'Insights' that trigger user action.

[INSIGHT CRYSTALS]
- 💎 Viewpoint: Code is not just syntax, it is the user's external brain.
- 🚀 Action: Use the 'Decompress' button to retrieve lost context only when necessary.
"""

print(f"\n[Decompressed View]\n{decompressed}")
speak("Reading Decompressed Detail.")
time.sleep(2)
speak(decompressed)

print("\n>> TEST COMPLETE")
speak("Test Complete. Ready for deployment.")
