
import random
import pickle

class QLearningAgent:
    """
    Q学習エージェント
    
    Q-Table: { state: [q_action0, q_action1, q_action2, q_action3] }
    """
    def __init__(self, actions, alpha=0.1, gamma=0.9):
        self.actions = actions # List of action indices [0, 1, 2, 3]
        self.alpha = alpha     # 学習率: 新しい経験をどれだけ重視するか
        self.gamma = gamma     # 割引率: 未来の報酬をどれだけ重視するか
        self.q_table = {}      # Q値テーブル (カンニングペーパー)

    def get_q_value(self, state, action):
        """Q値を取得 (未経験の状態なら0を返す)"""
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
        return self.q_table[state][action]

    def get_action(self, state, epsilon=0.1):
        """
        行動選択 (Epsilon-Greedy法)
        epsilonの確率でランダムに行動し(探索)、
        それ以外は現在のベストな行動を選ぶ(活用)。
        """
        # 未知の状態を初期化
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)

        if random.random() < epsilon:
            # 探索 (Explore): ランダムに動く
            return random.choice(self.actions)
        else:
            # 活用 (Exploit): 現在のQ値が最大のアクションを選ぶ
            current_q_values = self.q_table[state]
            max_q = max(current_q_values)
            # 最大値を持つ行動が複数ある場合はランダムに選ぶ (偏り防止)
            best_actions = [i for i, q in enumerate(current_q_values) if q == max_q]
            return random.choice(best_actions)

    def update(self, state, action, reward, next_state):
        """
        Q値の更新 (Q学習の核心)
        
        Q(s,a) <- Q(s,a) + alpha * [reward + gamma * max(Q(s',a')) - Q(s,a)]
        """
        # 未知の状態を初期化
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * len(self.actions)

        old_q = self.q_table[state][action]
        next_max_q = max(self.q_table[next_state])
        
        # TD誤差法による更新
        new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
        self.q_table[state][action] = new_q

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, filename):
        try:
            with open(filename, 'rb') as f:
                self.q_table = pickle.load(f)
            return True
        except FileNotFoundError:
            return False
