import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# .envの読み込み
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / "_config" / ".env")

class LLMAnalyzer:
    """Gemini APIを使用して論文を要約するクラス"""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def analyze(self, text: str, title: str) -> str:
        """論文テキストを解析し、構造化された要約を返す"""
        
        prompt = f"""
あなたは先進的なAI研究パートナー「Antigravity」です。
提供された論文テキスト（タイトル: {title}）を読み、以下の厳密なフォーマットに従って日本語で要約してください。

# Knowledge Digest: {title}

[Skill activated: skill-paper-digest]

## 1. Background (Context & Problem)
> この研究が解決しようとしている問題は何ですか？なぜ重要なのですか？

## 2. Methods (Approach & Implementation)
> どのような手法、アルゴリズム、実装技術が使われていますか？

## 3. Novelty (Differentiation)
> 既存手法と何が決定的に異なりますか？何が「新しい」のですか？

## 4. Critical View (Limitations & Critique)
> この研究の限界や欠点は何ですか？どのような未解決課題がありますか？

## 5. Lateral Links (Connections)
> この知見は、「統合思考OS (VECTIS)」や個人の生産性向上にどう貢献しますか？

---
論文テキスト:
{text[:30000]}  # トークン節約とコンテキスト制限のため、必要に応じて調整
"""
        
        response = self.model.generate_content(prompt)
        return response.text

if __name__ == "__main__":
    # 単体テスト (実際のテキストがない場合はモック)
    analyzer = LLMAnalyzer()
    print("Analyzer initialized.")
