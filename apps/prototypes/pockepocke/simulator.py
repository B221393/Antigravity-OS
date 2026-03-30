"""
simulator.py – 究極の戦略・確率論的シミュレーター (全環境対応版)
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
    stage: Optional[int] = 0
    hp: Optional[int] = None
    pokemon_type: Optional[str] = None
    evolves_from: Optional[str] = None
    attacks: list[Attack] = field(default_factory=list)
    ability: str = ""
    effect: str = ""
    weakness: Optional[str] = None
    resistance: Optional[str] = None

@dataclass
class ActivePokemon:
    card: Card
    damage: int = 0
    energy: dict[str, int] = field(default_factory=dict)
    status: str = ""
    turn_played: int = 0 

    def __post_init__(self):
        self.is_ex = self.card.name.endswith("ex")
        # 弱点マップの簡易自動生成
        weak_map = {
            "Fire": "Water", "Water": "Lightning", "Grass": "Fire",
            "Lightning": "Fighting", "Fighting": "Psychic", "Psychic": "Darkness",
            "Darkness": "Metal", "Metal": "Fire", "Dragon": "Dragon"
        }
        if not self.card.weakness:
            self.card.weakness = weak_map.get(self.card.pokemon_type)

    @property
    def remaining_hp(self) -> int:
        return max(0, (self.card.hp or 0) - self.damage)
    @property
    def is_knocked_out(self) -> bool: return self.remaining_hp <= 0

    def can_evolve(self, current_turn: int) -> bool:
        if "イーブイ" in self.card.name: return True
        return current_turn > self.turn_played

    def evolve(self, evolution_card: Card, current_turn: int):
        self.card = evolution_card
        self.is_ex = evolution_card.name.endswith("ex")
        self.turn_played = current_turn

# ---------------------------------------------------------------------------
# Strategic Player Logic
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
        self.mulligan_count = 0

    def _init_energy_zone(self) -> list[str]:
        types = set()
        for c in self.deck:
            if c.pokemon_type and c.pokemon_type != "Colorless":
                types.add(c.pokemon_type)
        return list(types) if types else ["Colorless"]

    def take_turn(self, opponent: Player, game: Game, rng: random.Random):
        # 1. 選択肢の事前チェック（自明な手のバイパス）
        actions = self._get_available_actions(opponent, game)
        if not actions or (len(actions) == 1 and actions[0] == "pass"):
            return # Skip inference

        # 2. 戦略推論 (リーサル検知等)
        self._execute_strategic_moves(opponent, game, rng)

    def _get_available_actions(self, opponent, game):
        # 簡略化したアクションリスト
        return ["play_card", "attack", "pass"] 

    def _execute_strategic_moves(self, opponent, game, rng):
        # サポート・特性の処理
        self._process_abilities(opponent, game, rng)
        
        # トレーナーズ・ポケモンのプレイ
        for card in self.hand[:]:
            if card.card_type == "Trainer":
                self._play_trainer_strategic(card, opponent, game, rng)
            elif card.card_type == "Pokemon":
                self._play_pokemon_strategic(card, opponent, game, rng)

        # エネルギー貼付
        self._attach_energy_strategic()

        # 攻撃（早期打ち切りの判定用）
        self._attack_strategic(opponent, game)

    def _play_trainer_strategic(self, card, opponent, game, rng):
        if "ナツメ" in card.name and not self._supporter_played:
            if opponent.bench:
                # 倒せる敵を優先的に引きずり出す
                lethal_targets = [b for b in opponent.bench if b.remaining_hp <= 40]
                idx = 0
                if lethal_targets:
                    idx = opponent.bench.index(lethal_targets[0])
                else:
                    idx = rng.randrange(len(opponent.bench))
                opponent.active, opponent.bench[idx] = opponent.bench[idx], opponent.active
                self._supporter_played = True
                self.hand.remove(card); self.discard.append(card)
        
        elif "博士の研究" in card.name and not self._supporter_played:
            for _ in range(2): 
                if self.deck: self.hand.append(self.deck.pop(0))
            self._supporter_played = True
            self.hand.remove(card); self.discard.append(card)

    def _play_pokemon_strategic(self, card, opponent, game, rng):
        # メガシンカ特例
        is_mega = "メガ" in card.name
        evolution_success = False
        if card.stage and card.stage > 0:
            for slot in ([self.active] if self.active else []) + self.bench:
                if slot.card.name == card.evolves_from and slot.can_evolve(game.turn_count):
                    slot.evolve(card, game.turn_count)
                    self.hand.remove(card); evolution_success = True; break
        
        if not evolution_success and (card.stage == 0 or is_mega):
            if not self.active:
                self.active = ActivePokemon(card); self.active.turn_played = game.turn_count
                self.hand.remove(card)
            elif len(self.bench) < 3:
                p_n = ActivePokemon(card); p_n.turn_played = game.turn_count
                self.bench.append(p_n); self.hand.remove(card)

    def _attach_energy_strategic(self):
        if not self.energy_pool: return
        target = self.active
        # バトル場が脆弱ならベンチに温存
        if not target or (target.remaining_hp <= 20 and self.bench):
            if self.bench: target = max(self.bench, key=lambda p: p.card.hp or 0)
        
        if target:
            for etype, count in list(self.energy_pool.items()):
                target.energy[etype] = target.energy.get(etype, 0) + count
                self.energy_pool[etype] = 0

    def _attack_strategic(self, opponent, game):
        if not self.active or not opponent.active: return
        valid_attacks = self.active.card.attacks
        if not valid_attacks: return

        # 弱点計算
        dmg = valid_attacks[0].damage
        if opponent.active.card.weakness == self.active.card.pokemon_type:
            dmg += 20
        
        opponent.active.damage += dmg
        if opponent.active.is_knocked_out:
            self.points += (2 if opponent.active.is_ex else 1)
            opponent.active = None
            if opponent.bench: opponent.active = opponent.bench.pop(0)

    def _process_abilities(self, opponent, game, rng):
        # ゲッコウガ: 狙撃
        for p in ([self.active] if self.active else []) + self.bench:
            if "ゲッコウガ" in p.card.name:
                opp_targets = ([opponent.active] if opponent.active else []) + opponent.bench
                if opp_targets:
                    # リーサル優先
                    target = next((o for o in opp_targets if o.remaining_hp <= 20), rng.choice(opp_targets))
                    target.damage += 20
                    if target.is_knocked_out:
                        self.points += (2 if target.is_ex else 1)
                        if target == opponent.active:
                            opponent.active = None
                            if opponent.bench: opponent.active = opponent.bench.pop(0)
                        else: opponent.bench.remove(target)

# ---------------------------------------------------------------------------
# Game Engine with Early Stopping & Seed Management
# ---------------------------------------------------------------------------

class Game:
    def __init__(self, p1: Player, p2: Player, deck1_cfg: dict = None, deck2_cfg: dict = None) -> None:
        self.p1 = p1
        self.p2 = p2
        self.turn_count = 0
        self.max_turns = 50
        if deck1_cfg and "energy_type" in deck1_cfg: self.p1.energy_zone = deck1_cfg["energy_type"]
        if deck2_cfg and "energy_type" in deck2_cfg: self.p2.energy_zone = deck2_cfg["energy_type"]
        self._setup()

    def _setup(self):
        """たねポケモンが出るまで試行 (マリガンを統計から除外するための処理)"""
        for p in [self.p1, self.p2]:
            has_basic = False
            while not has_basic:
                p.mulligan_count += 1
                random.shuffle(p.deck)
                p.deck = (p.hand + p.deck); p.hand = []
                for _ in range(5): 
                    if p.deck: p.hand.append(p.deck.pop(0))
                for c in p.hand[:]:
                    is_mega = "メガ" in c.name
                    if (c.card_type == "Pokemon" and c.stage == 0) or is_mega:
                        if "化石" in c.name: continue
                        p.active = ActivePokemon(c); p.hand.remove(c); has_basic = True; break
                if p.mulligan_count > 100: break

    def play(self, rng: random.Random, verbose=False) -> str:
        for _ in range(self.max_turns):
            self.turn_count += 1
            curr, other = (self.p1, self.p2) if self.turn_count % 2 == 1 else (self.p2, self.p1)
            
            if verbose:
                print(f"\n{'='*40}")
                print(f" Turn {self.turn_count} | Turn: {curr.name}")
                print(f"{'='*40}")

            # 早期打ち切り判定: 相手の盤面が空
            if not other.active and not other.bench: return "p1" if curr == self.p1 else "p2"

            # エネルギー生成
            if self.turn_count > 1 or curr == self.p2:
                etype = rng.choice(curr.energy_zone)
                curr.energy_pool[etype] = curr.energy_pool.get(etype, 0) + 1
            
            curr.take_turn(other, self, rng)
            
            # リーサルチェック
            if curr.points >= 3: return "p1" if curr == self.p1 else "p2"
        return "draw"

class HumanPlayer(Player):
    def take_turn(self, opponent: Player, game: Game, rng: random.Random):
        # ドロー
        if self.deck:
            self.hand.append(self.deck.pop(0))
        
        self._supporter_played = False
        
        while True:
            self._display_board(opponent, game)
            print(f"\n[Hand] {' / '.join([f'({i}) {c.name}' for i, c in enumerate(self.hand)])}")
            print(f"[Energy Pool] {self.energy_pool}")
            print(f"[Points] You: {self.points} / Opponent: {opponent.points}")
            
            cmd = input("\nCommand ( (index): Play card, e: Attach Energy, a: Attack, p: Pass ): ").lower().strip()
            
            if cmd == 'p':
                break
            elif cmd == 'a':
                self._attack_strategic(opponent, game)
                break
            elif cmd == 'e':
                self._attach_energy_human()
            elif cmd.isdigit():
                idx = int(cmd)
                if 0 <= idx < len(self.hand):
                    card = self.hand[idx]
                    if card.card_type == "Pokemon":
                        self._play_pokemon_strategic(card, opponent, game, rng)
                    elif card.card_type == "Trainer":
                        self._play_trainer_strategic(card, opponent, game, rng)
                else:
                    print("Invalid index.")
            else:
                print("Unknown command.")

    def _display_board(self, opponent, game):
        print(f"\n--- OPPONENT: {opponent.name} ---")
        if opponent.active:
            print(f" ACTIVE: {opponent.active.card.name} (HP: {opponent.active.remaining_hp}/{opponent.active.card.hp}) [E: {opponent.active.energy}]")
        else:
            print(" ACTIVE: None")
        print(f" BENCH: {', '.join([f'{b.card.name} ({b.remaining_hp})' for b in opponent.bench])}")
        
        print(f"\n--- YOU: {self.name} ---")
        if self.active:
            print(f" ACTIVE: {self.active.card.name} (HP: {self.active.remaining_hp}/{self.active.card.hp}) [E: {self.active.energy}]")
        else:
            print(" ACTIVE: None")
        print(f" BENCH: {', '.join([f'{b.card.name} ({b.remaining_hp})' for b in self.bench])}")

    def _attach_energy_human(self):
        if not self.energy_pool or sum(self.energy_pool.values()) == 0:
            print("No energy to attach.")
            return
        
        targets = []
        if self.active: targets.append(("Active", self.active))
        for i, b in enumerate(self.bench):
            targets.append((f"Bench {i}", b))
        
        if not targets: return
        
        print("\nTarget:")
        for i, (name, slot) in enumerate(targets):
            print(f" ({i}) {name}: {slot.card.name}")
        
        t_cmd = input("Select target index: ")
        if t_cmd.isdigit():
            t_idx = int(t_cmd)
            if 0 <= t_idx < len(targets):
                target = targets[t_idx][1]
                # 全エネルギーを貼る
                for etype, count in list(self.energy_pool.items()):
                    target.energy[etype] = target.energy.get(etype, 0) + count
                    self.energy_pool[etype] = 0
                print(f"Attached energy to {target.card.name}.")

def load_master_db(path):
    # (既存のload_master_dbロジックの末尾をコピー)
    db = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 4: continue
            cid = row[0]
            try:
                db[cid] = Card(id=cid, name=row[1], card_type=row[2], pokemon_type=row[3], 
                              hp=int(row[4]) if str(row[4]).isdigit() else 60,
                              stage=int(row[5]) if str(row[5]).isdigit() else 0, 
                              evolves_from=row[6], ability=row[7], effect=row[8])
                dmg = 30
                if "ex" in row[1].lower(): dmg = 80
                if "メガ" in row[1]: dmg = 120
                db[cid].attacks.append(Attack({"Colorless": 1}, dmg, "通常攻撃"))
            except Exception: continue
    return db

if __name__ == "__main__":
    print("Strategic Simulator Ready.")
