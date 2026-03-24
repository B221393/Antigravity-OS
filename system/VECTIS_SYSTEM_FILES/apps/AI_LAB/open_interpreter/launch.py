import os
import sys
import subprocess
from dotenv import load_dotenv
from colorama import Fore, init

init(autoreset=True)

# Load EGO .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.env"))
load_dotenv(env_path)

print(Fore.CYAN + "========================================")
print(Fore.CYAN + "   EGO x OPEN INTERPRETER LAUNCHER   ")
print(Fore.CYAN + "========================================")

# Detect Keys
gemini_key = os.getenv("GEMINI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

print(Fore.YELLOW + "Select Model Provider:")
print("1. Ollama (Local - Recommended for privacy)")
print("2. Gemini (Google - Fast & Smart)")
print("3. Groq (Ultra Fast)")
print("4. GPT-4 (OpenAI - Requires Key)")
print("5. Anthropic (Claude - Requires Key)")

choice = input(Fore.GREEN + "\nEnter number (1-5) [1]: ").strip()

# Updated to use interpreter script directly
interpreter_script = os.path.join(os.path.dirname(sys.executable), "interpreter")
cmd = [interpreter_script] 

if choice == "2" and gemini_key:
    # Open Interpreter supports gemini experimental
    # Assuming user has set it up or we pass generic OpenAI compat
    os.environ["GEMINI_API_KEY"] = gemini_key
    cmd.extend(["--model", "gemini-1.5-flash"]) 
    print(Fore.CYAN + "Using Gemini...")

elif choice == "3" and groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
    cmd.extend(["--model", "groq/llama3-70b-8192"])
    print(Fore.CYAN + "Using Groq...")

elif choice == "4":
    # Default OpenAI behavior
    print(Fore.CYAN + "Using OpenAI (Ensure OPENAI_API_KEY is set)...")

elif choice == "5" and anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    cmd.extend(["--model", "claude-3-opus-20240229"])
    print(Fore.CYAN + "Using Claude...")

else:
    # Default to Ollama (Local)
    print(Fore.CYAN + "Using Local LLM via Ollama...")
    # Check what models are available
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "llama3" in res.stdout:
            cmd.extend(["--model", "ollama/llama3"])
        elif "phi4" in res.stdout:
            cmd.extend(["--model", "ollama/phi4"])
        else:
            print(Fore.RED + "No standard models found. Trying generic local...")
            cmd.extend(["--local"])
    except:
        cmd.extend(["--local"]) 

# Launch
print(Fore.WHITE + f"Running command: {' '.join(cmd)}")
print("----------------------------------------")
try:
    subprocess.run(cmd, shell=True)
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"Error: {e}")
