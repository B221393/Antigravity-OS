import json
import csv
import random
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

# ─────────────────────────────────────────
# CONFIGURATION v8 (INTELLIGENT PRUNER)
# ─────────────────────────────────────────
DB_PATH = "data/master_card_db.csv"
LOG_DIR = "logs/autonomous"
REPORT_PATH = "logs/autonomous/mvp_contribution_report.md"
GENERATED_DIR = "decks/generated"
GAMES_PER_MATCHUP = 50
GENERATIONS = 1000 # 1000でも十分傾向が出るため
DECK_SIZE = 20

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

@dataclass
class LCard:
    id: str; name: str; card_type: str; pokemon_type: str = "Colorless"
    hp: int = 60; stage: int = 0; evolves_from: str = ""; dmg: int = 30; is_ex: bool = False; ability: str = ""

class Slot:
    def __init__(self, card: LCard):
        self.card = card; self.damage = 0; self.energy = 0.0; self.status = ""
    @property
    def alive(self): return (self.card.hp - self.damage) > 0

class ArchPlayer:
    def __init__(self, name: str, cards: list[LCard], strategy: str = "aggro"):
        self.name = name; self.deck = cards[:]; self.hand = []; self.active = None; self.bench = []; self.points = 0; self.strategy = strategy
        self.energy_zone = list(set(c.pokemon_type for c in cards if c.pokemon_type != "Colorless" and c.card_type == "Pokemon")) or ["Colorless"]
        # [NEW v8] カードごとの貢献度蓄積用
        self.usage_stats = defaultdict(float) 

    def setup(self, rng: random.Random):
        rng.shuffle(self.deck)
        self.hand = [self.deck.pop(0) for _ in range(min(5, len(self.deck)))]
        for c in self.hand[:]:
            if c.card_type == "Pokemon" and c.stage == 0:
                self.active = Slot(c); self.hand.remove(c)
                self.usage_stats[c.id] += 1.0 # 召喚貢献
                break

    def take_turn(self, opp: "ArchPlayer", turn: int, rng: random.Random):
        if self.deck: 
            card = self.deck.pop(0)
            self.hand.append(card)
        
        # [NEW v8] 活性チェック (ベンチ召喚)
        for c in self.hand[:]:
            if c.card_type == "Pokemon" and c.stage == 0 and len(self.bench) < 3:
                self.bench.append(Slot(c)); self.hand.remove(c)
                self.usage_stats[c.id] += 0.5 # ベンチ待機貢献

        if self.active:
            etype = rng.choice(self.energy_zone)
            if etype == "Darkness" and "ダークライex" in self.active.card.name:
                if opp.active: 
                    opp.active.damage += 20
                    self.usage_stats[self.active.card.id] += 2.0 # 特性ダメージ貢献
            self.active.energy += 1.0
            if "ギラティナex" in self.active.card.name: self.active.energy += 0.5

        if not self.active or not opp.active: return
        
        if self.active.energy >= 2.5:
            opp.active.damage += self.active.card.dmg
            self.usage_stats[self.active.card.id] += (self.active.card.dmg / 10.0) # ダメージ量比例

        if not opp.active.alive:
            self.usage_stats[self.active.card.id] += 10.0 # KO(トドメ)貢献
            self.points += 2 if opp.active.card.is_ex else 1
            opp.active = None
            if opp.bench: opp.active = opp.bench.pop(0)

# ── SIMULATION CORE ──
def play_match(d1_data, d2_data, all_cards, games=50):
    def build(data): return ArchPlayer(data["name"], [all_cards[cid] for cid in data["deck_composition"] if cid in all_cards], data.get("strategy", "aggro"))
    p1_wins = 0; rng = random.Random()
    total_stats_d1 = defaultdict(float)
    
    for i in range(games):
        c1 = build(d1_data); c2 = build(d2_data)
        c1.setup(rng); c2.setup(rng)
        t = 0
        while t < 40 and c1.points < 3 and c2.points < 3:
            t += 1; curr, other = (c1, c2) if t % 2 else (c2, c1)
            curr.take_turn(other, t, rng)
        
        if c1.points >= 3: p1_wins += 1
        for cid, score in c1.usage_stats.items(): total_stats_d1[cid] += score
            
    return p1_wins / games, total_stats_d1

def autonomous_loop():
    from deck_archetypes import ARCHETYPES
    db = {}; raw_cards = []
    with open(DB_PATH, encoding='utf-8') as f:
        for r in csv.reader(f):
            if len(r)<5: continue
            c = LCard(id=r[0], name=r[1], card_type=r[2], pokemon_type=r[3], hp=int(r[4]) if r[4].isdigit() else 60, stage=int(r[5]) if r[5].isdigit() else 0, dmg=int(r[10]) if len(r)>10 and r[10].isdigit() else 30, is_ex="ex" in r[1].lower())
            db[c.id] = c; raw_cards.append(c)

    champions = {}
    for name, cfg in ARCHETYPES.items():
        # 初期はランダムな適正タイプの詰め合わせ
        deck = random.sample([c for c in raw_cards if c.pokemon_type in cfg["core_types"] or c.card_type=="Trainer"], 20)
        champions[name] = {"name": name, "deck_composition": [c.id for c in deck], "wr": 0.5, "stats": defaultdict(float)}

    print(f"=== Autonomous PRUNER Evolution START ({GENERATIONS} gens) ===")
    
    for gen in range(1, GENERATIONS + 1):
        p1_n = random.choice(list(champions.keys()))
        p2_n = random.choice(list(champions.keys()))
        wr, stats = play_match(champions[p1_n], champions[p2_n], db, GAMES_PER_MATCHUP)
        
        # [NEW v8] インテリジェント突然変異
        # 1. 貢献統計の累積
        for cid, s in stats.items(): champions[p1_n]["stats"][cid] += s
        
        # 2. 「使わない/貢献しないカード」の置換
        # 数世代に一度、ワーストスコアのカードを削除してガチャ
        if gen % 5 == 0:
            deck_ids = champions[p1_n]["deck_composition"]
            # スコアの低い順にソート (未登場は0点)
            scores = {cid: champions[p1_n]["stats"].get(cid, 0) for cid in deck_ids}
            worst_cid = min(scores, key=scores.get)
            
            # 置換
            new_card = random.choice(raw_cards)
            deck_ids[deck_ids.index(worst_cid)] = new_card.id
            champions[p1_n]["stats"][worst_cid] = 0 # リセット

        if gen % 100 == 0:
            print(f"[Gen {gen}] Pruning in progress... Best WR candidates developing.")

    # MVPレポート
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# MVP & Card Contribution Report v8\n")
        sorted_champs = sorted(champions.items(), key=lambda x: -x[1]["wr"])
        for r, (n, info) in enumerate(sorted_champs[:10], 1):
            f.write(f"## Rank #{r}: {n}\n")
            # デッキ内の貢献度ランキング
            deck_mvps = sorted(info["stats"].items(), key=lambda x: -x[1])[:5]
            f.write("| MVP Rank | Card Name | Score |\n|---|---|---|\n")
            for mr, (cid, score) in enumerate(deck_mvps, 1):
                f.write(f"| #{mr} | {db[cid].name} | {score:.1f} |\n")
            f.write("\n")

    print(f"\n=== Autonomous Evolution COMPLETE ===")
    print(f"Checkout MVP insights in: {REPORT_PATH}")

if __name__ == "__main__":
    autonomous_loop()
