import os
import asyncio
import tempfile
import whisper
import subprocess
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from soul_delegation_agent import main as soul_agent_main

def auto_git_sync(message: str = "Auto-Sync: Thought Chunk"):
    """GitHub への自動同期（External Brain Sync）"""
    try:
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", message], capture_output=True)
        # ネットワークの状態によっては失敗する可能性があるが、バックグラウンド実行を想定
        subprocess.Popen(["git", "push"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[SYSTEM] Git Sync Triggered: {message}")
    except Exception as e:
        print(f"[WARNING] Git Sync failed: {e}")

app = FastAPI(title="Qumi Integrated OS Backend")

# Initialize local Whisper model (Hybrid approach: Local STT + Cloud LLM)
# Use 'base' for better speed/quality balance on Windows
whisper_model = whisper.load_model("base")

# Enable CORS for the PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SoulInput(BaseModel):
    thought: str
    persona: str = "soul"

@app.get("/")
async def root():
    return {"status": "online", "system": "Qumi Integrated OS"}

@app.post("/delegate")
async def delegate_thought(item: SoulInput):
    """構造化エージェントへの委譲（テキストベース・人格指定可能）"""
    try:
        from soul_delegation_agent import run_soul_agent
        result = await run_soul_agent(item.thought, persona=item.persona)
        # 思考が構造化されたら GitHub に自動同期（External Brain Sync）
        auto_git_sync(f"Sync ({item.persona}): {item.thought[:20]}...")
        return {"result": result}
    except Exception as e:
        print(f"[ERROR] Delegation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def process_voice_input(file: UploadFile = File(...), persona: str = "soul"):
    """音声入力プロセッサ: Whisper -> User Persona Routing -> MetaClaw/Agent"""
    try:
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Whisperで文字起こし (Local Hybrid)
        print(f"[SYSTEM] Transcribing audio with Whisper...")
        transcription = whisper_model.transcribe(tmp_path)
        text = transcription.get("text", "").strip()
        os.unlink(tmp_path) # クリーンアップ

        if not text:
            return {"error": "No speech detected"}

        print(f"[SYSTEM] Transcription: '{text}' (Persona: {persona})")

        # 指定された人格に委譲して構造化
        from soul_delegation_agent import run_soul_agent
        result = await run_soul_agent(text, persona=persona)

        # 思考が構造化されたら GitHub に自動同期（External Brain Sync）
        auto_git_sync(f"Voice Sync ({persona}): {text[:20]}...")

        return {
            "transcription": text,
            "structured_result": result,
            "persona": persona
        }
    except Exception as e:
        print(f"[ERROR] Voice Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def proxy_chat(request: Request):
    # Proxy to MetaClaw (default port 30000)
    METACLAW_URL = "http://127.0.0.1:30000/v1/chat/completions"
    body = await request.json()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(METACLAW_URL, json=body, timeout=60.0)
            return response.json()
        except Exception as e:
            # Fallback if MetaClaw is not running?
            return {"error": "MetaClaw proxy unreachable", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
