
import sys
import time
import os

# パス設定 (モジュール読み込みのため)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from envs.maze_env import MazeEnv
from agents.q_agent import QLearningAgent

def print_policy(env, agent):
    """学習結果(ポリシー)を矢印で表示"""
    print("\n=== ✨ 学習された「最強のカンニングペーパー」 (Policy) ===")
    print("↑↓←→: 推奨ルート,  .: 未探索/中立,  H: 穴,  G: ゴール")
    print("-" * (env.size * 4 + 1))
    
    actions_symbols = ['↑', '↓', '←', '→']
    
    for r in range(env.size):
        line = "|"
        for c in range(env.size):
            state = (r, c)
            cell = " "
            if state == env.goal_pos:
                cell = "G"
            elif state in env.holes:
                cell = "H"
            else:
                # そのマスのベストアクションを取得
                if state in agent.q_table:
                    qs = agent.q_table[state]
                    max_q = max(qs)
                    # Q値がすべて0（未学習）ならドット表示
                    if max_q == 0 and min(qs) == 0:
                        cell = "."
                    else:
                        best_action = qs.index(max_q)
                        cell = actions_symbols[best_action]
                else:
                    cell = "."
            line += f" {cell} |"
        print(line)
        print("-" * (env.size * 4 + 1))

def main():
    env = MazeEnv(size=4)
    # Action: 0=Up, 1=Down, 2=Left, 3=Right
    agent = QLearningAgent(actions=[0, 1, 2, 3], alpha=0.1, gamma=0.9)
    
    episodes = 2000
    
    print(f"🚀 Q学習を開始します (Total Episodes: {episodes})")
    print("最初の数回はランダムに動き、徐々に賢くなります...")
    time.sleep(2)

    for episode in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0
        
        # 学習が進むにつれて探索(ランダム)を減らす
        # 最初は epsilon=1.0 (100%ランダム) -> 最後は 0.01 (ほぼ最適行動)
        epsilon = max(0.01, 1.0 - (episode / (episodes * 0.8)))
        
        while not done:
            # 1. 行動を決める
            action = agent.get_action(state, epsilon)
            
            # 2. 行動して結果を見る
            next_state, reward, done = env.step(action)
            
            # 3. 学ぶ (Qテーブルを更新)
            agent.update(state, action, reward, next_state)
            
            state = next_state
            total_reward += reward
            
        # ログ出力 (100回に1回)
        if (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{episodes} | Epsilon: {epsilon:.2f} | Total Reward: {total_reward:.2f}")

    print("\n✅ 学習完了！")
    print_policy(env, agent)

    # 最終テスト (学習成果の確認)
    print("\n🤖 === 最終テスト: 完成したAIのエキシビションマッチ ===")
    state = env.reset()
    done = False
    env.render()
    steps = 0
    
    while not done and steps < 20: # 無限ループ防止
        time.sleep(0.5)
        # 完全に学習結果だけに従う (epsilon=0)
        action = agent.get_action(state, epsilon=0) 
        state, reward, done = env.step(action)
        env.render()
        steps += 1
        
        if state == env.goal_pos:
            print("🎉 GOAL!! AIは最短ルートを見つけました！")
        elif state in env.holes:
            print("💀 GAME OVER... まだ学習が足りないようです。")

if __name__ == "__main__":
    main()
