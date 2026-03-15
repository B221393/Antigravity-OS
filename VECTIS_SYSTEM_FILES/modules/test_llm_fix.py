
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.unified_llm import UnifiedLLM

def test_fallback():
    print("--- Testing UnifiedLLM Fallback Logic ---")
    # Initialize with 'ollama' and a model name that Gemini definitely doesn't support ('gemma:2b')
    llm = UnifiedLLM(provider="ollama", model_name="gemma:2b")
    
    prompt = "Hello, reply with 'Gemini Fallback Successful' if you can read this."
    
    try:
        # This should try Ollama -> Cohere -> Gemini
        # Since Ollama is likely down/unavailable, and Cohere might 429, Gemini is the target.
        # Before fix: Gemini would 404 because it tried to use 'gemma:2b'
        # With fix: Gemini should use 'gemini-1.5-flash'
        res = llm.generate(prompt)
        print(f"Result: {res}")
        if "Fallback Successful" in res or len(res) > 0:
            print("SUCCESS: Generated content.")
        else:
            print("FAILURE: No content.")
            
    except Exception as e:
        print(f"CRITICAL FAIL: {e}")

if __name__ == "__main__":
    test_fallback()
