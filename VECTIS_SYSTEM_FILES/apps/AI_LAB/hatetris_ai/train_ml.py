import os
import sys
import json
import random
import time
from collections import deque
import multiprocessing as mp

# === HATETRIS ENGINE (Bitwise for speed) ===
PIECES = {
    'S': [[[0,1,1],[1,1,0],[0,0,0]], [[0,1,0],[0,1,1],[0,0,1]]],
    'Z': [[[1,1,0],[0,1,1],[0,0,0]], [[0,0,1],[0,1,1],[0,1,0]]],
    'O': [[[1,1],[1,1]]],
    'I': [[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]]],
    'L': [[[0,0,1],[1,1,1],[0,0,0]], [[0,1,0],[0,1,0],[0,1,1]], [[0,0,0],[1,1,1],[1,0,0]], [[1,1,0],[0,1,0],[0,1,0]]],
    'J': [[[1,0,0],[1,1,1],[0,0,0]], [[0,1,1],[0,1,0],[0,1,0]], [[0,0,0],[1,1,1],[0,0,1]], [[0,1,0],[0,1,0],[1,1,0]]],
    'T': [[[0,1,0],[1,1,1],[0,0,0]], [[0,1,0],[0,1,1],[0,1,0]], [[0,0,0],[1,1,1],[0,1,0]], [[0,1,0],[1,1,0],[0,1,0]]]
}
PIECE_ORDER = ['S', 'Z', 'O', 'I', 'L', 'J', 'T']

def get_spawn(pid):
    if pid == 'I': return 3, -1
    if pid == 'O': return 4, 0
    return 3, 0

def collides(board, pid, r, x, y):
    shape = PIECES[pid][r]
    for ri, row in enumerate(shape):
        for ci, val in enumerate(row):
            if val:
                by = y + ri
                bx = x + ci
                if bx < 0 or bx >= 10 or by >= 20: return True
                if by >= 0 and (board[by] & (1 << bx)): return True
    return False

def lock_piece(board, pid, r, x, y):
    new_board = list(board)
    shape = PIECES[pid][r]
    for ri, row in enumerate(shape):
        for ci, val in enumerate(row):
            if val:
                by = y + ri
                bx = x + ci
                if 0 <= by < 20:
                    new_board[by] |= (1 << bx)
    
    lines = 0
    final_board = []
    FULL_ROW = (1 << 10) - 1
    for rval in new_board:
        if rval == FULL_ROW:
            lines += 1
        else:
            final_board.append(rval)
            
    while len(final_board) < 20:
        final_board.insert(0, 0)
        
    return tuple(final_board), lines

def get_reachable(board, pid):
    xs, ys = get_spawn(pid)
    if collides(board, pid, 0, xs, ys): return []
    
    queue = deque([(0, xs, ys)])
    visited = {(0, xs, ys)}
    locks = []
    unique_boards = set()
    
    while queue:
        r, x, y = queue.popleft()
        
        # drops
        if collides(board, pid, r, x, y + 1):
            new_bd, lines = lock_piece(board, pid, r, x, y)
            if new_bd not in unique_boards:
                unique_boards.add(new_bd)
                topy = 20
                for i, rval in enumerate(new_bd):
                    if rval > 0:
                        topy = i
                        break
                locks.append({'r':r, 'x':x, 'y':y, 'board':new_bd, 'lines':lines, 'topy':topy})
        else:
            st = (r, x, y + 1)
            if st not in visited:
                visited.add(st)
                queue.append(st)
        
        # left, right, rotate
        moves = [
            (r, x - 1, y),
            (r, x + 1, y),
            ((r + 1) % len(PIECES[pid]), x, y)
        ]
        for mr, mx, my in moves:
            if not collides(board, pid, mr, mx, my):
                st = (mr, mx, my)
                if st not in visited:
                    visited.add(st)
                    queue.append(st)
                    
    return locks

def get_evil_piece(board):
    worst_pid = PIECE_ORDER[0]
    min_topy = 999
    
    for pid in PIECE_ORDER:
        locks = get_reachable(board, pid)
        if not locks: return pid, True
        player_max_topy = max(l['topy'] for l in locks)
        if player_max_topy < min_topy:
            min_topy = player_max_topy
            worst_pid = pid
    return worst_pid, False

# === AI EVALUATION ===
def evaluate(board, lines, weights):
    # weights = [agg_h, lines, holes, bumpiness, max_h, wells]
    heights = [0]*10
    holes = 0
    for c in range(10):
        found = False
        for r in range(20):
            if board[r] & (1 << c):
                if not found:
                    heights[c] = 20 - r
                    found = True
            elif found:
                holes += 1

    agg_h = sum(heights)
    bump = sum(abs(heights[c] - heights[c+1]) for c in range(9))
    max_h = max(heights)
    
    wells = 0
    for c in range(10):
        left = heights[c-1] if c > 0 else 20
        right = heights[c+1] if c < 9 else 20
        if left > heights[c] and right > heights[c]:
            wells += min(left, right) - heights[c]

    score = (
        weights[0] * agg_h +
        weights[1] * lines +
        weights[2] * holes +
        weights[3] * bump +
        weights[4] * max_h +
        weights[5] * wells
    )
    return score

def run_game(weights, max_pieces=100):
    board = tuple([0]*20)
    total_lines = 0
    piece_count = 0
    
    while piece_count < max_pieces:
        pid, over = get_evil_piece(board)
        if over: break
        
        locks = get_reachable(board, pid)
        if not locks: break
        
        best_score = -999999
        best_b = None
        
        for l in locks:
            sc = evaluate(l['board'], l['lines'], weights)
            if sc > best_score:
                best_score = sc
                best_b = l
                
        if not best_b: break
        board = best_b['board']
        total_lines += best_b['lines']
        piece_count += 1
        
    # Return survival score (Lines are prioritized, survival pieces as tiebreaker)
    return total_lines * 1000 + piece_count

def evaluate_individual(weights):
    # Hatetris is deterministic, so 1 play per individual is enough.
    score = run_game(weights, max_pieces=150)
    return score, weights

# === GENETIC ALGORITHM ===
def main():
    POP_SIZE = 16
    GENS = 500
    CPUS = max(1, mp.cpu_count() - 1)
    
    print(f"==================================================")
    print(f" Hatetris ML Engine (Genetic Algorithm) Started")
    print(f" Cores utilized: {CPUS}")
    print(f" Population: {POP_SIZE}, Generations: {GENS}")
    print(f"==================================================\n")
    
    os.makedirs('data', exist_ok=True)
    weights_path = os.path.join('data', 'best_weights.json')
    log_path = os.path.join('data', 'training.log')
    
    try:
        with open(weights_path, 'r') as f:
            best_weights = json.load(f)
            print("=> Loaded previous best weights from file.")
    except:
        # Default typical heuristics: [agg_h, lines, holes, bumpiness, max_h, wells]
        best_weights = [-0.51, 0.76, -0.36, -0.18, -0.2, -0.3]
        print("=> Starting from default heuristic weights.")
        
    pop = [best_weights]
    for _ in range(POP_SIZE - 1):
        pop.append([w + random.uniform(-0.5, 0.5) for w in best_weights])
        
    with mp.Pool(CPUS) as pool:
        for gen in range(GENS):
            t0 = time.time()
            results = pool.map(evaluate_individual, pop)
            results.sort(key=lambda x: x[0], reverse=True)
            
            best_score = results[0][0]
            best_weights = results[0][1]
            
            lines_cleared = best_score // 1000
            pieces_survived = best_score % 1000
            
            print(f"Gen {gen+1}/{GENS} | Best: {lines_cleared} Lines ({pieces_survived} pieces) | Time: {time.time()-t0:.1f}s")
            
            with open(log_path, 'a') as f:
                f.write(f"Gen {gen+1} | Lines: {lines_cleared} | Pieces: {pieces_survived} | Weights: {best_weights}\n")
            with open(weights_path, 'w') as f:
                json.dump(best_weights, f)
                
            # Create next generation
            new_pop = [best_weights]
            elite_count = POP_SIZE // 4
            
            # Keep top 25% (Elitism)
            for i in range(1, elite_count):
                new_pop.append(results[i][1])
                
            # Crossover & Mutation for the rest
            while len(new_pop) < POP_SIZE:
                parentA = random.choice(results[:elite_count])[1]
                parentB = random.choice(results[:elite_count])[1]
                child = []
                for a, b in zip(parentA, parentB):
                    gene = a if random.random() < 0.5 else b
                    if random.random() < 0.2: # 20% mutation chance
                        gene += random.uniform(-0.2, 0.2)
                    child.append(gene)
                new_pop.append(child)
                
            pop = new_pop

if __name__ == '__main__':
    main()
