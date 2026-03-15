import json
import os
from usi_client import USIEngine
from vectis_brain import VectisBrain

class VectisEngine:
    """
    EGO ENGINE (NEURAL HYBRID)
    Features:
    - Persistent Opening Book (Learns from matches/analysis)
    - Neural Network Brain (Backpropagation Learning)
    - Optimized USI Parameters
    """
    def __init__(self, base_engine_path):
        self.engine = USIEngine(base_engine_path)
        self.book_path = os.path.join(os.path.dirname(__file__), "vectis_book.json")
        self.book = self._load_book()
        self.brain = VectisBrain()
        self.learning_rate = 0.1
        
    def _load_book(self):
        if os.path.exists(self.book_path):
            try:
                with open(self.book_path, 'r') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_book(self):
        with open(self.book_path, 'w') as f:
            json.dump(self.book, f, indent=2)
        self.brain.save()

    def start(self):
        if self.engine.start():
            # TUNING: MAX POWER
            self.engine.send_command("setoption name Hash value 256") 
            self.engine.send_command("setoption name Threads value 4")
            self.engine.send_command("setoption name NetworkDelay value 0")
            return True
        return False

    def get_move(self, sfen, history_moves, time_limit=1000):
        # 0. NEURAL INTUITION
        # Ask Brain what it thinks of the current flow
        win_prob = self.brain.predict(history_moves)
        # We could use this to 'resign early' or 'play risky'
        # For now, we trust the engine but maybe vary time based on confidence
        
        # 1. BOOK LOOKUP
        board_key = "startpos_" + " ".join(history_moves)
        if board_key in self.book:
            entry = self.book[board_key]
            if entry.get("score", 0) > 100: # Winning line
                return entry["move"]

        # 2. ENGINE SEARCH
        # If Brain is pessimistic (<0.3), maybe spend more time?
        alloc_time = time_limit
        if win_prob < 0.4:
            alloc_time += 500 # Think harder if losing
            
        best = self.engine.go(sfen, history_moves, time_limit=alloc_time)
        return best

    def learn_results(self, moves, result_score):
        """
        Reinforcement: Update book & Train Neural Net.
        result_score: +1 (Win), -1 (Loss), 0 (Draw)
        """
        # 1. Book Learning (Explicit Memory)
        learning_depth = min(len(moves), 30)
        for i in range(learning_depth):
            partial_moves = moves[:i]
            played_move = moves[i]
            board_key = "startpos_" + " ".join(partial_moves)
            if board_key not in self.book:
                self.book[board_key] = {"move": played_move, "score": 0, "visits": 0}
            if self.book[board_key]["move"] == played_move:
                 self.book[board_key]["visits"] += 1
                 self.book[board_key]["score"] += result_score * 10
        
        # 2. Neural Learning (Implicit Intuition / Backpropagation)
        # Train on the final state and a few intermediate states
        # Map result_score (-1, 0, 1) to (0.0, 0.5, 1.0)
        target = 0.5
        if result_score == 1: target = 1.0
        elif result_score == -1: target = 0.0
        
        # Backpropagate on the full game sequence (Outcome applies to whole game history?)
        # RL usually applies discounted reward. 
        # We will train on the LAST move, and the Middle move.
        loss = self.brain.train(moves, target)
        
        # Also train on mid-game
        if len(moves) > 10:
             self.brain.train(moves[:len(moves)//2], target)

        self.save_book()


    def stop(self):
        self.engine.stop()
