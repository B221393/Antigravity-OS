import asyncio
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# React Native Webからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SoulRequest(BaseModel):
    thought: str

@app.post("/api/soul")
async def delegate_soul(req: SoulRequest):
    print(f"\n====================\n【RECEIVED SOUL】: {req.thought}\n====================")
    
    task_description = (
        f"ユーザーの以下の抽象的な思考（魂）を処理してください。\n"
        f"思考: '{req.thought}'\n\n"
        f"1. この思考を具体化するための情報やヒントをGoogle検索してください。\n"
        f"2. そこから、思考を深めるための重要な気付き（Actionable Insights）を抜き出してください。\n"
        f"3. 最後に、必ず以下のJSONフォーマットのみを出力して終了してください: "
        f"{{\"title\": \"string\", \"core_philosophy\": \"string\", \"insights\": [\"string\"]}}"
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
    agent = Agent(task=task_description, llm=llm)
    
    # ブラウザが裏で立ち上がり、自動で検索して思考を拡張する
    history = await agent.run()
    
    # browser-useエージェントの最終結果を取得
    try:
        final_output = history.final_result()
        print(f"\n【AGENT SUCCESS】: {final_output}\n")
        return {"status": "success", "result": final_output}
    except Exception as e:
        print(f"\n【AGENT ERROR】: {e}\n")
        return {"status": "error", "result": str(history)}

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print("=" * 60)
    print(" 🚀 [ 統合思考OS ] - EXTERNAL BRAIN API SERVER (PORT:8000)")
    print("=" * 60)
    uvicorn.run("soul_api_server:app", host="0.0.0.0", port=8000, reload=True)
