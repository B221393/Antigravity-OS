"""
simulator.py – ポケモンカードゲーム ポケポケ シミュレーター (統計対応・完全版)
"""

from __future__ import annotations

import json
import csv
import random
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Attack:
    energy_cost: dict[str, int]
    damage: int
    name: str = ""
    coin_flips: int = 0
    effect: str = ""

    @property
    def total_cost(self) -> int:
        return sum(self.energy_cost.values())


@dataclass
class Card:
    name: str
    card_type: str          # "Pokemon" | "Trainer" | "Item" | "Supporter"
    stage: Optional[int]    # 0=たね, 1=1進化, 2=2進化
    hp: Optional[int]
    pokemon_type: Optional[str]
    evolves_from: Optional[str]
    attacks: list[Attack]
    weakness: Optional[str] = None
    effect: str = ""
    ability: str = ""
    is_baby: bool = False


@dataclass
class ActivePokemon:
    card: Card
    damage: int = 0
    energy: dict[str, int] = field(default_factory=dict)
    status: str = ""
    is_ex: bool = field(init=False)
    just_switched: bool = False
    extra_damage: int = 0

    def __post_init__(self) -> None:
        self.is_ex = self.card.name.endswith("ex")
        if not self.energy:
            self.energy = {}

    @property
    def total_energy(self) -> int:
        return sum(self.energy.values())

    @property
    def remaining_hp(self) -> int:
        return max(0, (self.card.hp or 0) - self.damage)

    @property
    def is_knocked_out(self) -> bool:
        return self.remaining_hp <= 0

    @property
    def best_attack(self) -> Optional[Attack]:
        usable = self.active_attacks_available()
        return max(usable, key=lambda a: a.damage) if usable else None

    def active_attacks_available(self) -> list[Attack]:
        available = []
        for a in self.card.attacks:
            temp_energy = self.energy.copy()
            can_use = True
            for etype, count in a.energy_cost.items():
                if etype == "Colorless": continue
                if temp_energy.get(etype, 0) < count:
                    can_use = False
                    break
                temp_energy[etype] -= count
            if not can_use: continue
            if sum(temp_energy.values()) >= a.energy_cost.get("Colorless", 0):
                available.append(a)
        return available

    @property
    def strongest_attack(self) -> Optional[Attack]:
        return max(self.card.attacks, key=lambda a: a.damage) if self.card.attacks else None

    def evolve(self, evolution_card: Card) -> None:
        self.card = evolution_card
        self.is_ex = evolution_card.name.endswith("ex")


# ---------------------------------------------------------------------------
# Core Simulation Logic
# ---------------------------------------------------------------------------

def _build_card_from_info(info: dict) -> Card:
    attacks = []
    card_type = info.get("type", info.get("pokemon_type", "-"))
    
    def parse_attack(name_key, cost_key, dmg_key, effect_key):
        if not info.get(name_key): return
        dmg_str = str(info[dmg_key]).replace("+","").replace("x","").replace("×","")
        dmg = int(dmg_str) if dmg_str.isdigit() else 0
        raw_cost = info.get(cost_key, "0")
        cost_dict = {}
        if ":" in str(raw_cost):
            for part in str(raw_cost).split(","):
                t, c = part.split(":")
                cost_dict[t.strip()] = int(c)
        else:
            c = int(raw_cost) if str(raw_cost).isdigit() else 0
            if c > 0:
                ctype = card_type if card_type != "-" else "Colorless"
                cost_dict[ctype] = c
        attacks.append(Attack(name=info[name_key], energy_cost=cost_dict, damage=dmg, effect=info.get(effect_key,"")))

    parse_attack("attack1_name", "attack1_cost", "attack1_damage", "attack1_effect")
    parse_attack("attack2_name", "attack2_cost", "attack2_damage", "attack2_effect")

    if not attacks and "attacks" in info:
        for a in info["attacks"]:
            cost = a.get("energy_cost", {})
            if isinstance(cost, int): cost = {card_type if card_type != "-" else "Colorless": cost}
            attacks.append(Attack(name=a.get("name", ""), energy_cost=cost, damage=a.get("damage", 0), effect=a.get("effect", "")))

    def safe_int(v):
        if v is None: return None
        v_str = str(v).strip()
        return int(v_str) if v_str.isdigit() else None

    return Card(
        name=info["name"], card_type=info.get("card_type", "Pokemon"),
        stage=safe_int(info.get("stage")), hp=safe_int(info.get("hp")),
        pokemon_type=card_type, evolves_from=info.get("evolves_from"),
        attacks=attacks, ability=info.get("ability", ""), effect=info.get("effect", ""), is_baby=False
    )

def load_deck_from_json(path: str | Path) -> list[Card]:
    db_path = Path(__file__).parent / "data" / "master_card_db.csv"
    db = {}
    if db_path.exists():
        with open(db_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader: db[str(row["id"])] = row
    with open(path, encoding="utf-8") as f: deck_data = json.load(f)
    cards = []
    for entry in deck_data.get("cards", []):
        if isinstance(entry, (str, int)):
            if str(entry) in db: cards.append(_build_card_from_info(db[str(entry)]))
        elif isinstance(entry, dict):
            card_obj = _build_card_from_info(entry)
            for _ in range(entry.get("count", 1)): cards.append(deepcopy(card_obj))
    if len(cards) != 20: raise ValueError(f"Deck must have 20 cards. Found {len(cards)} in {path}")
    return cards


WIN_POINTS = 3
BENCH_MAX = 3
HAND_SIZE = 5
MAX_TURNS = 50

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
        self._supporter_played = False
        self.supporter_damage_boost = 0
        self.iris_active = False
        self.supporter_locked = False
        self.item_locked = False
        self.history: list[str] = []
        self.energy_zone = self._initialize_energy_zone()

    def _initialize_energy_zone(self) -> list[str]:
        types = set()
        for c in (self.deck + self.hand):
            if c.card_type != "Pokemon": continue
            if c.pokemon_type == "Dragon":
                for a in c.attacks:
                    for etype in a.energy_cost:
                        if etype != "Colorless": types.add(etype)
            elif c.pokemon_type and c.pokemon_type != "-":
                types.add(c.pokemon_type)
        return list(types) if types else ["Colorless"]

    def log(self, msg: str) -> None: self.history.append(msg)
    def shuffle_deck(self, rng: random.Random) -> None: rng.shuffle(self.deck)
    def draw(self, n: int = 1) -> None:
        drawn = self.deck[:n]
        self.deck = self.deck[n:]
        self.hand.extend(drawn)

    def setup_active(self) -> bool:
        basics = [c for c in self.hand if c.card_type == "Pokemon" and c.stage == 0]
        if not basics: return False
        chosen = basics[0]
        self.hand.remove(chosen)
        self.active = ActivePokemon(card=chosen)
        return True

    def take_turn(self, opponent: Player, rng: random.Random) -> None:
        self._supporter_played = False
        self.supporter_damage_boost = 0
        self.iris_active = False
        if self.deck: self.draw(1)
        
        etype = rng.choice(self.energy_zone)
        self.energy_pool[etype] = self.energy_pool.get(etype, 0) + 1
        
        self._use_abilities(opponent, rng)
        self._play_trainers(rng, opponent)
        self._evolve_pokemon()
        self._place_basics_to_bench()
        
        # 致死予測
        imminent_death = False
        if self.active and opponent.active:
            opp_atk = opponent.active.best_attack
            if opp_atk and opp_atk.damage >= self.active.remaining_hp: imminent_death = True
        
        self._attach_energy_smart(imminent_death)
        self._attack(opponent, rng)

    def _attach_energy_smart(self, imminent_death: bool) -> None:
        targets = []
        if self.active: targets.append(self.active)
        targets.extend(self.bench)
        for etype, count in list(self.energy_pool.items()):
            for _ in range(count):
                best_t, best_s = None, -1.0
                for t in targets:
                    s = 0.0
                    strongest = t.strongest_attack
                    if strongest:
                        if etype in strongest.energy_cost and t.energy.get(etype, 0) < strongest.energy_cost[etype]: s += 10.0
                        if t.total_energy < strongest.total_cost: s += 5.0
                    if t == self.active and imminent_death: s -= 8.0
                    if t.is_ex: s += 2.0
                    if s > best_s: best_s, best_t = s, t
                if best_t and best_s > 0:
                    best_t.energy[etype] = best_t.energy.get(etype, 0) + 1
                    self.energy_pool[etype] -= 1

    def _use_abilities(self, opponent: Player, rng: random.Random) -> None:
        all_p = ([self.active] if self.active else []) + self.bench
        for p in all_p:
            if p.card.ability == "water_shuriken" and opponent.bench:
                target = min(opponent.bench, key=lambda ap: ap.remaining_hp)
                target.damage += 20
                if target.is_knocked_out:
                    self.points += (2 if target.is_ex else 1)
                    opponent.bench.remove(target)

    def _play_trainers(self, rng: random.Random, opponent: Player) -> None:
        for card in self.hand[:]:
            if card.card_type == "Item":
                self._apply_item(card, rng, opponent)
                if card in self.hand:
                    self.hand.remove(card)
                    self.discard.append(card)
        if not self._supporter_played:
            supps = [c for c in self.hand if c.card_type == "Supporter"]
            if supps:
                chosen = supps[0] # シンプル化
                self._apply_supporter(chosen, rng, opponent)
                self.hand.remove(chosen)
                self.discard.append(chosen)
                self._supporter_played = True

    def _apply_item(self, card: Card, rng: random.Random, opponent: Player) -> None:
        if self.item_locked: return
        if card.effect == "heal_30" and self.active: self.active.damage = max(0, self.active.damage - 30)
        elif card.effect == "rare_candy": self._apply_rare_candy()
        elif card.effect == "switch" and self.bench: self._switch_pokemon()

    def _apply_rare_candy(self) -> None:
        in_play = ([self.active] if self.active else []) + self.bench
        stage2s = [c for c in self.hand if c.card_type == "Pokemon" and c.stage == 2]
        for slot in in_play:
            if slot.card.stage != 0: continue
            for s2 in stage2s:
                if s2.evolves_from: # 簡易判定
                    valid = (s2.name == "オノノクス" and slot.card.name == "キバゴ") or \
                            (s2.name == "サーナイトex" and slot.card.name == "ラルトス") or \
                            (s2.name == "リザードンex" and slot.card.name == "ヒトカゲ")
                    if valid:
                        slot.evolve(s2)
                        self.hand.remove(s2)
                        return

    def _apply_supporter(self, card: Card, rng: random.Random, opponent: Player) -> None:
        if self.supporter_locked: return
        if card.effect == "draw_3": self.draw(3)
        elif card.effect == "switch_opponent_active" and opponent.bench:
            new_active = opponent.bench.pop(0)
            if opponent.active: opponent.bench.append(opponent.active)
            opponent.active = new_active

    def _switch_pokemon(self) -> None:
        if self.bench and self.active:
            old = self.active
            self.active = self.bench.pop(0)
            self.bench.append(old)

    def _evolve_pokemon(self) -> None:
        for slot in ([self.active] if self.active else []) + self.bench:
            for card in self.hand[:]:
                if card.card_type == "Pokemon" and card.evolves_from == slot.card.name:
                    slot.evolve(card)
                    self.hand.remove(card)
                    break

    def _place_basics_to_bench(self) -> None:
        for card in self.hand[:]:
            if len(self.bench) >= BENCH_MAX: break
            if card.card_type == "Pokemon" and card.stage == 0:
                self.bench.append(ActivePokemon(card=card))
                self.hand.remove(card)

    def _attack(self, opponent: Player, rng: random.Random) -> None:
        if not self.active or not opponent.active: return
        attack = self.active.best_attack
        if not attack: return
        
        dmg = attack.damage + self.active.extra_damage + self.supporter_damage_boost
        self.active.extra_damage = 0
        self.supporter_damage_boost = 0
        
        if opponent.active.card.ability == "prevent_ex_damage" and self.active.is_ex: dmg = 0
        if opponent.active.card.weakness == self.active.card.pokemon_type: dmg += 20
        
        opponent.active.damage += dmg
        
        if attack.effect == "bench_energy_20":
            extra = (sum(b.total_energy for b in self.bench) + sum(b.total_energy for b in opponent.bench)) * 20
            opponent.active.damage += extra

        if opponent.active.is_knocked_out:
            pts = 2 if opponent.active.is_ex else 1
            self.points += pts
            opponent.active = None
            if opponent.bench: opponent.active = opponent.bench.pop(0)

class Game:
    def __init__(self, p1: Player, p2: Player, rng: random.Random) -> None:
        self.p1, self.p2, self.rng = p1, p2, rng
        self._first_player: Optional[Player] = None
    def setup(self) -> tuple[bool, bool]:
        def deal(p):
            for _ in range(100):
                p.deck.extend(p.hand); p.hand.clear(); p.shuffle_deck(self.rng); p.draw(5)
                if any(c.card_type == "Pokemon" and c.stage == 0 for c in p.hand): return True
            return False
        deal(self.p1); deal(self.p2)
        self.p1.setup_active(); self.p2.setup_active()
        return False, False
    def play(self) -> str:
        self._first_player = self.p1
        for turn in range(MAX_TURNS * 2):
            curr, other = (self.p1, self.p2) if turn % 2 == 0 else (self.p2, self.p1)
            curr.take_turn(other, self.rng)
            if curr.points >= WIN_POINTS: return "p1" if curr == self.p1 else "p2"
            if not other.active and not other.bench: return "p1" if curr == self.p1 else "p2"
        return "draw"

@dataclass
class SimulationResult:
    deck1_name: str
    deck2_name: str
    total_games: int
    deck1_wins: int
    deck2_wins: int
    draws: int
    deck1_hand_accidents: int = 0
    deck2_hand_accidents: int = 0
    games_with_accident: int = 0
    first_player_wins: int = 0
    second_player_wins: int = 0
    p1_first_count: int = 0

    @property
    def deck1_win_rate(self) -> float:
        valid = self.total_games - self.games_with_accident
        return self.deck1_wins / valid if valid else 0.0

    @property
    def deck2_win_rate(self) -> float:
        valid = self.total_games - self.games_with_accident
        return self.deck2_wins / valid if valid else 0.0

def simulate(deck1_path, deck2_path, n=1000, seed=None):
    rng = random.Random(seed)
    d1_cards = load_deck_from_json(deck1_path)
    d2_cards = load_deck_from_json(deck2_path)
    w1 = w2 = draws = 0
    for _ in range(n):
        game = Game(Player("P1", deepcopy(d1_cards)), Player("P2", deepcopy(d2_cards)), rng)
        game.setup()
        res = game.play()
        if res == "p1": w1 += 1
        elif res == "p2": w2 += 1
        else: draws += 1
    return SimulationResult("Deck1", "Deck2", n, w1, w2, draws)
