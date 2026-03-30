"""
autonomous_loop.py - 完全自律型デッキ進化・最強探索ループ
生成された200種以上の軸ベースからデッキを自動構築し、個別のJSONとして進化の系譜を保存する。
"""

import json
import csv
import random
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from card_traits import is_status_immune, get_damage_reduction, COIN_FLIP_ATTACKS
from deck_archetypes import ARCHETYPES

DB_PATH = "data/master_card_db.csv"
LOG_DIR = "logs/autonomous"
REPORT_PATH = "logs/autonomous/champion_report.md"
GENERATED_DIR = "decks/generated"
GAMES_PER_MATCHUP = 20
GENERATIONS = 300
DECK_SIZE = 20

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 軽量データ構造
# ─────────────────────────────────────────

@dataclass
class LCard:
    id: str
    name: str
    card_type: str
    pokemon_type: str = "Colorless"
    hp: int = 60
    stage: int = 0
    evolves_from: str = ""
    dmg: int = 30

    @property
    def is_ex(self): return "ex" in self.name.lower()
    @property
    def is_mega(self): return "メガ" in self.name
    @property
    def is_basic(self): return self.stage == 0 or self.is_mega

    def calc_dmg(self, target: "Slot", attacker_is_ex: bool) -> int:
        base = self.dmg
        WEAKNESS = {
            "Fire": "Water", "Water": "Lightning", "Grass": "Fire",
            "Lightning": "Fighting", "Fighting": "Psychic", "Psychic": "Darkness",
            "Darkness": "Metal", "Metal": "Fire"
        }
        if target.card.pokemon_type == WEAKNESS.get(self.pokemon_type):
            base += 20
        reduction = get_damage_reduction(target.card.name, attacker_is_ex)
        base = max(0, base - reduction)
        if self.name in COIN_FLIP_ATTACKS:
            base = int(base * 0.7)
        return base

@dataclass
class Slot:
    card: LCard
    damage: int = 0
    energy: int = 0
    status: str = ""
    status_immune: bool = False

    def __post_init__(self):
        self.status_immune = is_status_immune(self.card.name, self.card.id)

    @property
    def remaining(self): return max(0, self.card.hp - self.damage)
    @property
    def alive(self): return self.remaining > 0

    def apply_status_damage(self):
        if self.status == "poison" and not self.status_immune:
            self.damage += 10
        if self.status == "paralysis":
            self.status = ""

# ─────────────────────────────────────────
# プレイヤーAI
# ─────────────────────────────────────────

class ArchPlayer:
    def __init__(self, name: str, cards: list[LCard], strategy: str = "aggro"):
        self.name = name
        self.deck = cards[:]
        self.hand: list[LCard] = []
        self.active: Optional[Slot] = None
        self.bench: list[Slot] = []
        self.points = 0
        self.strategy = strategy
        self.energy_zone = list(set(
            c.pokemon_type for c in cards
            if c.pokemon_type and c.pokemon_type != "Colorless" and c.card_type == "Pokemon"
        )) or ["Colorless"]

    def setup(self, rng: random.Random):
        retries = 0
        while not self.active:
            retries += 1
            if retries > 30: break
            rng.shuffle(self.deck)
            self.hand = [self.deck.pop(0) for _ in range(min(5, len(self.deck)))]
            for c in self.hand[:]:
                if c.card_type == "Pokemon" and c.is_basic:
                    self.active = Slot(c)
                    self.hand.remove(c)
                    break

    def take_turn(self, opp: "ArchPlayer", turn: int, rng: random.Random):
        if self.active:
            self.active.apply_status_damage()
            if self.active.status == "paralysis":
                return

        if self.deck:
            self.hand.append(self.deck.pop(0))

        for c in self.hand[:]:
            if c.card_type == "Pokemon" and c.is_basic and len(self.bench) < 3:
                self.bench.append(Slot(c))
                self.hand.remove(c)

        if self.active:
            self.active.energy += 1

        if not self.active or not opp.active:
            return
        
        att = self.active.card
        dmg = att.calc_dmg(opp.active, att.is_ex)

        if self.strategy == "control" and not opp.active.status_immune:
            opp.active.status = "poison"

        if self.strategy == "snipe" and opp.bench:
            dying = [b for b in opp.bench if b.remaining <= 30]
            if dying:
                target = dying[0]
                snipe_dmg = max(20, dmg // 2)
                target.damage += snipe_dmg
                if not target.alive:
                    self.points += 2 if target.card.is_ex else 1
                    opp.bench.remove(target)
                return

        opp.active.damage += dmg
        if not opp.active.alive:
            self.points += 2 if opp.active.card.is_ex else 1
            opp.active = None
            if opp.bench:
                if self.strategy == "snipe":
                    opp.active = min(opp.bench, key=lambda s: s.remaining)
                else:
                    opp.active = opp.bench.pop(0)
                if opp.active in opp.bench:
                    opp.bench.remove(opp.active)

# ─────────────────────────────────────────
# ゲームエンジン
# ─────────────────────────────────────────

def run_game(p1: ArchPlayer, p2: ArchPlayer, rng: random.Random) -> str:
    p1.setup(rng)
    p2.setup(rng)
    if not p1.active or not p2.active:
        return "draw"

    for turn in range(50):
        curr, opp = (p1, p2) if turn % 2 == 0 else (p2, p1)
        curr.take_turn(opp, turn, rng)
        if curr.points >= 3:
            return "p1" if curr == p1 else "p2"
        if not opp.active and not opp.bench:
            return "p1" if curr == p1 else "p2"
    return "draw"

# ─────────────────────────────────────────
# デッキ・ファイル管理
# ─────────────────────────────────────────

def save_generated_deck(arch_name: str, info: dict):
    # ファイル名に使用できない文字を置換
    safe_name = arch_name.replace("/", "_").replace("\\", "_")
    filepath = os.path.join(GENERATED_DIR, f"{safe_name}.json")
    
    deck_list = [c.name for c in sorted(info["deck"], key=lambda x: (x.card_type, x.pokemon_type, x.name))]
    data = {
        "name": arch_name,
        "strategy": info["strategy"],
        "win_rate": info.get("wr", 0.0),
        "wins": info.get("wins", 0),
        "total_games": info.get("total", 0),
        "deck_composition": deck_list,
        "mutation_history": info.get("history", [])
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_archetype_deck(arch_name: str, arch_cfg: dict, all_cards: list[LCard], rng: random.Random) -> list[LCard]:
    card_by_name: dict[str, list[LCard]] = {}
    for c in all_cards:
        card_by_name.setdefault(c.name, []).append(c)

    deck: list[LCard] = []
    
    # ① 軸ex（2枚保証）
    for a_ex in arch_cfg.get("axis_ex", []):
        matches = [c for name, cards in card_by_name.items() if a_ex in name for c in cards]
        if matches:
            chosen = rng.choice(matches)
            deck.append(chosen)
            deck.append(chosen)
            
    # ② サブex（ピン刺し or 2枚）
    for s_ex in arch_cfg.get("sub_ex", []):
        matches = [c for name, cards in card_by_name.items() if s_ex in name for c in cards]
        if matches:
            chosen = rng.choice(matches)
            deck.append(chosen)
            # 安定感を出すためピン刺し（1枚）をデフォルト、goods_heavyでなければ2枚
            if not arch_cfg.get("goods_heavy", False):
                deck.append(chosen)

    # ③ キーグッズ
    # フレイムパッチなどのシナジーアイテムを1〜2枚確保
    for g_name in arch_cfg.get("key_goods", []):
        matches = [c for name, cards in card_by_name.items() if g_name in name for c in cards]
        if matches:
            chosen = rng.choice(matches)
            deck.append(chosen)
            if arch_cfg.get("goods_heavy", False): 
                deck.append(chosen) # グッズ偏重なら2枚

    # ④ 残り（タイプ合致のポケモン + グッズ）
    target_types = set(arch_cfg["core_types"])
    typed_pokemon = [c for c in all_cards if c.card_type == "Pokemon" and c.pokemon_type in target_types]
    basics = [c for c in typed_pokemon if c.is_basic]
    evos = [c for c in typed_pokemon if c.stage > 0]
    trainers = [c for c in all_cards if c.card_type in ("Trainer", "Supporter", "Item", "Stadium")]

    # 最低限のたねの確保
    while len([c for c in deck if c.card_type == "Pokemon" and c.is_basic]) < 4:
        if basics:
            deck.append(rng.choice(basics))
        else:
            break

    # 進化ポケの補充
    for _ in range(rng.randint(1, 4)):
        if evos and len(deck) < 20:
            deck.append(rng.choice(evos))

    # 枠埋め
    while len(deck) < DECK_SIZE:
        # グッズ偏重ならトレーナーズのプールを優先、そうでないならバランス
        pool = trainers if (arch_cfg.get("goods_heavy", False) or len(deck) >= 12) else basics
        if not pool: pool = all_cards
        deck.append(rng.choice(pool))

    return deck[:DECK_SIZE]

# ─────────────────────────────────────────
# 自律ループ本体
# ─────────────────────────────────────────

def autonomous_loop():
    all_cards: list[LCard] = []
    with open(DB_PATH, encoding="utf-8-sig") as f:
        for r in csv.reader(f):
            if len(r) < 5: continue
            try:
                dmg = 80 if "ex" in r[1].lower() else (120 if "メガ" in r[1] else 30)
                all_cards.append(LCard(id=r[0], name=r[1], card_type=r[2],
                                      pokemon_type=r[3], hp=int(r[4]) if r[4].isdigit() else 60,
                                      stage=int(r[5]) if r[5].isdigit() else 0,
                                      evolves_from=r[6] if len(r) > 6 else "", dmg=dmg))
            except: continue
    print(f"[Loaded] {len(all_cards)} cards")

    rng = random.Random()
    champions: dict[str, dict] = {}
    
    # 初期化
    for arch_name, arch_cfg in ARCHETYPES.items():
        deck = build_archetype_deck(arch_name, arch_cfg, all_cards, rng)
        champions[arch_name] = {
            "deck": deck,
            "wr": 0.0,
            "wins": 0,
            "total": 0,
            "strategy": arch_cfg["strategy"],
            "history": [{"gen": 0, "diff": "Initial construction"}]
        }
        # 初期状態を保存
        save_generated_deck(arch_name, champions[arch_name])
    
    print(f"[Init] {len(champions)} archetypes generated.")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gen_log = open(f"{LOG_DIR}/gen_log_{timestamp}.csv", "w", encoding="utf-8")
    gen_log.write("gen,arch,wr,mutation\n")

    print(f"\n=== Autonomous Kodoku Evolution ({GENERATIONS} gens) ===\n")

    for gen in range(1, GENERATIONS + 1):
        arch_names = list(champions.keys())
        # 高速化のため、対象をランダムに50デッキ抽出してマッチメイク
        active_matchups = rng.sample(arch_names, min(50, len(arch_names)))
        
        # 蠱毒（抽出した50デッキ間）
        for i, a1_name in enumerate(active_matchups):
            for j, a2_name in enumerate(active_matchups):
                if i >= j: continue
                a1 = champions[a1_name]
                a2 = champions[a2_name]
                for _ in range(GAMES_PER_MATCHUP):
                    p1 = ArchPlayer(a1_name, [LCard(**vars(c)) for c in a1["deck"]], a1["strategy"])
                    p2 = ArchPlayer(a2_name, [LCard(**vars(c)) for c in a2["deck"]], a2["strategy"])
                    res = run_game(p1, p2, rng)
                    a1["total"] += 1
                    a2["total"] += 1
                    if res == "p1": a1["wins"] += 1
                    elif res == "p2": a2["wins"] += 1

        # 通算勝率(Running WR)の更新と突然変異
        for arch_name in active_matchups:
            champ = champions[arch_name]
            # 通算勝率（現実的な数字に収束する）
            champ["wr"] = champ["wins"] / champ["total"] if champ["total"] > 0 else 0
            
            # 変異生成 (微小変化: 1枚入れ替え)
            old_deck = champ["deck"][:]
            new_deck = old_deck[:]
            idx = rng.randrange(len(new_deck))
            removed_card = new_deck.pop(idx)
            
            core_types = ARCHETYPES[arch_name]["core_types"]
            valid_pool = [c for c in all_cards if (c.pokemon_type in core_types) or (c.card_type != "Pokemon")]
            added_card = rng.choice(valid_pool) if valid_pool else rng.choice(all_cards)
            new_deck.append(added_card)

            # --- 適者生存テスト (Mutant vs Environment) ---
            # 「たまたまの上振れ100%」を避けるため、環境デッキ10個に対する「親」と「子」の勝率の差分を見る
            test_opponents = rng.sample(arch_names, 10)
            parent_wins, mutant_wins = 0, 0
            test_games = 5

            for opp_name in test_opponents:
                opp = champions[opp_name]
                for _ in range(test_games):
                    # 親のテスト
                    p1 = ArchPlayer("Parent", [LCard(**vars(c)) for c in old_deck], champ["strategy"])
                    p2 = ArchPlayer("Opp", [LCard(**vars(c)) for c in opp["deck"]], opp["strategy"])
                    if run_game(p1, p2, rng) == "p1": parent_wins += 1
                    
                    # 子（変異）のテスト
                    m1 = ArchPlayer("Mutant", [LCard(**vars(c)) for c in new_deck], champ["strategy"])
                    m2 = ArchPlayer("Opp", [LCard(**vars(c)) for c in opp["deck"]], opp["strategy"])
                    if run_game(m1, m2, rng) == "p1": mutant_wins += 1

            mutation_info = "unchanged"
            
            # 子が親の勝数を上回った（明確に強くなった）場合のみ採用
            # かつ、親よりも＋2勝以上差をつけた場合に採用し、微小な運ブレを排除
            if mutant_wins >= parent_wins + 2:
                champ["deck"] = new_deck
                
                mutation_info = f"Out: {removed_card.name} / In: {added_card.name} (Parent: {parent_wins}/{test_games*10} -> Mutant: {mutant_wins}/{test_games*10})"
                champ["history"].append({"gen": gen, "diff": mutation_info})
                
                # 個別JSONファイルを即時更新
                save_generated_deck(arch_name, champ)
            
            gen_log.write(f"{gen},{arch_name},{champ['wr']:.4f},{mutation_info}\n")

        # 定期ランキング
        if gen % 10 == 0 or gen == 1:
            print(f"\n[Gen {gen}] === Mutation Ranking (Running WR) ===")
            sorted_champs = sorted(champions.items(), key=lambda x: -x[1]["wr"])
            for rank, (name, info) in enumerate(sorted_champs[:10], 1): # Top 10
                muts = len(info['history'])-1
                print(f"  #{rank} {name:<25} WR: {info['wr']:.2%} ({info['wins']}/{info['total']}) Mut: {muts}")

    gen_log.close()

    # 最終チャンピオンレポート
    sorted_final = sorted(champions.items(), key=lambda x: -x[1]["wr"])
    with open(REPORT_PATH, "w", encoding="utf-8") as rf:
        rf.write("# Autonomous Kodoku Champion Report\n")
        rf.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        rf.write(f"## Final Rankings\n\n")
        rf.write("| Rank | Deck Name | Strategy | Win Rate | Mutations | ex枚数 |\n")
        rf.write("|---|---|---|---|---|---|\n")
        for rank, (name, info) in enumerate(sorted_final[:30], 1): # Top 30
            ex_count = sum(1 for c in info["deck"] if c.is_ex)
            mut_count = len(info["history"]) - 1
            rf.write(f"| #{rank} | {name} | {info['strategy']} | {info['wr']:.2%} | {mut_count}回 | {ex_count}枚 |\n")

    print(f"\n=== Autonomous Evolution COMPLETE ===")
    print(f"Champion: {sorted_final[0][0]} (WR: {sorted_final[0][1]['wr']:.2%})")
    print(f"Checkout individual deck JSON logs in: {GENERATED_DIR}/")

if __name__ == "__main__":
    autonomous_loop()
