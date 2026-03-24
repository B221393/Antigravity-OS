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

class NovelRequest(BaseModel):
    title: str
    synopsis: str
    context: str

@app.post("/api/soul")
async def delegate_soul(req: SoulRequest):
    # ... (既存のコード) ...
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
    
    history = await agent.run()
    
    try:
        final_output = history.final_result()
        return {"status": "success", "result": final_output}
    except Exception as e:
        return {"status": "error", "result": str(history)}

@app.post("/api/novel")
async def generate_novel_branches(req: NovelRequest):
    print(f"\n====================\n【NOVEL EXPANSION REQUEST】: {req.title}\n====================")
    
    prompt = (
        f"あなたは創作支援AIです。以下の小説の続きとして、3つの異なる展開を提案してください。\n\n"
        f"タイトル: {req.title}\n"
        f"あらすじ: {req.synopsis}\n"
        f"現在の本文末尾: \n\"\"\"{req.context[-500:]}\"\"\"\n\n"
        f"以下の3つのタイプで続きを提案してください：\n"
        f"1. ACTION: 状況が急変する、あるいは物理的な動きがある展開。\n"
        f"2. DRAMA: 登場人物の感情や人間関係を深掘りする展開。\n"
        f"3. LOGIC: 世界観の謎が解ける、あるいは論理的な解決に向かう展開。\n\n"
        f"出力は必ず以下の純粋なJSONフォーマットのみで行ってください：\n"
        f"[\n"
        f"  {{\"type\": \"ACTION\", \"label\": \"急展開\", \"text\": \"続きの文章...\"}},\n"
        f"  {{\"type\": \"DRAMA\", \"label\": \"心理描写\", \"text\": \"続きの文章...\"}},\n"
        f"  {{\"type\": \"LOGIC\", \"label\": \"理論的解決\", \"text\": \"続きの文章...\"}}\n"
        f"]"
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
    
    try:
        # browser-useを使わずに直接LLMに聞く（高速化のため）
        response = await llm.ainvoke(prompt)
        # JSONの抽出（念のためマークダウンを剥がす）
        content = response.content.replace('```json', '').replace('```', '').strip()
        branches = json.loads(content)
        return {"status": "success", "branches": branches}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print("=" * 60)
    print(" 🚀 [ 統合思考OS ] - EXTERNAL BRAIN API SERVER (PORT:8000)")
    print("=" * 60)
    uvicorn.run("soul_api_server:app", host="0.0.0.0", port=8000, reload=True)
