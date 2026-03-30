import os
import json
import random
import google.generativeai as genai
from simulator import load_master_db, Player, Game, deepcopy
from pathlib import Path

# API設定
GEMINI_KEY = "AIzaSyCTAMkGMaVv9__N20fLPHPJRhwYp_2esB4" # .envから取得
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 設定
DB_PATH = "data/master_card_db.csv"
BASE_DECK_PATH = "decks/meta/ultimate_haxorus_deck.json"
OPPONENT_DECK_PATH = "decks/lightning_rush_deck.json"
TRIAL_ITERATIONS = 3
GAMES_PER_TRIAL = 100

def ask_ai_about_deck(deck_name, cards, win_rate, opponent_info):
    card_names = [c.name for c in cards]
    prompt = f"""
    【重要: ポケモンカードゲーム POCKET (ポケポケ) のルール】
    ・デッキは「20枚」固定です。
    ・「エネルギーカード」はデッキに入れず、エネルギーゾーンから毎番1個生成されます。
    ・サイドカードはなく、「3ポイント」先取で勝利です（exをたおすと2点）。
    ・ベンチは最大「3枠」です。
    
    上記スマホアプリ版ポケポケのルールに基づき、以下のデッキ診断をお願いします。
    
    【対象デッキ: {deck_name}】
    カード構成: {', '.join(card_names)}
    
    【対戦相手】
    {opponent_info}
    
    【シミュレーション結果】
    勝率: {win_rate:.1%}
    
    分析内容:
    1. このデッキの強みと弱点を100文字程度で。
    2. ポケポケのルール（20枚制限）を考慮した「1枚の差し替え案」を具体的に。
    (※エネルギーカードを追加するような、標準レギュレーションの提案は不要です)
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis Error: {e}"

def run_trial():
    print("--- Starting AI-Guided Trial Optimization ---")
    db = load_master_db(DB_PATH)
    all_cids = list(db.keys())
    
    with open(BASE_DECK_PATH) as f: current_best_data = json.load(f)
    with open(OPPONENT_DECK_PATH) as f: opp_data = json.load(f)
    
    def get_deck_objs(cids): return [deepcopy(db[cid]) for cid in cids if cid in db]
    
    for i in range(TRIAL_ITERATIONS):
        print(f"\nTrial {i+1}/{TRIAL_ITERATIONS}: Testing new mutation...")
        
        # 1枚差し替え
        test_cids = current_best_data["cards"][:]
        idx = random.randrange(len(test_cids))
        new_cid = random.choice(all_cids)
        old_name = db[test_cids[idx]].name
        test_cids[idx] = new_cid
        new_name = db[new_cid].name
        
        # シミュレーション
        wins = 0
        rng = random.Random()
        for _ in range(GAMES_PER_TRIAL):
            p1 = Player("Trial", get_deck_objs(test_cids))
            p2 = Player("Rival", get_deck_objs(opp_data["cards"]))
            # 設定（エネルギーゾーン等）を反映
            game = Game(p1, p2, deck1_cfg=current_best_data, deck2_cfg=opp_data)
            if game.play(rng) == "p1": wins += 1
            
        win_rate = wins / GAMES_PER_TRIAL
        print(f"  Result: {old_name} -> {new_name} | Win Rate: {win_rate:.1%}")
        
        # AI分析
        analysis = ask_ai_about_deck("オノノクス改良案", get_deck_objs(test_cids), win_rate, "雷速攻")
        print(f"  [Gemini Analysis]:\n{analysis}")

if __name__ == "__main__":
    run_trial()
