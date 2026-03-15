import os
import json
import subprocess
import sys
import re

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
CONFIG_FILE = os.path.join(CONFIG_DIR, "llm_config.json")

def ensure_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        save_config("phi4", 0)

def save_config(model, keep_alive):
    data = {"ollama_model": model, "keep_alive": keep_alive}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"\n[SUCCESS] Configuration Updated:\nModel: {model}\nKeep-Alive: {keep_alive}")

def get_installed_models():
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, encoding='utf-8')
        lines = res.stdout.strip().split('\n')
        models = []
        if len(lines) > 1:
            for line in lines[1:]: # Skip header
                parts = line.split()
                if parts:
                    models.append(parts[0])
        return models
    except FileNotFoundError:
        print("[ERROR] Ollama not found in PATH.")
        return []

def get_free_memory_mb():
    # Windows specific
    try:
        cmd = "wmic OS get FreePhysicalMemory /Value"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # Output: FreePhysicalMemory=123456
        match = re.search(r"FreePhysicalMemory=(\d+)", res.stdout)
        if match:
            kb = int(match.group(1))
            return kb // 1024
        return 0
    except:
        return 0

def auto_optimize(models):
    print("\n--- 🤖 AUTO-OPTIMIZING STRATEGY ---")
    free_ram = get_free_memory_mb()
    print(f"[SENSOR] Free RAM: {free_ram} MB")
    
    selected_model = "phi4" # Default Goal
    keep_alive = 0
    
    # Strategy
    if free_ram > 12000: # 12GB+ Free
        print("[DECISION] High RAM detected. UNLEASHING MAX POWER.")
        # Try finding phi4 or largest
        candidates = [m for m in models if "phi4" in m]
        if candidates: selected_model = candidates[0]
        else: selected_model = models[0] # Fallback
        
        keep_alive = "10m" # Keep ready long time
        
    elif free_ram > 6000: # 6GB+ Free
        print("[DECISION] Medium RAM. Balanced Mode.")
        # Prefer llama3.2 (3B)
        candidates = [m for m in models if "llama3.2" in m and "1b" not in m]
        if candidates: selected_model = candidates[0]
        elif "phi4" in models: selected_model = "phi4"
        else: selected_model = models[0]
        
        keep_alive = 0 # Snapshot execution to be safe
        
    else: # Low RAM
        print("[DECISION] Low RAM. Eco/Survival Mode.")
        # Find 1B model
        candidates = [m for m in models if "1b" in m]
        if candidates: selected_model = candidates[0]
        else:
            print("[WARN] No lightweight model found. Using smallest available.")
            selected_model = models[-1] # Assuming standard list sorting? Not reliable but fallback.
            selected_model = models[0] 

        keep_alive = 0 # Unload immediately
    
    save_config(selected_model, keep_alive)

def main():
    ensure_config()
    
    print("==========================================")
    print("   🦙 VECTIS LLAMA ARCHITECT (CLI) 🦙")
    print("==========================================\n")
    
    models = get_installed_models()
    if not models:
        print("No models found.")
        sys.exit(1)

    print("Options:")
    print(" [1] MANUAL CONFIG")
    print(" [2] AUTO-OPTIMIZE (Adaptive System)")
    
    mode = input("\nSelect Mode (1-2): ")
    
    if mode == "2":
        auto_optimize(models)
        return

    # MANUAL MODE
    print(f"\nFound {len(models)} models:")
    for i, m in enumerate(models):
        print(f" [{i+1}] {m}")

    choice = input(f"\nSelect Active Model (1-{len(models)}): ")
    try:
        idx = int(choice)
        selected_model = models[idx-1]
    except:
        selected_model = models[0]

    print("\n [1] SLOW THINKING (Save RAM, Unload immediately)")
    print(" [2] FAST RESPONSE (Keep in RAM for 5 min)")
    m_choice = input("\nSelect Memory Strategy (1-2): ")
    
    keep_alive = 0
    if m_choice == "2":
        keep_alive = "5m"
        
    save_config(selected_model, keep_alive)
    
    # Install Offer
    if "llama3.2:1b" not in models:
        print("\n------------------------------------------")
        print("Suggestion: Install 'llama3.2:1b' for Eco Mode?")
        if input("(y/n): ") == 'y':
            subprocess.run(["ollama", "pull", "llama3.2:1b"])

if __name__ == "__main__":
    main()
