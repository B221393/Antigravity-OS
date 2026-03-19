"""
数当てゲーム (Number Guessing Game)
====================================
コンピュータが 1〜100 の範囲でランダムな整数を決め、
プレイヤーがその数を当てるゲームです。

遊び方:
  python number_guessing_game.py          # 通常モード (1〜100)
  python number_guessing_game.py --easy   # かんたんモード (1〜50)
  python number_guessing_game.py --hard   # むずかしいモード (1〜200)

特徴:
  - 試行回数のカウントと最高スコア（セッション内）の管理
  - 「もっと大きい」「もっと小さい」のヒント
  - 制限試行回数を超えるとゲームオーバー
  - 複数回プレイに対応
"""

from __future__ import annotations

import random
import sys
import time
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# 定数 / Constants
# ---------------------------------------------------------------------------

DIFFICULTIES: dict[str, dict[str, str | int]] = {
    "easy":   {"label": "かんたん",       "low": 1, "high": 50,  "max_tries": 10},
    "normal": {"label": "ふつう",         "low": 1, "high": 100, "max_tries": 7},
    "hard":   {"label": "むずかしい",     "low": 1, "high": 200, "max_tries": 7},
}


# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------

@dataclass
class GameConfig:
    """1 ゲームの設定を保持します。"""
    label: str
    low: int
    high: int
    max_tries: int


@dataclass
class SessionStats:
    """セッション全体の統計を管理します。"""
    games_played: int = 0
    games_won: int = 0
    best_tries: Optional[int] = None
    total_tries: int = 0
    history: list[tuple[int, bool]] = field(default_factory=list)

    def record(self, tries: int, won: bool) -> None:
        """1 ゲームの結果を記録します。"""
        self.games_played += 1
        self.total_tries += tries
        self.history.append((tries, won))
        if won:
            self.games_won += 1
            if self.best_tries is None or tries < self.best_tries:
                self.best_tries = tries

    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.games_won / self.games_played * 100

    def summary(self) -> str:
        lines = [
            "=" * 40,
            "  セッション結果",
            "=" * 40,
            f"  プレイ回数  : {self.games_played} 回",
            f"  クリア回数  : {self.games_won} 回",
            f"  勝率        : {self.win_rate:.1f}%",
        ]
        if self.best_tries is not None:
            lines.append(f"  最少試行数  : {self.best_tries} 回")
        if self.games_played > 0:
            avg = self.total_tries / self.games_played
            lines.append(f"  平均試行数  : {avg:.1f} 回")
        lines.append("=" * 40)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 入力ユーティリティ
# ---------------------------------------------------------------------------

def _read_int(prompt: str, low: int, high: int) -> int:
    """整数入力を受け付け、範囲外や非整数は再入力を促します。"""
    while True:
        raw = input(prompt).strip()
        if raw.lower() in ("q", "quit", "exit"):
            raise SystemExit("\nゲームを終了します。またね！")
        try:
            value = int(raw)
        except ValueError:
            print(f"  ⚠  整数を入力してください。（{low}〜{high}）")
            continue
        if not (low <= value <= high):
            print(f"  ⚠  {low}〜{high} の範囲で入力してください。")
            continue
        return value


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    """y/n の質問に答えてもらいます。"""
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        raw = input(prompt + suffix).strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  y か n で答えてください。")


# ---------------------------------------------------------------------------
# ゲームロジック
# ---------------------------------------------------------------------------

def _hint(guess: int, answer: int) -> str:
    """ヒントメッセージを返します。"""
    diff = abs(guess - answer)
    if guess < answer:
        direction = "📈  もっと大きい数です！"
    else:
        direction = "📉  もっと小さい数です！"

    if diff <= 5:
        closeness = "🔥 めちゃくちゃ近い！"
    elif diff <= 15:
        closeness = "😮 かなり近い！"
    elif diff <= 30:
        closeness = "🙂 まあまあ近い"
    else:
        closeness = "❄️  まだ遠い…"

    return f"  {direction}  （{closeness}）"


def play_game(cfg: GameConfig) -> tuple[int, bool]:
    """
    1 ゲームをプレイします。

    Returns
    -------
    tries : int
        使用した試行回数
    won : bool
        正解できたかどうか
    """
    answer = random.randint(cfg.low, cfg.high)
    tries = 0
    won = False

    print(f"\n{'='*40}")
    print(f"  難易度: {cfg.label}")
    print(f"  範囲  : {cfg.low} 〜 {cfg.high}")
    print(f"  制限  : {cfg.max_tries} 回以内に当ててね！")
    print(f"{'='*40}")
    print("  （'q' で終了）\n")

    start_time = time.time()

    while tries < cfg.max_tries:
        remaining = cfg.max_tries - tries
        prompt = f"  [{remaining} 回残り] 数を入力: "
        guess = _read_int(prompt, cfg.low, cfg.high)
        tries += 1

        if guess == answer:
            elapsed = time.time() - start_time
            print(f"\n  🎉 正解！ {answer} です！")
            print(f"     {tries} 回で当てました。 ({elapsed:.1f} 秒)")
            won = True
            break
        else:
            print(_hint(guess, answer))

    if not won:
        print(f"\n  😢 ゲームオーバー。正解は {answer} でした。")

    return tries, won


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------

def _select_difficulty(argv: list[str]) -> GameConfig:
    """コマンドライン引数から難易度を決定します。"""
    for flag, key in [("--easy", "easy"), ("--hard", "hard"), ("--normal", "normal")]:
        if flag in argv:
            d = DIFFICULTIES[key]
            return GameConfig(**d)

    # 引数なし → インタラクティブに選択
    print("\n難易度を選んでください:")
    keys = list(DIFFICULTIES.keys())
    for i, key in enumerate(keys, 1):
        d = DIFFICULTIES[key]
        print(f"  {i}. {d['label']} ({d['low']}〜{d['high']}, {d['max_tries']}回以内)")
    choice = _read_int("  番号を入力: ", 1, len(keys))
    d = DIFFICULTIES[keys[choice - 1]]
    return GameConfig(**d)


def main() -> None:
    """ゲームのメインループ。"""
    print("\n" + "=" * 40)
    print("    🎯  数当てゲームへようこそ！  🎯")
    print("=" * 40)

    cfg = _select_difficulty(sys.argv[1:])
    stats = SessionStats()

    while True:
        tries, won = play_game(cfg)
        stats.record(tries, won)

        play_again = _ask_yes_no("\nもう一度プレイしますか？")
        if not play_again:
            break
        # 連続プレイでは毎回同じ難易度を使用
        print("\n同じ難易度で続けます。")

    print(stats.summary())
    print("\nプレイしてくれてありがとう！またね 👋\n")


if __name__ == "__main__":
    main()
