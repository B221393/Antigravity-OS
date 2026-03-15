
import random
import os

class MazeEnv:
    """
    Q学習用の迷路環境 (GridWorld)
    
    State: (row, col) のタプル
    Action: 0=Up, 1=Down, 2=Left, 3=Right
    Reward: Goal=+1, Hole=-1, Step=-0.01 (最短経路を促すため)
    """
    def __init__(self, size=4):
        self.size = size
        self.grid = [['.' for _ in range(size)] for _ in range(size)]
        self.start_pos = (0, 0)
        self.agent_pos = self.start_pos
        self.goal_pos = (size-1, size-1)
        
        # 穴(Hole)の配置 (固定配置で学習の収束を確認しやすくする)
        # 4x4の場合の配置例:
        # S . . .
        # . H . H
        # . . . H
        # H . . G
        self.holes = set()
        if size == 4:
            self.holes = {(1, 1), (1, 3), (2, 3), (3, 0)}
        else:
            # ランダム生成 (サイズが違う場合)
            for _ in range(size):
                r, c = random.randint(0, size-1), random.randint(0, size-1)
                if (r, c) != self.start_pos and (r, c) != self.goal_pos:
                    self.holes.add((r, c))

    def reset(self):
        """エージェントをスタート地点に戻す"""
        self.agent_pos = self.start_pos
        return self.agent_pos

    def step(self, action):
        """
        行動を実行し、次の状態、報酬、終了フラグを返す
        Returns: next_state, reward, done
        """
        row, col = self.agent_pos
        
        # 行動による移動
        if action == 0:   # Up
            row = max(0, row - 1)
        elif action == 1: # Down
            row = min(self.size - 1, row + 1)
        elif action == 2: # Left
            col = max(0, col - 1)
        elif action == 3: # Right
            col = min(self.size - 1, col + 1)
        
        next_state = (row, col)
        self.agent_pos = next_state
        
        # 判定
        if next_state == self.goal_pos:
            return next_state, 1.0, True  # Goal!
        elif next_state in self.holes:
            return next_state, -1.0, True # Death
        else:
            return next_state, -0.01, False # Step cost

    def render(self):
        """コンソールに迷路を表示 (エージェントの位置は 'A')"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("-" * (self.size * 4 + 1))
        for r in range(self.size):
            line = "|"
            for c in range(self.size):
                cell = " "
                if (r, c) == self.agent_pos:
                    cell = "A"
                elif (r, c) == self.start_pos:
                    cell = "S"
                elif (r, c) == self.goal_pos:
                    cell = "G"
                elif (r, c) in self.holes:
                    cell = "H"
                line += f" {cell} |"
            print(line)
            print("-" * (self.size * 4 + 1))
