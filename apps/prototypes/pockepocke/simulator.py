"""
simulator.py – ポケモンカードゲーム ポケポケ シミュレーター

ポケポケのルール概要:
  - デッキ枚数: 20枚（同名カード最大2枚）
  - 初期手札: 5枚
  - 毎ターン1枚ドロー
  - エネルギーはエネルギーゾーンから毎ターン1個補給（デッキに含まない）
  - バトル場1体 + ベンチ最大3体
  - 相手ポケモンを3体倒した方が勝ち（ポイント制）
  - 手札事故: 初期手札にたねポケモンが1枚もない状態
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
    energy_cost: dict[str, int] # {"Fighting": 1, "Metal": 1} のような形式
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
    stage: Optional[int]    # 0=たね, 1=1進化, 2=2進化  (None for non-Pokemon)
    hp: Optional[int]
    pokemon_type: Optional[str]
    evolves_from: Optional[str]
    attacks: list[Attack]
    weakness: Optional[str] = None  # 弱点タイプを追加
    effect: str = ""        # For Trainer / Item / Supporter cards
    ability: str = ""       # 特性 (例: "prevent_ex_damage")
    is_baby: bool = False   # ベビィポケモン: 攻撃前にコイントスが必要


@dataclass
class ActivePokemon:
    """A Card that has been placed in play, tracking damage counters and status."""
    card: Card
    damage: int = 0
    energy: dict[str, int] = field(default_factory=dict) # タイプ別の保持エネ
    status: str = ""        # "" | "sleep" | "poison" | "burn"
    is_ex: bool = field(init=False)
    just_switched: bool = False  # この番に入れ替わったかのフラグ
    extra_damage: int = 0        # 次の攻撃に加算されるダメージ量

    def __post_init__(self) -> None:
        self.is_ex = self.card.name.endswith("ex")
        if not self.energy:
            self.energy = {}

    @property
    def total_energy(self) -> int:
        return sum(self.energy.values())

    @property
    def remaining_hp(self) -> int:
        return max(0, self.card.hp - self.damage)  # type: ignore[operator]

    @property
    def is_knocked_out(self) -> bool:
        return self.remaining_hp <= 0

    @property
    def best_attack(self) -> Optional[Attack]:
        """必要なタイプのエネがすべて揃っているワザの中で最大打点のものを返す"""
        usable = []
        for a in self.card.attacks:
            can_use = True
            for etype, count in a.energy_cost.items():
                if self.energy.get(etype, 0) < count:
                    can_use = False
                    break
            if can_use:
                usable.append(a)
        return max(usable, key=lambda a: a.damage) if usable else None

    @property
    def strongest_attack(self) -> Optional[Attack]:
        """必要エネを無視して最もダメージが高いワザを返す（AIの目標設定用）"""
        return max(self.card.attacks, key=lambda a: a.damage) if self.card.attacks else None

    def evolve(self, evolution_card: Card) -> None:
        """Replace this Pokémon's card with its evolution, preserving battle state."""
        self.card = evolution_card
        self.is_ex = evolution_card.name.endswith("ex")


# ---------------------------------------------------------------------------
# Deck loading helpers
# ---------------------------------------------------------------------------

def _build_card_from_info(info: dict) -> Card:
    attacks = []
    card_type = info.get("type", info.get("pokemon_type", "-"))
    
    # 既存のCSV/DB形式のワザ解析
    if info.get("attack1_name"):
        dmg_str = str(info["attack1_damage"]).replace("+","").replace("x","").replace("×","")
        dmg = int(dmg_str) if dmg_str.isdigit() else 0
        raw_cost = info.get("attack1_cost", "0")
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
        attacks.append(Attack(name=info["attack1_name"], energy_cost=cost_dict, damage=dmg, effect=info.get("attack1_effect","")))
    
    if info.get("attack2_name"):
        dmg_str = str(info["attack2_damage"]).replace("+","").replace("x","").replace("×","")
        dmg = int(dmg_str) if dmg_str.isdigit() else 0
        raw_cost = info.get("attack2_cost", "0")
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
        attacks.append(Attack(name=info["attack2_name"], energy_cost=cost_dict, damage=dmg, effect=info.get("attack2_effect","")))

    # JSON直接形式（attacksがリスト形式）の場合の解析
    if not attacks and "attacks" in info:
        for a in info["attacks"]:
            cost = a.get("energy_cost", {})
            if isinstance(cost, int):
                cost = {card_type if card_type != "-" else "Colorless": cost}
            attacks.append(Attack(
                name=a.get("name", ""),
                energy_cost=cost,
                damage=a.get("damage", 0),
                effect=a.get("effect", "")
            ))

    def safe_int(v):
        if v is None: return None
        v_str = str(v).strip()
        return int(v_str) if v_str.isdigit() else None

    return Card(
        name=info["name"],
        card_type=info.get("card_type", "Pokemon"),
        stage=safe_int(info.get("stage")),
        hp=safe_int(info.get("hp")),
        pokemon_type=card_type,
        evolves_from=info.get("evolves_from"),
        attacks=attacks,
        ability=info.get("ability", ""),
        effect=info.get("effect", ""),
        is_baby=False
    )

def load_deck_from_json(path: str | Path) -> list[Card]:
    """master_card_db.csv または JSON内の直接定義からデッキを構築する。"""
    db_path = Path(__file__).parent / "data" / "master_card_db.csv"
    db = {}
    if db_path.exists():
        with open(db_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                db[str(row["id"])] = row
    
    with open(path, encoding="utf-8") as f:
        deck_data = json.load(f)
    
    raw_cards = deck_data.get("cards", [])
    cards: list[Card] = []
    
    for entry in raw_cards:
        if isinstance(entry, (str, int)):
            # ID形式
            cid_str = str(entry)
            if cid_str in db:
                cards.append(_build_card_from_info(db[cid_str]))
        elif isinstance(entry, dict):
            # オブジェクト形式 (count対応)
            count = entry.get("count", 1)
            card_obj = _build_card_from_info(entry)
            for _ in range(count):
                cards.append(deepcopy(card_obj))
    
    if len(cards) != 20:
        raise ValueError(f"Deck must have exactly 20 cards. Found {len(cards)} in {path}")
    
    return cards


# ---------------------------------------------------------------------------
# Player / Game state
# ---------------------------------------------------------------------------

WIN_POINTS = 3      # 相手ポケモンを3体倒したら勝利
BENCH_MAX = 3       # ベンチ最大数
HAND_SIZE = 5       # 初期手札枚数
ENERGY_PER_TURN = 1 # ターンごとに補給されるエネルギー量
MAX_TURNS = 50      # 無限ループ防止


class Player:
    """Represents one player with deck, hand, board state, and simple AI."""

    def __init__(self, name: str, deck_cards: list[Card]) -> None:
        self.name = name
        self.deck: list[Card] = deck_cards[:]
        self.hand: list[Card] = []
        self.discard: list[Card] = []
        self.active: Optional[ActivePokemon] = None
        self.bench: list[ActivePokemon] = []
        self.energy_pool: dict[str, int] = {} # タイプ別のエネルギー
        self.points: int = 0        # KO points scored
        self._supporter_played: bool = False
        self.supporter_damage_boost: int = 0
        self.iris_active: bool = False # アイリス使用フラグ
        self.supporter_locked: bool = False # 次の自分の番、サポーターを使えないフラグ
        self.item_locked: bool = False # 次の自分の番、グッズ（Item）を使えないフラグ
        self.history: list[str] = []   # 各ターンの思考・行動ログ

    def log(self, msg: str) -> None:
        self.history.append(msg)

    def shuffle_deck(self, rng: random.Random) -> None:
        rng.shuffle(self.deck)

    def draw(self, n: int = 1) -> list[Card]:
        drawn = self.deck[:n]
        self.deck = self.deck[n:]
        self.hand.extend(drawn)
        return drawn

    @property
    def has_basic_in_hand(self) -> bool:
        return any(c.card_type == "Pokemon" and c.stage == 0 for c in self.hand)

    def setup_active(self) -> bool:
        basics = [c for c in self.hand if c.card_type == "Pokemon" and c.stage == 0]
        if not basics:
            return False
        chosen = basics[0]
        self.hand.remove(chosen)
        self.active = ActivePokemon(card=chosen)
        return True

    def take_turn(self, opponent: "Player", rng: random.Random) -> Optional[str]:
        self._supporter_played = False
        self.supporter_damage_boost = 0 
        self.iris_active = False 
        if self.deck:
            self.draw(1)
        
        # エネルギー生成
        types_in_deck = set()
        all_my_cards = self.deck + self.hand + self.discard
        if self.active: all_my_cards.append(self.active.card)
        for ap in self.bench: all_my_cards.append(ap.card)

        for c in all_my_cards:
            if c.pokemon_type and c.pokemon_type != "-":
                if c.pokemon_type == "Dragon":
                    # ドラゴンタイプの場合は、ワザのコストから必要なタイプを抽出
                    for attack in c.attacks:
                        for etype in attack.energy_cost.keys():
                            if etype != "Colorless":
                                types_in_deck.add(etype)
                else:
                    types_in_deck.add(c.pokemon_type)
        
        types_list = list(types_in_deck)
        if types_list:
            etype = rng.choice(types_list)
            self.energy_pool[etype] = self.energy_pool.get(etype, 0) + 1
            self.log(f"Energy: Generated {etype} energy (Pool: {self.energy_pool})")
        
        self._use_abilities(opponent, rng)

        # --- すごいAI: 脅威予測と生存戦略 ---
        imminent_death = False
        if self.active and opponent.active:
            opp_attack = opponent.active.best_attack
            if opp_attack:
                expected_dmg = opp_attack.damage
                if self.active.card.weakness == opponent.active.card.pokemon_type:
                    expected_dmg += 20
                if expected_dmg >= self.active.remaining_hp:
                    imminent_death = True
                    self.log(f"AI Prediction: {self.active.card.name} will likely be KO'd next turn by {opponent.active.card.name}.")

        # 勝ち筋の計算
        if self.active and opponent.active:
            attack = self.active.best_attack
            if attack:
                dmg = attack.damage + self.active.extra_damage
                if opponent.active.card.weakness == self.active.card.pokemon_type:
                    dmg += 20
                
                will_ko = dmg >= opponent.active.remaining_hp
                pts = 2 if opponent.active.is_ex else 1
                iris_card = next((c for c in self.hand if c.effect == "iris_point_boost"), None)
                if iris_card and will_ko and (self.points + pts + 1 >= WIN_POINTS):
                    self.log(f"Strategy: LETHAL! Using Iris on {opponent.active.card.name} ({self.points} -> {self.points + pts + 1})")
                    self._apply_supporter(iris_card, rng, opponent)
                    self.hand.remove(iris_card)
                    self.discard.append(iris_card)
                    self._supporter_played = True

        # 入れ替え戦略（致死予測に基づく）
        if self.active and self.bench:
            should_switch = False
            if self.active.status == "sleep":
                should_switch = True
            elif imminent_death and not self.active.is_ex and any(b.is_ex for b in self.bench):
                # 非exが倒されそうな時、後ろに強力なexがいれば壁として見捨てる（入れ替えない）選択も
                pass
            elif imminent_death and self.active.is_ex:
                # exが倒されそうな時は絶対に逃がす（ポイントを2点取られるのを防ぐ）
                self.log("Strategy: EVASION! Switching EX Pokemon to prevent 2-point loss.")
                should_switch = True
            elif self.active.remaining_hp <= 30:
                should_switch = True
            
            if should_switch:
                self._switch_pokemon()

        self._play_trainers(rng, opponent)
        self._evolve_pokemon()
        self._place_basics_to_bench()
        
        # --- すごいAI: エネルギー分散投資 ---
        if self.energy_pool:
            if imminent_death and self.bench:
                # 倒されそうな場合、バトル場ではなくベンチのエースを育てる
                target = max(self.bench, key=lambda ap: (ap.card.hp or 0) * (2 if ap.is_ex else 1))
                for etype, count in self.energy_pool.items():
                    target.energy[etype] = target.energy.get(etype, 0) + count
                self.log(f"Strategy: Hedging! Attaching energy to bench {target.card.name} instead of doomed active.")
                self.energy_pool = {}
            else:
                self._attach_energy()

        return self._attack(opponent, rng)

    def _use_abilities(self, opponent: "Player", rng: random.Random) -> None:
        """毎ターン攻撃前に自動で発動する特性の処理"""
        all_my_pokemon = []
        if self.active: all_my_pokemon.append(self.active)
        all_my_pokemon.extend(self.bench)

        for p in all_my_pokemon:
            # ゲッコウガの「みずしゅりけん」: ベンチに20ダメージ
            if p.card.ability == "water_shuriken" and opponent.bench:
                # 戦略的ターゲット選定: HPが最も低いベンチポケモンを狙う
                target = min(opponent.bench, key=lambda ap: ap.remaining_hp)
                target.damage += 20
                if target.is_knocked_out:
                    self.points += (2 if target.is_ex else 1)
                    opponent.discard.append(target.card)
                    opponent.bench.remove(target)

    def _play_trainers(self, rng: random.Random, opponent: Optional["Player"] = None) -> None:
        # グッズ（Item）は制限なしに使用
        for card in self.hand[:]:
            if card.card_type == "Item":
                self._apply_item(card, rng, opponent)
                if card in self.hand: # まだ手札にあれば（サーチ失敗等でない場合）
                    self.hand.remove(card)
                    self.discard.append(card)

        # サポーター（Supporter）はターン1回の戦略的選択
        if not self._supporter_played:
            if self.supporter_locked:
                self.log(f"Strategy: Supporter usage is LOCKED by opponent's effect!")
                self.supporter_locked = False # 1ターン封じられたので解除
                return

            best_supporter = self._choose_best_supporter(opponent, rng)
            if best_supporter:
                self.log(f"Strategy: Choosing to play {best_supporter.name} this turn.")
                self._apply_supporter(best_supporter, rng, opponent)
                self.hand.remove(best_supporter)
                self.discard.append(best_supporter)
                self._supporter_played = True

    def _choose_best_supporter(self, opponent: Optional["Player"], rng: random.Random) -> Optional[Card]:
        supporters = [c for c in self.hand if c.card_type == "Supporter"]
        if not supporters: return None
        if not opponent or not opponent.active: return supporters[0]

        # 1. サカキ (boost_damage_20): 倒せるなら使う
        if any(c.effect == "boost_damage_20" for c in supporters):
            attack = self.active.best_attack if self.active else None
            if attack:
                dmg = attack.damage + self.active.extra_damage
                if dmg < opponent.active.remaining_hp <= (dmg + 20):
                    return next(c for c in supporters if c.effect == "boost_damage_20")

        # 2. ナツメ (switch_opponent_active): 脅威排除ロジック
        if any(c.effect == "switch_opponent_active" for c in supporters):
            if opponent.bench:
                # 相手のベンチに育ちかけのEXがいる、または倒しやすい手負いがいる場合
                vulnerable_ex = [b for b in opponent.bench if b.is_ex and b.remaining_hp <= (self.active.best_attack.damage if self.active and self.active.best_attack else 0)]
                if vulnerable_ex:
                    self.log("Strategy: THREAT ELIMINATION! Using Boss's Orders on vulnerable EX.")
                    return next(c for c in supporters if c.effect == "switch_opponent_active")

        # 3. ものまねむすめ (draw_until_opponent_hand_size): 手札差が3枚以上なら爆アド
        copycat = next((c for c in supporters if c.effect == "draw_until_opponent_hand_size"), None)
        if copycat and len(opponent.hand) - len(self.hand) >= 3:
            self.log("Strategy: Value! Using Copycat to draw massive cards.")
            return copycat

        # 4. 博士の研究 (draw_3)
        research = next((c for c in supporters if c.effect == "draw_3"), None)
        if research and len(self.hand) < 4: 
            return research

        # 5. マーズ (mars_hand_discard): 相手の手札が多い時に妨害
        mars = next((c for c in supporters if c.effect == "mars_hand_discard"), None)
        if mars and len(opponent.hand) >= 4:
            return mars

        return supporters[0]

    def _apply_item(self, card: Card, rng: random.Random, opponent: Optional["Player"] = None) -> None:
        if card.effect == "heal_30" and self.active:
            self.active.damage = max(0, self.active.damage - 30)
        elif card.effect in ("search_basic", "search_any"):
            self._search_deck(card.effect, rng)
        elif card.effect == "boost_damage_30" and self.active:
            self.active.extra_damage += 30
        elif card.effect == "rare_candy":
            self._apply_rare_candy()
        elif card.effect == "hand_to_deck_refresh":
            # メンテナンス: 手札を2枚山に戻して1枚引く (事故回避)
            if len(self.hand) >= 2:
                for _ in range(2):
                    c = self.hand.pop(rng.randrange(len(self.hand)))
                    self.deck.append(c)
                self.shuffle_deck(rng)
                self.draw(1)
        elif card.effect == "hp_boost_20" and self.active:
            # 大きなマント: 最大HPを一時的に+20
            self.active.damage = max(0, self.active.damage - 20)
        elif card.effect == "switch" and self.bench:
            self._switch_pokemon()
        elif card.effect == "energy_accel" and self.active:
            self.active.energy += 1
        elif card.effect == "opponent_discard_hand_to_3" and opponent:
            if len(opponent.hand) > 3:
                num_discard = len(opponent.hand) - 3
                for _ in range(num_discard):
                    c = opponent.hand.pop(rng.randrange(len(opponent.hand)))
                    opponent.discard.append(c)

    def _switch_pokemon(self) -> None:
        if not self.bench:
            return
        if self.active:
            self.active.status = "" # Switching cures status
            self.active.extra_damage = 0 # Buffs are usually lost on switch
            old_active = self.active
            self.active = self.bench.pop(0)
            self.bench.append(old_active)
            self.active.just_switched = True

    def _apply_rare_candy(self) -> None:
        in_play = []
        if self.active:
            in_play.append(self.active)
        in_play.extend(self.bench)
        stage2_cards = [c for c in self.hand if c.card_type == "Pokemon" and c.stage == 2]
        for slot in in_play:
            if slot.card.stage != 0:
                continue
            for stage2 in stage2_cards:
                # 正しい進化ラインかチェック (例: オノノクスの evolves_from は オノンド)
                # ポケポケのふしぎなアメは、2進化カードをたねから直接重ねる
                # ただし進化系統が一致している必要がある
                if stage2.evolves_from:
                    # ここでは簡易的に「進化前の進化前」の名前を特定できないため、
                    # CSVのデータ構造を補完するか、2進化カード側の定義で判定する
                    # オノノクスの場合は「オノンド」から進化だが、アメなら「キバゴ」から進化可能
                    # 便宜上、全ての2進化は対応する系統のたねからアメで進化可能とする
                    # 本来は2進化カードに「たねの名前」を持たせるのが理想
                    is_valid_evolution = False
                    if stage2.name == "オノノクス" and slot.card.name == "キバゴ":
                        is_valid_evolution = True
                    elif stage2.name == "サーナイトex" and slot.card.name == "ラルトス":
                        is_valid_evolution = True
                    elif stage2.name == "リザードンex" and slot.card.name == "ヒトカゲ":
                        is_valid_evolution = True
                    
                    if is_valid_evolution:
                        slot.evolve(stage2)
                        self.hand.remove(stage2)
                        self.log(f"Item: Used Rare Candy to evolve {slot.card.name} into {stage2.name}!")
                        return

    def _apply_supporter(self, card: Card, _rng: random.Random, opponent: Optional["Player"] = None) -> None:
        if card.effect == "draw_5":
            self.draw(min(5, len(self.deck)))
        elif card.effect in ("draw_3_and_bench_supporter", "draw_3"):
            self.draw(min(3, len(self.deck)))
        elif card.effect == "draw_2":
            self.draw(min(2, len(self.deck)))
        elif card.effect == "draw_until_opponent_hand_size" and opponent:
            # ものまねむすめ: 相手の手札と同じ枚数になるように引く
            diff = len(opponent.hand) - len(self.hand)
            if diff > 0:
                self.draw(min(diff, len(self.deck)))
        elif card.effect == "mars_hand_discard" and opponent and opponent.hand:
            # マーズ: 2枚引き、相手の手札をランダムに1枚トラッシュ
            self.draw(min(2, len(self.deck)))
            c = opponent.hand.pop(_rng.randrange(len(opponent.hand)))
            opponent.discard.append(c)
        elif card.effect == "iris_damage_boost" and opponent:
            # アイリス: 相手の獲得ポイント数に応じてダメージアップ (1点ごとに+20, 最大+40)
            self.supporter_damage_boost = min(40, opponent.points * 20)
        elif card.effect == "search_any":
            self._search_deck("search_any", _rng)
        elif card.effect == "heal_bench_50" and self.bench:
            target = min(self.bench, key=lambda ap: ap.remaining_hp)
            target.damage = max(0, target.damage - 50)
        elif card.effect == "switch_opponent_active" and opponent and opponent.bench:
            new_active = opponent.bench.pop(0)
            if opponent.active:
                opponent.bench.append(opponent.active)
            opponent.active = new_active
        elif card.effect == "discard_opponent_bench" and opponent and opponent.bench:
            target = max(
                opponent.bench,
                key=lambda ap: (ap.card.hp or 0) * max((a.damage for a in ap.card.attacks), default=0),
            )
            opponent.bench.remove(target)
            opponent.discard.append(target.card)

    def _search_deck(self, effect: str, rng: random.Random) -> None:
        candidates = [
            c for c in self.deck
            if (effect == "search_basic" and c.card_type == "Pokemon" and c.stage == 0)
            or effect == "search_any"
        ]
        if candidates:
            chosen = rng.choice(candidates)
            self.deck.remove(chosen)
            self.hand.append(chosen)

    def _evolve_pokemon(self) -> None:
        self._try_evolve(self.active)
        for bench_mon in self.bench:
            self._try_evolve(bench_mon)

    def _try_evolve(self, slot: Optional[ActivePokemon]) -> None:
        if slot is None:
            return
        for card in self.hand[:]:
            if (
                card.card_type == "Pokemon"
                and card.stage is not None
                and card.stage > 0
                and card.evolves_from == slot.card.name
            ):
                slot.evolve(card)
                self.hand.remove(card)
                return

    def _place_basics_to_bench(self) -> None:
        for card in self.hand[:]:
            if len(self.bench) >= BENCH_MAX:
                break
            if card.card_type == "Pokemon" and card.stage == 0:
                self.bench.append(ActivePokemon(card=card))
                self.hand.remove(card)

    def _attach_energy(self) -> None:
        if self.active and self.energy_pool:
            for etype, count in self.energy_pool.items():
                self.active.energy[etype] = self.active.energy.get(etype, 0) + count
            self.energy_pool = {}

    def _attack(self, opponent: "Player", rng: random.Random) -> Optional[str]:
        if self.active is None or opponent.active is None:
            return None
        
        # 眠りチェック
        if self.active.status == "sleep":
            if rng.random() < 0.5:
                self.log(f"{self.active.card.name} woke up!")
                self.active.status = ""
            else:
                self.log(f"{self.active.card.name} is still sleeping...")
                return None
        
        # ベベィチェック
        if opponent.active.card.is_baby:
            if rng.random() >= 0.5:
                self.log(f"Attack failed due to Baby rule!")
                return None
        
        attack = self.active.best_attack
        if attack is None:
            return None
        if attack.coin_flips > 0:
            heads = sum(1 for _ in range(attack.coin_flips) if rng.random() < 0.5)
            actual_damage = attack.damage * heads
        else:
            actual_damage = attack.damage
        
        # 特殊ブースト合算
        actual_damage += self.active.extra_damage
        actual_damage += self.supporter_damage_boost
        
        # バフのリセット
        self.active.extra_damage = 0
        self.supporter_damage_boost = 0

        # 【新ギミック】特性チェック: 相手が ex無効特性を持っており、自分が ex の場合
        if opponent.active.card.ability == "prevent_ex_damage" and self.active.is_ex:
            self.log(f"Ability: {opponent.active.card.name} prevented damage from EX!")
            actual_damage = 0

        # 弱点計算 (+20ダメージ)
        if opponent.active.card.weakness == self.active.card.pokemon_type:
            actual_damage += 20

        # ダメージ反映
        opponent.active.damage += actual_damage
        self.log(f"{self.active.card.name} uses {attack.name} for {actual_damage} damage!")

        # 効果の判定（汎用化）
        if attack.effect == "bench_energy_20":
            # 50 + お互いのベンチのエネルギー数 * 20
            my_bench_energy = sum(b.total_energy for b in self.bench)
            opp_bench_energy = sum(b.total_energy for b in opponent.bench)
            extra = (my_bench_energy + opp_bench_energy) * 20
            opponent.active.damage += extra
            self.log(f"Effect: Bench energy boost! +{extra} damage.")
        elif attack.effect == "haisui_no_jin":
            if self.active.remaining_hp <= (self.active.card.hp or 0) / 2:
                actual_damage *= 2 # 注: 現状の実装では即時反映ではないがロジックとして保持
        elif attack.effect == "side_link":
            actual_damage += opponent.points * 30
        elif attack.effect == "boost_next_damage_40":
            self.active.extra_damage = 40
        elif attack.effect == "discard_self_energy_1":
            self.active.energy = max(0, self.active.energy - 1)
        elif attack.effect == "sleep" and opponent.active:
            opponent.active.status = "sleep"

        if opponent.active.is_knocked_out:
            # 気絶処理
            points = 2 if opponent.active.is_ex else 1
            if self.iris_active:
                points += 1
                self.log(f"Strategy: Iris added +1 point! ({points - 1} -> {points})")
                self.iris_active = False # 使用済み
            
            self.points += points
            self.log(f"KO! {self.name} gets {points} points. (Total: {self.points})")
            
            opponent.discard.append(opponent.active.card)
            
            # 【新ギミック】オドリドリ（パッションダンス等）: 
            if any(b.card.name == "オドリドリ" for b in self.bench):
                self.draw(1)
            
            opponent.active = None
            if opponent.bench:
                opponent.active = opponent.bench.pop(0)
        
        return attack.effect

    def _handle_attack_effect(self, effect: str, active: ActivePokemon, opponent: Player, rng: random.Random) -> None:
        """特殊効果タグに基づいた固有ロジック"""
        if effect == "discard_self_energy_1":
            active.energy = max(0, active.energy - 1)
        elif effect == "boost_next_damage_40":
            active.extra_damage = 40
        elif effect == "sleep" and opponent.active:
            opponent.active.status = "sleep"
        elif effect == "energy_accel_bench" and self.bench:
            # リーシャン: ベンチのポケモン1匹にエネルギーを1個加速
            target = max(self.bench, key=lambda ap: (ap.card.hp or 0)) 
            target.energy += 1
            self.log(f"Effect: Energy accelerated to bench {target.card.name}")
        elif effect == "energy_accel_from_discard" and self.bench:
            # メガライボルト: トラッシュからベンチにエネ2個加速 (簡易的に2個生成して付着)
            target = max(self.bench, key=lambda ap: (ap.card.hp or 0))
            etype = self.active.card.pokemon_type if self.active else "Lightning"
            target.energy[etype] = target.energy.get(etype, 0) + 2
            self.log(f"Effect: Turbo Bolt accelerated 2 energies to {target.card.name}!")
        elif effect == "lock_supporter":

            # メガアブソル: 相手の次の番、サポーターを封じる
            opponent.supporter_locked = True
            self.log(f"Effect: {opponent.name}'s Supporters are LOCKED for next turn!")
        elif effect == "side_link":
            pass


class Game:
    def __init__(self, player1: Player, player2: Player, rng: random.Random, randomize_first_player: bool = False) -> None:
        self.p1 = player1
        self.p2 = player2
        self.rng = rng
        self.randomize_first_player = randomize_first_player
        self._first_player: Optional[Player] = None

    def _deal_opening_hand(self, player: Player) -> bool:
        """
        Deals 5 cards to the player. If no basic Pokémon is found, reshuffles and tries again.
        Returns True if an accident (no basic on FIRST draw) occurred.
        """
        all_cards = player.deck + player.hand
        if not any(c.card_type == "Pokemon" and c.stage == 0 for c in all_cards):
            return False

        accident = False
        for i in range(100):
            if player.hand:
                player.deck.extend(player.hand)
                player.hand.clear()
            player.shuffle_deck(self.rng)
            player.draw(HAND_SIZE)
            
            if i == 0 and not player.has_basic_in_hand:
                accident = True
                
            if player.has_basic_in_hand:
                break
        return accident

    def setup(self) -> tuple[bool, bool]:
        """Sets up the game by dealing hands and choosing active Pokémon.
        Returns (p1_accident, p2_accident) indicating if first draw was failed."""
        a1 = self._deal_opening_hand(self.p1)
        a2 = self._deal_opening_hand(self.p2)
        self.p1.setup_active()
        self.p2.setup_active()
        return a1, a2

    def play(self) -> str:
        if self.randomize_first_player and self.rng.random() < 0.5:
            first_player, second_player = (self.p2, self.p1)
        else:
            first_player, second_player = (self.p1, self.p2)
        self._first_player = first_player
        for turn in range(1, MAX_TURNS * 2 + 1):
            current, other = (first_player, second_player) if turn % 2 == 1 else (second_player, first_player)
            if current.active is None and not current.bench:
                return "p2" if current is self.p1 else "p1"
            if other.active is None and not other.bench:
                return "p1" if current is self.p1 else "p2"
            if turn == 1:
                # 1ターン目のエネルギー生成
                types_in_deck = list(set(current.active.card.pokemon_type for current in [current] if current.active and current.active.card.pokemon_type and current.active.card.pokemon_type != "-"))
                if not types_in_deck: # 控えも考慮
                    types_in_deck = list(set(c.pokemon_type for c in (current.deck + current.hand + current.discard) if c.pokemon_type and c.pokemon_type != "-"))
                if types_in_deck:
                    etype = self.rng.choice(types_in_deck)
                    current.energy_pool[etype] = current.energy_pool.get(etype, 0) + 1
                
                current._play_trainers(self.rng, other)
                current._evolve_pokemon()
                current._place_basics_to_bench()
                current._attach_energy()
                continue
            current.take_turn(other, self.rng)
            if current.points >= WIN_POINTS:
                return "p1" if current is self.p1 else "p2"
            if other.active is None and not other.bench:
                return "p1" if current is self.p1 else "p2"
        return "draw"


@dataclass
class SimulationResult:
    deck1_name: str
    deck2_name: str
    total_games: int
    deck1_wins: int
    deck2_wins: int
    draws: int
    deck1_hand_accidents: int
    deck2_hand_accidents: int
    games_with_accident: int
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

    @property
    def deck1_accident_rate(self) -> float:
        return self.deck1_hand_accidents / self.total_games if self.total_games else 0.0

    @property
    def deck2_accident_rate(self) -> float:
        return self.deck2_hand_accidents / self.total_games if self.total_games else 0.0

    @property
    def first_player_win_rate(self) -> float:
        decided = self.first_player_wins + self.second_player_wins
        return self.first_player_wins / decided if decided else 0.0

    @property
    def second_player_win_rate(self) -> float:
        decided = self.first_player_wins + self.second_player_wins
        return self.second_player_wins / decided if decided else 0.0

    def __str__(self) -> str:
        valid = self.total_games - self.games_with_accident
        decided = self.first_player_wins + self.second_player_wins
        fp_line = f"先行勝率: {self.first_player_win_rate:.1%}  後攻勝率: {self.second_player_win_rate:.1%}" if decided > 0 else ""
        lines = [
            f"=== {self.deck1_name} vs {self.deck2_name} ===",
            f"総試合数: {self.total_games}  有効試合数: {valid}",
            f"[{self.deck1_name}]  勝利: {self.deck1_wins}  勝率: {self.deck1_win_rate:.1%}  手札事故率: {self.deck1_accident_rate:.1%}",
            f"[{self.deck2_name}]  勝利: {self.deck2_wins}  勝率: {self.deck2_win_rate:.1%}  手札事故率: {self.deck2_accident_rate:.1%}",
            f"引き分け: {self.draws}",
        ]
        if fp_line:
            lines.append(fp_line)
        return "\n".join(lines) + "\n"


def simulate(deck1_path: str | Path, deck2_path: str | Path, n: int = 1000, seed: Optional[int] = None, randomize_first_player: bool = True) -> SimulationResult:
    rng = random.Random(seed)
    deck1_cards = load_deck_from_json(deck1_path)
    deck2_cards = load_deck_from_json(deck2_path)
    deck1_json = json.loads(Path(deck1_path).read_text(encoding="utf-8"))
    deck2_json = json.loads(Path(deck2_path).read_text(encoding="utf-8"))
    deck1_name = deck1_json.get("name", str(deck1_path))
    deck2_name = deck2_json.get("name", str(deck2_path))
    
    deck1_wins = deck2_wins = draws = 0
    deck1_accidents = deck2_accidents = games_with_accident = 0
    first_player_wins = second_player_wins = p1_first_count = 0

    for _ in range(n):
        p1 = Player(deck1_name, deepcopy(deck1_cards))
        p2 = Player(deck2_name, deepcopy(deck2_cards))
        game = Game(p1, p2, rng, randomize_first_player=randomize_first_player)
        
        # Setup returns (p1_accident, p2_accident)
        a1, a2 = game.setup()
        
        if a1: deck1_accidents += 1
        if a2: deck2_accidents += 1
        if a1 or a2:
            games_with_accident += 1
            # 事故が発生しても試合は続行し、勝率計算に含める（現行のplay()は事故後もセットアップ済みなのでそのまま続行可能）

        result = game.play()
        p1_went_first = (game._first_player is p1)
        if p1_went_first: p1_first_count += 1
        
        if result == "p1":
            deck1_wins += 1
            if p1_went_first: first_player_wins += 1
            else: second_player_wins += 1
        elif result == "p2":
            deck2_wins += 1
            if p1_went_first: second_player_wins += 1
            else: first_player_wins += 1
        else:
            draws += 1
            
    return SimulationResult(deck1_name, deck2_name, n, deck1_wins, deck2_wins, draws, deck1_accidents, deck2_accidents, games_with_accident, first_player_wins, second_player_wins, p1_first_count)
