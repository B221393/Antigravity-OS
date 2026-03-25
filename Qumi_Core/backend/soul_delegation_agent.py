import asyncio
import os
import json
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv; load_dotenv() # .envファイルからの読み込み

async def run_soul_agent(soul_input: str):
    """
    ユーザーの抽象的な思考（魂）をブラウザ操作エージェントで構造化（JSON化）する。
    """
    print(f"\n[SYSTEM] Soul Agent processing input: '{soul_input}'")

    task_description = (
        f"ユーザーの以下の抽象的な思考（魂）を処理してください。\n"
        f"思考: '{soul_input}'\n\n"
        f"1. この思考に関連する最新の情報や事例をGoogle検索してください。\n"
        f"2. そこから、この思考を具体的に言語化・体系化するための重要な要素を3つ抜き出してください。\n"
        f"3. 最後に、それらの情報を完全な JSON 形式（キーは title, core_philosophy, actionable_insights の3つ）として出力してください。"
    )

    # Gemini などのLLMにブラウザごと操作を委譲（魂をJSONにするプロセス）
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
    
    agent = Agent(
        task=task_description,
        llm=llm
    )
    
    # エージェント実行
    result = await agent.run()
    return result

async def main():
    print("="*60)
    print(" [ 統合思考OS ] - EXTERNAL BRAIN DELEGATION ENGINE (CLI Layer)")
    print("="*60)
    
    soul_input = input("\n[あなた] 思考（魂のフワッとしたアイディア）を入力: ")
    result = await run_soul_agent(soul_input)
    
    print("\n" + "="*60)
    print(" 【魂の構造化完了（JSON）】")
    print("="*60)
    print(result)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
