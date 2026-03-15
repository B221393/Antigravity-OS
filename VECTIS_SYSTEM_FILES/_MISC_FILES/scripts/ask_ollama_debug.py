import os
import sys
import subprocess
import json
import argparse

ERROR_LOG_PATH = os.path.join(os.path.dirname(__file__), "../logs/ERROR_REPORT.md")

def ask_ollama(prompt, model="code-llama"):
    """
    Ollamaに質問を投げ、回答を取得する
    """
    try:
        # Check if ollama is installed
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Ollama is not installed or not found in PATH.")
        return None

    full_prompt = f"Analyze the following error log and suggest a fix:\n\n{prompt}"
    
    print(f"Thinking with {model}...")
    try:
        result = subprocess.run(
            ["ollama", "run", model, full_prompt],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.stdout
    except Exception as e:
        return f"Ollama execution failed: {e}"

def read_last_error():
    if not os.path.exists(ERROR_LOG_PATH):
        return "No error log found."
    
    with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # Get last few lines
        return "".join(lines[-10:])

def main():
    parser = argparse.ArgumentParser(description="Debug VECTIS errors using local Ollama.")
    parser.add_argument("--log", type=str, help="Specific log content to analyze")
    parser.add_argument("--model", type=str, default="gemma:2b", help="Ollama model to use (default: gemma:2b)")
    
    args = parser.parse_args()
    
    error_content = args.log if args.log else read_last_error()
    
    if not error_content or error_content.strip() == "":
        print("No error content to analyze.")
        return

    suggestion = ask_ollama(error_content, model=args.model)
    
    if suggestion:
        print("\n=== AI Suggestion ===\n")
        print(suggestion)
        print("\n=====================\n")
    else:
        print("Failed to get suggestion.")

if __name__ == "__main__":
    main()
