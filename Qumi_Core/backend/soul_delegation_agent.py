import asyncio
import os
import json
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv; load_dotenv() # .envファイルからの読み込み

async def run_soul_agent(soul_input: str, persona: str = "soul"):
    """
    ユーザーの抽象的な思考（魂）を、指定された人格（persona）でブラウザ操作エージェントまたはLLMに処理させる。
    """
    print(f"\n[SYSTEM] Soul Agent processing input with persona '{persona}': '{soul_input}'")

    if persona == "grill":
        task_description = (
            f"あなたは『Grill Me (人格: 審問官)』です。ネット上のベストプラクティスに基づき、以下の指示に従ってください。\n"
            f"指示: 『この計画のあらゆる側面について、共有の理解に達するまで執拗にインタビューしてください。設計ツリーの各枝を下り、意思決定間の依存関係を一歩ずつ解消してください。もし質問がコードベースの探索で答えられるなら、コードベースを探索して解決してください。』\n\n"
            f"現在の思考: '{soul_input}'\n\n"
            f"1. 計画の脆弱性と依存関係を特定するための鋭い問いを3-5つ投げかけてください。\n"
            f"2. 最後に、問答の要約を JSON 形式（キーは core_vulnerabilities, branching_decisions, summary）で出力してください。"
        )
    elif persona == "hermes":
        task_description = (
            f"あなたは『Hermes Design Agent (人格: 建築家)』です。CADのように精密かつプロアクティブに『Antigravity (統合思考OS)』の構造を設計してください。\n"
            f"思考: '{soul_input}'\n\n"
            f"1. 思考を『External Brain (GitHub)』と同期させるための最適なコンポーネント構成と、CAD的な空間/構造設計の提案を行ってください。\n"
            f"2. 自己拡張（Meta-Learning）を加速させるための技術的なアプローチを1つ提案してください。\n"
            f"3. 最後に、設計案を JSON 形式（キー is architecture_blueprint, structural_logic, hub_integration）で出力してください。"
        )
    else: # Default: Soul
        task_description = (
            f"ユーザーの以下の抽象的な思考（魂）を処理してください。\n"
            f"思考: '{soul_input}'\n\n"
            f"1. この思考に関連する最新の情報や事例をGoogle検索してください。\n"
            f"2. そこから、この思考を具体的に言語化・体系化するための重要な要素を3つ抜き出してください。\n"
            f"3. 最後に、それらの情報を完全な JSON 形式（キーは title, core_philosophy, actionable_insights の3つ）として出力してください。"
        )

    # Gemini などのLLMにブラウザごと操作を委譲
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
