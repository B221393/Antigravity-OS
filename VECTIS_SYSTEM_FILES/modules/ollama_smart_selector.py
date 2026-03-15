"""
Ollama Smart Model Selector
===========================
メモリ状況に応じて動的に最適なOllamaモデルを選択するモジュール。

使用例:
    from ollama_smart_selector import get_optimal_model, ask_ollama
    
    # 最適なモデルを自動選択
    model = get_optimal_model()
    
    # 質問を投げる
    response = ask_ollama("要約してください", model=model)
"""

import subprocess
import json
import psutil
from typing import Optional, Tuple, List
import requests

# モデル定義: (モデル名, 必要メモリGB, 性能スコア)
AVAILABLE_MODELS = [
    ("gemma:2b", 1.7, 60),        # 軽量・基本
    ("phi3:mini", 2.4, 70),       # バランス良
    ("qwen2.5:1.5b", 1.6, 65),    # 日本語強い
    ("llama3.2:1b", 1.3, 55),     # 最軽量
    ("llama3.2", 4.7, 85),        # 高性能（16GB+向け）
    ("gemma2:9b", 5.5, 90),       # 高品質（16GB+向け）
]

OLLAMA_API_URL = "http://localhost:11434"


def get_available_memory_gb() -> float:
    """利用可能なメモリをGB単位で取得"""
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024 ** 3)
    return available_gb


def get_installed_models() -> List[str]:
    """インストール済みのOllamaモデル一覧を取得"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        models = []
        for line in result.stdout.strip().split('\n')[1:]:  # ヘッダーをスキップ
            if line.strip():
                model_name = line.split()[0]
                models.append(model_name)
        return models
    except Exception as e:
        print(f"[WARN] モデル一覧取得に失敗: {e}")
        return []


def get_optimal_model(min_memory_buffer_gb: float = 2.0) -> Tuple[str, str]:
    """
    現在のメモリ状況から最適なモデルを選択
    
    Args:
        min_memory_buffer_gb: 最低限確保するメモリ余裕（GB）
    
    Returns:
        (モデル名, 選択理由)
    """
    available_gb = get_available_memory_gb()
    usable_gb = available_gb - min_memory_buffer_gb
    
    installed_models = get_installed_models()
    
    # 使用可能なモデルをフィルタリング（インストール済み & メモリ内）
    candidates = []
    for model_name, required_gb, score in AVAILABLE_MODELS:
        if model_name in installed_models and required_gb <= usable_gb:
            candidates.append((model_name, required_gb, score))
    
    if not candidates:
        # フォールバック: 最軽量のインストール済みモデル
        for model_name, required_gb, score in sorted(AVAILABLE_MODELS, key=lambda x: x[1]):
            if model_name in installed_models:
                return (model_name, f"⚠️ メモリ不足({available_gb:.1f}GB)だが{model_name}を使用")
        return ("gemma:2b", "❌ デフォルトモデルを試行（要インストール）")
    
    # 性能スコアが最も高いものを選択
    best = max(candidates, key=lambda x: x[2])
    reason = f"✅ {available_gb:.1f}GB空き → {best[0]} ({best[1]}GB) を選択"
    
    return (best[0], reason)


def ask_ollama(prompt: str, model: Optional[str] = None, timeout: int = 120) -> str:
    """
    Ollamaに質問を投げる（モデル自動選択対応）
    
    Args:
        prompt: 質問文
        model: 使用するモデル（Noneなら自動選択）
        timeout: タイムアウト秒数
    
    Returns:
        AIの回答
    """
    if model is None:
        model, reason = get_optimal_model()
        print(f"[Smart Selector] {reason}")
    
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 2048,  # メモリ節約のためコンテキスト制限
                }
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return "❌ Ollamaが起動していません。`ollama serve`を実行してください。"
    except Exception as e:
        return f"❌ エラー: {e}"


def ensure_model_installed(model: str = "gemma:2b") -> bool:
    """指定モデルがインストールされていなければインストール"""
    installed = get_installed_models()
    if model in installed:
        print(f"✅ {model} はインストール済み")
        return True
    
    print(f"⏳ {model} をインストール中...")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        print(f"✅ {model} のインストール完了")
        return True
    except Exception as e:
        print(f"❌ インストール失敗: {e}")
        return False


# === テスト用 ===
if __name__ == "__main__":
    print("=" * 50)
    print("🧠 Ollama Smart Selector テスト")
    print("=" * 50)
    
    # メモリ状況
    mem_gb = get_available_memory_gb()
    print(f"\n📊 利用可能メモリ: {mem_gb:.2f} GB")
    
    # インストール済みモデル
    models = get_installed_models()
    print(f"📦 インストール済みモデル: {models}")
    
    # 最適モデル選択
    model, reason = get_optimal_model()
    print(f"\n🎯 {reason}")
    
    # テスト実行
    print("\n📝 テスト1: 誤字脱字修正")
    result1 = ask_ollama("以下の誤字を修正: 「私わ学校に行きまsu」", model=model)
    print(f"   結果: {result1[:100]}...")
    
    print("\n📝 テスト2: 要約")
    result2 = ask_ollama(
        "Summarize in one sentence: Machine learning is a subset of AI that enables computers to learn from data.",
        model=model
    )
    print(f"   結果: {result2[:100]}...")
    
    print("\n✅ テスト完了！")
