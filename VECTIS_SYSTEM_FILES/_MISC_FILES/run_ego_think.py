import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath("apps/ego_evolution"))
from trainer import EgoSimulator

from modules.error_relay import ErrorRelay
relay = ErrorRelay("Ego_Engine")

def autonomous_think():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sim = EgoSimulator()
        print("🧠 EGO CORE: Initiating Deep Reflection on Future Updates...")
        
        context = "User requested 'Autonomous Update'. The system should evolve based on '2025_favorites' and current goals (Kodansha, TOEIC)."
        result = sim.run_deep_reflection(context)
        
        print("\n✅ EGO DECISION MATRIX:")
        print(f"   ➤ BEST MOVE: {result.get('path', ['?'])[0]}")
        print(f"   ➤ RESONANCE: {result.get('score')}")
        print(f"   ➤ THOUGHT: {result.get('thought')}")
        
        # Check for memory training
        print("\n🧠 MEMORY ANALYSIS (2025 Favorites)...")
        data_file = Path("apps/ego_evolution/data/2025_favorites.txt")
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                content = f.read()
            train_res = sim.train_from_memories(content)
            if "analysis_summary" in train_res:
                print(f"   ➤ ANALYSIS: {train_res['analysis_summary'][:100]}...")
                print(f"   ➤ ARCHETYPE SHIFT: {train_res.get('refined_archetype', 'No Change')}")
    except Exception as e:
        relay.report(e, context="Ego_Engine System Crash")
        raise e # Re-raise to ensure external caller knows it failed, after logging

if __name__ == "__main__":
    autonomous_think()
