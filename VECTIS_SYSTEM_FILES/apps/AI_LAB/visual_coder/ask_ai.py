
import sys
import os
import json

# Add VECTIS root to path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
vectis_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.append(vectis_root)

try:
    from modules.unified_llm_client import ask_llm
except ImportError:
    # Fallback if module not found
    def ask_llm(prompt):
        return f"# [Error] LLM Client not found.\n# Mock response for: {prompt}\nprint('AI Generation Failed')"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        try:
            # Request Python code specifically
            full_prompt = f"Write Python code for the following task. Return ONLY the code, no markdown backticks, no explanation. Task: {prompt}"
            response = ask_llm(full_prompt)
            # Clean up response just in case
            response = response.replace("```python", "").replace("```", "").strip()
            print(response)
        except Exception as e:
            print(f"# Error calling LLM: {str(e)}")
    else:
        print("# No prompt provided")
