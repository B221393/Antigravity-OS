import json
import random
import csv
from copy import deepcopy
from pathlib import Path
from simulator import Player, Game, load_deck_from_json, simulate

# 1. 軸（Core）の定義
CORE_IDS = ["610", "610", "611", "611", "612", "612", "741", "741"] # 8枚固定

# 2. 変動枠の候補（Pool）
POOL_IDS = [
    "1001", # アイリス (Point Boost)
    "1003", # 博士の研究 (Draw 3)
    "1004", # サカキ (Damage Boost)
    "1005", # ナツメ (Switch Opponent)
    "2001", # モンスターボール (Search Basic)
    "2002", # ふしぎなアメ (Rare Candy)
    "2003", # スピーダー (Switch)
    "2005"  # レッドカード (Disruption)
]

def run_optimization():
    target_opponent = "decks/pikachu_deck.json" # Tier-1を仮想敵にする
    results = []
    
    # 試行回数: 軸をベースに、サポートの比率を少しずつ変えた30パターン程度をテスト
    # 今回は「1枚刺し」の有効性も検証するため、ランダムサンプリングで最適解を探る
    print("--- デッキ黄金比の自動探索開始 ---")
    
    for i in range(50): # 50通りの微修正パターン
        # 変動枠12枚をプールから選ぶ
        flexible_slots = []
        # 必須級を最低枚数確保
        flexible_slots += ["1003", "1003"] # 博士は2枚必須
        flexible_slots += ["2002", "2002"] # アメは2枚必須
        
        # 残り8枚をランダムまたは重み付けで選択
        remaining_pool = POOL_IDS * 4 # 重複許可
        random.shuffle(remaining_pool)
        flexible_slots += remaining_pool[:8]
        
        deck_ids = CORE_IDS + flexible_slots
        temp_deck_path = f"decks/temp_opt_{i}.json"
        
        with open(temp_deck_path, "w", encoding="utf-8") as f:
            json.dump({"name": f"Pattern_{i}", "cards": deck_ids}, f)
        
        # 100試合で評価
        res = simulate(temp_deck_path, target_opponent, n=100)
        
        results.append({
            "pattern": i,
            "win_rate": res.deck1_win_rate,
            "accident_rate": res.deck1_accident_rate,
            "deck_ids": ",".join(deck_ids)
        })
        
        if i % 10 == 0:
            print(f"Progress: {i}/50 patterns tested...")

    # 勝率順にソート
    sorted_res = sorted(results, key=lambda x: x["win_rate"], reverse=True)
    
    # 結果をCSVに保存
    with open("data/optimization_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pattern", "win_rate", "accident_rate", "deck_ids"])
        writer.writeheader()
        writer.writerows(sorted_res)

    best = sorted_res[0]
    print(f"\n--- 探索完了! 最強の黄金比を発見 ---")
    print(f"Pattern {best['pattern']} - 勝率: {best['win_rate']:.1%}")
    print(f"構成: {best['deck_ids']}")
    
    # 最強デッキを正式保存
    best_ids = best['deck_ids'].split(",")
    with open("decks/ultimate_haxorus_deck.json", "w", encoding="utf-8") as f:
        json.dump({"name": "究極オノノクス・アイリス", "cards": best_ids}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_optimization()
