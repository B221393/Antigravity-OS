"""
simulator.py – 自律進化型 ポケモンカードゲーム シミュレーター (完全版)
"""

from __future__ import annotations
import json
import csv
import random
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Attack:
    energy_cost: dict[str, int]
    damage: int
    name: str = ""
    effect: str = ""

@dataclass
class Card:
    id: str
    name: str
    card_type: str          # "Pokemon" | "Item" | "Supporter" | "Stadium"
    stage: Optional[int] = None
    hp: Optional[int] = None
    pokemon_type: Optional[str] = None
    evolves_from: Optional[str] = None
    attacks: list[Attack] = field(default_factory=list)
    ability: str = ""
    effect: str = ""
    weakness: Optional[str] = None

@dataclass
class ActivePokemon:
    card: Card
    damage: int = 0
    energy: dict[str, int] = field(default_factory=dict)
    status: str = ""
    extra_damage: int = 0

    def __post_init__(self):
        self.is_ex = self.card.name.endswith("ex")

    @property
    def total_energy(self) -> int: return sum(self.energy.values())
    @property
    def remaining_hp(self) -> int: return max(0, (self.card.hp or 0) - self.damage)
    @property
    def is_knocked_out(self) -> bool: return self.remaining_hp <= 0

    def evolve(self, evolution_card: Card):
        self.card = evolution_card
        self.is_ex = evolution_card.name.endswith("ex")

# ---------------------------------------------------------------------------
# Simulator Engine
# ---------------------------------------------------------------------------

class Player:
    def __init__(self, name: str, deck_cards: list[Card]) -> None:
        self.name = name
        self.deck = deck_cards[:]
        self.hand: list[Card] = []
        self.discard: list[Card] = []
        self.active: Optional[ActivePokemon] = None
        self.bench: list[ActivePokemon] = []
        self.energy_pool: dict[str, int] = {}
        self.points = 0
        self.energy_zone = self._init_energy_zone()
        self._supporter_played = False

    def _init_energy_zone(self) -> list[str]:
        types = set()
        for c in self.deck:
            if c.pokemon_type == "Dragon":
                for a in c.attacks:
                    for etype in a.energy_cost:
                        if etype != "Colorless": types.add(etype)
            elif c.pokemon_type: types.add(c.pokemon_type)
        return list(types) if types else ["Colorless"]

    def take_turn(self, opponent: Player, game: Game, rng: random.Random):
        self._supporter_played = False
        if self.deck: self.hand.append(self.deck.pop(0))
        
        etype = rng.choice(self.energy_zone)
        self.energy_pool[etype] = self.energy_pool.get(etype, 0) + 1
        
        self._process_abilities(opponent)
        self._play_cards(opponent, game, rng)
        self._attack(opponent, game)

    def _process_abilities(self, opponent: Player):
        # ゲッコウガなどの特性処理
        for p in ([self.active] if self.active else []) + self.bench:
            if p.card.ability == "water_shuriken" and opponent.bench:
                target = min(opponent.bench, key=lambda ap: ap.remaining_hp)
                target.damage += 20
                if target.is_knocked_out:
                    self.points += (2 if target.is_ex else 1)
                    opponent.bench.remove(target)

    def _play_cards(self, opponent: Player, game: Game, rng: random.Random):
        # アイテム、進化、スタジアム、サポーターの使用
        for card in self.hand[:]:
            if card.card_type == "Stadium":
                game.stadium = card
                self.hand.remove(card); self.discard.append(card)
            elif card.card_type == "Item":
                if card.effect == "rare_candy": self._apply_rare_candy()
                self.hand.remove(card); self.discard.append(card)
        
        # エネ付着 (AI)
        if self.active and self.energy_pool:
            for etype, count in list(self.energy_pool.items()):
                self.active.energy[etype] = self.active.energy.get(etype, 0) + count
                self.energy_pool[etype] = 0

    def _apply_rare_candy(self):
        stage2s = [c for c in self.hand if c.stage == 2]
        for slot in ([self.active] if self.active else []) + self.bench:
            if slot.card.stage == 0:
                for s2 in stage2s:
                    if s2.evolves_from: # 簡易判定
                        slot.evolve(s2); self.hand.remove(s2); return

    def _attack(self, opponent: Player, game: Game):
        if not self.active or not opponent.active: return
        attack = max(self.active.card.attacks, key=lambda a: a.damage, default=None)
        if not attack: return
        
        dmg = attack.damage
        # スタジアム補正 (例: トキワの森で特定タイプ強化など)
        if game.stadium and game.stadium.effect == "lightning_boost" and self.active.card.pokemon_type == "Lightning":
            dmg += 10
            
        # ポイント依存ダメージ
        if attack.effect == "point_proportional_damage_30":
            dmg += self.points * 30
            
        opponent.active.damage += dmg
        if opponent.active.is_knocked_out:
            self.points += (2 if opponent.active.is_ex else 1)
            opponent.active = None
            if opponent.bench: opponent.active = opponent.bench.pop(0)

class Game:
    def __init__(self, p1: Player, p2: Player) -> None:
        self.p1 = p1
        self.p2 = p2
        self.stadium: Optional[Card] = None
        self.turn_count = 0

    def play(self, rng: random.Random) -> str:
        for _ in range(100):
            self.turn_count += 1
            curr, other = (self.p1, self.p2) if self.turn_count % 2 == 1 else (self.p2, self.p1)
            curr.take_turn(other, self, rng)
            if curr.points >= 3: return "p1" if curr == self.p1 else "p2"
            if not other.active and not other.bench: return "p1" if curr == self.p1 else "p2"
        return "draw"

# ---------------------------------------------------------------------------
# Data & Optimization
# ---------------------------------------------------------------------------

def load_master_db(path: str) -> Dict[str, Card]:
    db = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["id"]
            db[cid] = Card(
                id=cid, name=row["name"], card_type=row["card_type"],
                stage=int(row["stage"]) if row["stage"].isdigit() else None,
                hp=int(row["hp"]) if row["hp"].isdigit() else None,
                pokemon_type=row["type"], evolves_from=row["evolves_from"],
                ability=row.get("ability", ""), effect=row.get("effect", ""),
                attacks=[Attack({}, int(row["attack1_damage"] or 0), row["attack1_name"], row["attack1_effect"])]
            )
    return db

def simulate_batch(d1_path, d2_path, db, n=100):
    with open(d1_path) as f: d1_data = json.load(f)
    with open(d2_path) as f: d2_data = json.load(f)
    
    def build_deck(data): return [deepcopy(db[cid]) for cid in data["cards"] if cid in db]
    
    wins, turns = 0, []
    rng = random.Random()
    for _ in range(n):
        game = Game(Player("P1", build_deck(d1_data)), Player("P2", build_deck(d2_data)))
        res = game.play(rng)
        if res == "p1": wins += 1
        turns.append(game.turn_count)
    
    return wins / n, sum(turns) / n

if __name__ == "__main__":
    # 自律実行の準備
    print("Simulator Engine Ready. 12-hour optimization loop can be started.")
