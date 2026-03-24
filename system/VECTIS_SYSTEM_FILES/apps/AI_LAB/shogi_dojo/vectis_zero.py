import random
import os
from usi_client import USIEngine

class VectisZero:
    """
    EGO ZERO: A Custom Shogi AI Wrapper.
    It uses a base engine (Suisho 5) for deep calculation but adds
    a 'Vectis Strategy Layer' for openings and time management.
    """
    def __init__(self, base_engine_path):
        self.engine = USIEngine(base_engine_path)
        self.name = "EGO ZERO (Proto)"
        self.book = {
            "startpos": ["7g7f", "2g2f", "5g5f"], # Expanded Book
        }
        self.active_strategy = "AGGRESSIVE" # Aggressive, Balanced, Defensive
        self.curiosity_level = 0.3 # 30% Chance to explore

    def start(self):
        if self.engine.start():
            # Inject Custom Settings to the Base Engine
            # e.g., turn off pondering to save resources for our wrapper logic
            self.engine.send_command("setoption name Ponder value false")
            # If we were using YaneuraOu, we could set EvalHash etc.
            self.engine.send_command("setoption name Threads value 4") 
            return True
        return False

    def get_move(self, sfen, history_moves, time_limit=1000):
        # 1. Opening Book Check & Curiosity
        # If early game (< 10 moves), allow exploration
        if len(history_moves) < 10:
             if random.random() < self.curiosity_level:
                 # Curiosity: Pick a random viable move if possible, or just play standard.
                 # Since we don't have a move generator here, we modify the Opening Book behavior.
                 if not history_moves and "startpos" in self.book:
                     selected = random.choice(self.book["startpos"])
                     print(f"[EGO ZERO] Curiosity Triggered! Exploring opening: {selected}")
                     return selected

        # 2. Strategy Injection
        # We can dynamically adjust time limit based on complexity
        # For now, we trust the engine but maybe add some 'noise' or 'contempt' if we were training
        
        # 3. Delegate to Base Engine
        return self.engine.go(sfen, history_moves, time_limit)

    def stop(self):
        self.engine.stop()
