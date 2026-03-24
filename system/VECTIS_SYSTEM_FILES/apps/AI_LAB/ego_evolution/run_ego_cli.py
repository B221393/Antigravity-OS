import sys
import random
import json
import os
import time
from pathlib import Path

# Add parent dir to path to import trainer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trainer import EgoSimulator

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("="*70)
    print(" 🧬 EGO EGO ENGINE - DEEP REFLECTION CLI v2.2 (FULL MEMORY)")
    print("   Identity: REVOLUTIONARY CREATOR")
    print("="*70)

def type_writer(text, speed=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def print_thinking():
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    print("\n")
    for i in range(30):
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r {frame} EGO_CORE: Consulted Identity Matrix... {i*3}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print("\r ✅ EGO_CORE: Reflection Complete.              \n")

def run_cli():
    try:
        sim = EgoSimulator()
    except Exception as e:
        print(f"Error loading Simulator: {e}")
        return

    while True:
        clear_screen()
        print_header()
        
        # Display Current Stats
        vectors = sim.model.get('ego_vectors', {})
        identity = sim.model.get('identity', {})
        
        print(f"\n[ARCHETYPE] {identity.get('archetype')}")
        print("\n[EGO VECTORS]")
        for k, v in vectors.items():
            bar_len = int(v * 20)
            bar = "▮" * bar_len + " " * (20 - bar_len)
            print(f" {k.ljust(25)}: [{bar}] {v:.2f}")

        print("\n[CONTROLS]")
        print(" 1. Deep Reflection (Consult the Core)")
        print(" 2. Quick Evaluation (Action Check)")
        print(" 3. View Narrative History")
        print(" 4. Analyze Input Data (DEEP TRAINING)")
        print(" q. Quit")
        
        choice = input("\nSelect > ").strip()
        
        if choice == '1':
            context = input("\nDescribe current situation (e.g. 'I feel stuck'): ")
            print_thinking()
            
            if hasattr(sim, 'run_deep_reflection'):
                res = sim.run_deep_reflection(context)
                
                print("-" * 60)
                print(f" >>> BEST MOVE: {res.get('path', ['Unknown'])[0].upper()}")
                print(f" >>> RESONANCE SCORE: {res.get('score', 0)}/100")
                print("-" * 60)
                print("\n[INNER MONOLOGUE]")
                type_writer(f"\"{res.get('thought', '...')}\"", speed=0.03)
                print("-" * 60)
            else:
                print("Error: Trainer module missing 'run_deep_reflection'.")
            input("\nPress Enter...")
            
        elif choice == '2':
            action = input("\nAction to evaluate (e.g. 'Watch Netflix'): ")
            print("\n")
            if hasattr(sim, 'evaluate_action_llm'):
                score, monologue = sim.evaluate_action_llm(action)
                bar_len = int(score / 5)
                bar = "█" * bar_len
                print(f" Reward: {score} [{bar}]")
                type_writer(f" Eqo: {monologue}")
            else:
                print("Error: Trainer module missing 'evaluate_action_llm'.")
            input("\nPress Enter...")
            
        elif choice == '3':
            history = sim.model.get('decision_history', [])
            print(f"\n[HISTORY] ({len(history)} records)")
            for h in history[-5:]:
                 context = h.get('context','?')
                 move = h.get('decision', {}).get('best_move', 'Unknown')
                 print(f" - {h['timestamp'][:16]}: {context} -> {move}")
            input("\nPress Enter...")

        elif choice == '4':
            # DEEP TRAINING MODE
            data_file = Path(__file__).parent / "data" / "FULL_SELF_ANALYSIS_LOG.txt"
            if not data_file.exists():
                print("No input data found at data/FULL_SELF_ANALYSIS_LOG.txt. Trying archives?")
                input("\nPress Enter...")
                continue
                
            with open(data_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            print("\n[LOADING FULL SELF-ANALYSIS LOG...]")
            lines = content.strip().split('\n')
            for line in lines[:10]:
                if line.strip():
                    print(f" Ingesting: {line[:60]}...")
                    time.sleep(0.02)
            if len(lines) > 10: print(f" ...and {len(lines)-10} more lines.")
                
            print("\n[RUNNING DEEP LEARNING ANALYSIS...]")
            print(" Using 2025 Context Window... Identifying Latent Variables...")
            
            old_vectors = sim.model.get("ego_vectors", {}).copy()
            res = sim.train_from_memories(content)
            
            if "status" in res and res["status"] == "error":
                print(f" Training Failed: {res['message']}")
            else:
                print("\n✅ TRAINING COMPLETE. EGO UPDATED.")
                print("-" * 60)
                print(f" ANALYSIS: {res.get('analysis_summary')}")
                print("-" * 60)
                print(f" NEW ARCHETYPE: {res.get('refined_archetype')}")
                print("-" * 60)
                # Show Narrative Kernel if available
                if "narrative_kernel" in res:
                     print(f" NARRATIVE KERNEL ACQUIRED: {res.get('narrative_kernel')}")
                print("\n [VECTOR SHIFTS]")
                
                new_vectors = sim.model.get("ego_vectors", {})
                all_keys = set(old_vectors.keys()) | set(new_vectors.keys())
                
                for k in all_keys:
                    old_v = old_vectors.get(k, 0.0)
                    new_v = new_vectors.get(k, 0.0)
                    diff = new_v - old_v
                    
                    if abs(diff) < 0.01: continue
                    
                    bg = " "
                    if diff > 0.05: bg = "++"
                    elif diff < -0.05: bg = "--"
                    
                    print(f" {k.ljust(25)}: {old_v:.2f} -> {new_v:.2f} ({bg} {diff:+.2f})")
            
            input("\nPress Enter to Save & Continue...")

        elif choice == 'q':
            break

if __name__ == "__main__":
    run_cli()
