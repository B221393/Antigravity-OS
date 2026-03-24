import sys
import os
import time
import datetime
import random
from usi_client import USIEngine
from vectis_engine import VectisEngine

# CONFIG
ENGINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/水匠5(211123)/水匠5/Suisho5-AVX2.exe"))
LOG_DIR = os.path.join(os.path.dirname(__file__), "training_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def print_banner():
    print("="*60)
    print("      EGO ENGINE - LEARNING LOOP")
    print("      Target: SUISHO 5 (Static)")
    print("="*60)
    print(f"Engine: {os.path.basename(ENGINE_PATH)}")
    print(f"Time Control: 800ms per move")
    print("-" * 60)

def save_game_record(moves, winner):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{LOG_DIR}/game_{ts}_{winner}.sfen"
    content = f"startpos moves {' '.join(moves)}"
    with open(filename, "w") as f:
        f.write(content)
    print(f" [LOG] Saved: {filename}")

def main():
    print_banner()
    
    # 1. Init
    print("[INIT] Awakening EGO ENGINE (Learner)...")
    vectis = VectisEngine(ENGINE_PATH)
    if not vectis.start():
        print("[ERR] Failed EGO.")
        return

    print("[INIT] Summoning SUISHO 5 (Teacher)...")
    suisho = USIEngine(ENGINE_PATH)
    if not suisho.start():
        vectis.stop()
        return

    print("\n[READY] TRAINING STARTED.\n")
    
    scores = {"EGO": 0, "SUISHO": 0, "DRAW": 0}
    match_count = 0
    
    try:
        while True:
            match_count += 1
            print(f"=== MATCH {match_count} | SCORE: V:{scores['EGO']} - S:{scores['SUISHO']} ===")
            
            # Reset
            vectis.engine.send_command("usinewgame")
            suisho.send_command("usinewgame")
            time.sleep(1)
            
            moves = []
            vectis_is_black = (match_count % 2 != 0)
            
            black_player = vectis if vectis_is_black else suisho
            white_player = suisho if vectis_is_black else vectis
            black_name = "EGO" if vectis_is_black else "SUISHO"
            white_name = "SUISHO" if vectis_is_black else "EGO"
            
            print(f" {black_name} (B) vs {white_name} (W)")
            
            turn = 0
            winner_code = 0 # 0=Draw, 1=Vectis Win, -1=Vectis Lose
            
            while True:
                turn += 1
                is_turn_black = (turn % 2 != 0)
                
                active = black_player if is_turn_black else white_player
                name = black_name if is_turn_black else white_name
                
                # Move
                # Heuristic: EGO gets a bit more time to think if it wants
                t_lim = 800
                if active == vectis:
                     best = vectis.get_move("startpos", moves, time_limit=t_lim)
                else:
                     best = suisho.go("startpos", moves, time_limit=t_lim)
                
                # Check outcome
                if best == "resign":
                    winner = white_name if is_turn_black else black_name
                    print(f" >> RESIGN! Winner: {winner}")
                    
                    if winner == "EGO":
                        scores["EGO"] += 1
                        winner_code = 1
                    else:
                        scores["SUISHO"] += 1
                        winner_code = -1
                    
                    save_game_record(moves, winner)
                    break
                
                moves.append(best)
                print(f"{turn:03d} {name[:1]}: {best}", end=" | " if turn % 4 != 0 else "\n")
                
                if len(moves) > 200:
                    print("\n >> DRAW")
                    scores["DRAW"] += 1
                    winner_code = 0
                    save_game_record(moves, "DRAW")
                    break
            
            # LEARN
            if winner_code != 0:
                print(f" [LEARNING] Updating EGO knowledge with result: {winner_code}")
                vectis.learn_results(moves, winner_code)
            
            print("-" * 30)
            time.sleep(2)
            
    except KeyboardInterrupt:
        vectis.stop()
        suisho.stop()


if __name__ == "__main__":
    main()
