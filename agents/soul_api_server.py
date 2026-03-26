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
    
    # 1. 外部脳（STRATEGIC_INTEL_LOG.md）への書き込み準備
    import datetime
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "STRATEGIC_INTEL_LOG.md")
    
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n### 📝 THOUGHT SYNC [{timestamp}]\n")
        f.write(f"- **INPUT**: {req.thought}\n")
        f.flush()

    task_description = (
        f"ユーザーの以下の抽象的な思考（魂）を処理してください。\n"
        f"思考: '{req.thought}'\n\n"
        f"1. この思考を具体化するための情報やヒントをGoogle検索してください。\n"
        f"2. そこから、思考を深めるための重要な気付き（Actionable Insights）を抜き出してください。\n"
        f"3. 最後に、必ず以下のJSONフォーマットのみを出力して終了してください: "
        f"{{\"title\": \"string\", \"core_philosophy\": \"string\", \"insights\": [\"string\"]}}"
    )

    # ... (AI処理) ...
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
    agent = Agent(task=task_description, llm=llm)
    
    history = await agent.run()
    
    try:
        final_output_str = history.final_result()
        final_output = json.loads(final_output_str) if isinstance(final_output_str, str) else final_output_str
        
        # 2. AIの気付きもログに追記
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"- **AI ANALYSIS**: {final_output.get('core_philosophy', 'N/A')}\n")
            insights = final_output.get('insights', [])
            for insight in insights:
                f.write(f"  - {insight}\n")
        
        return {"status": "success", "result": final_output}
    except Exception as e:
        # JSONパースエラーなどの場合でもテキストとして返す
        return {"status": "error", "result": str(history)}

class DebateRequest(BaseModel):
    thought: str

@app.post("/api/debate")
async def start_debate(req: DebateRequest):
    print(f"\n====================\n【MULTI-AGENT DEBATE】: {req.thought}\n====================")
    
    prompt = (
        f"以下のユーザーの考えについて、3人の異なる専門家として議論してください。\n"
        f"ユーザーの考え: '{req.thought}'\n\n"
        f"【登場人物】\n"
        f"1. ARCHITECT: 構造、効率、実現可能性を重視する。冷静で論理的。\n"
        f"2. CRITIC: あらゆる死角、リスク、倫理的問題を指摘する。鋭く批判的。\n"
        f"3. VISIONARY: 可能性、未来、夢を重視する。楽観的で情熱的。\n\n"
        f"彼らが互いに意見を戦わせ、最後に一つの「統合された気付き」を導き出してください。\n\n"
        f"出力形式（純粋なJSONのみ）:\n"
        f"{{\n"
        f"  \"architect\": \"文章\",\n"
        f"  \"critic\": \"文章\",\n"
        f"  \"visionary\": \"文章\",\n"
        f"  \"synthesis\": \"最終的な統合された答え\"\n"
        f"}}"
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
    
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.replace('```json', '').replace('```', '').strip()
        debate_result = json.loads(content)
        return {"status": "success", "debate": debate_result}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

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
