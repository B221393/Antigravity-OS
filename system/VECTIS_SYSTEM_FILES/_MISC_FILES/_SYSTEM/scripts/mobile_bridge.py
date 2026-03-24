import os
import json
import queue
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="Vectis Mobile Bridge")

# Command Queue to share with Orchestrator
command_queue = "command_queue.json"

# --- CORS SETUP ---
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev (Dashboard JS -> Bridge)
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STATIC MOUNTS ---
# Mount Scheduler App
try:
    if os.path.exists("apps/scheduler"):
        app.mount("/schedule", StaticFiles(directory="apps/scheduler", html=True), name="scheduler")
    else:
        print("Warning: apps/scheduler directory not found. Static mount skipped.")
except Exception as e:
    print(f"Mount Error: {e}")

# --- DIARY SERVICE INTEGRATION ---
import sys
# Ensure we can find apps/diary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
try:
    from apps.diary.diary_service import DiaryService
    # Initialize Global Service
    diary_service = DiaryService("apps/diary/data/entries.json")
except ImportError:
    print("Warning: DiaryService import failed.")
    diary_service = None

class DiaryEntryReq(BaseModel):
    title: str = "Mobile/Web Entry"
    content: str
    clarity: int = 50

@app.post("/v1/diary")
async def add_diary_api(entry: DiaryEntryReq):
    if not diary_service:
        return {"status": "error", "message": "Service unavailable"}
    
    # Save
    diary_service.add_entry(entry.title, entry.content, entry.clarity, entry_type="api_log")
    return {"status": "ok", "message": "Saved to Neural Log."}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vectis Mobile</title>
        <style>
            body { 
                background: #0f0f14; color: #fff; font-family: 'Inter', sans-serif; 
                display: flex; flex-direction: column; align-items: center; 
                justify-content: center; height: 100vh; margin: 0; 
                overflow: hidden;
            }
            .container { text-align: center; width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; }
            h1 { font-size: 1.5rem; color: #00ffbe; letter-spacing: 2px; margin-bottom: 5px; }
            #status { font-size: 0.8rem; color: #666; margin-bottom: 1rem; }
            
            input[type="text"] {
                width: 100%; padding: 15px; background: #1a1a24; border: 1px solid #333;
                color: #fff; border-radius: 8px; box-sizing: border-box; font-size: 1rem;
            }
            
            .btn {
                width: 100%; padding: 15px; border: none;
                border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s;
                text-decoration: none; display: inline-block; box-sizing: border-box;
                font-size: 1rem;
            }
            .btn:active { transform: scale(0.98); opacity: 0.8; }
            
            .btn-primary { background: #00ffbe; color: #000; }
            .btn-voice { background: #ff4b2b; color: #fff; }
            .btn-scheduler { background: linear-gradient(45deg, #00C9FF, #92FE9D); color: #000; }
            
            #log { 
                margin-top: 1rem; text-align: left; font-size: 0.7rem; color: #888;
                max-height: 100px; overflow-y: auto; padding: 10px; background: #1a1a24;
                border-radius: 4px; border: 1px solid #222;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div>
                <h1>VECTIS BRIDGE</h1>
                <div id="status">System: Waiting for command...</div>
            </div>

            <!-- SCHEDULER LINK -->
            <a href="/schedule/" class="btn btn-scheduler">📅 OPEN SCHEDULE APP</a>
            
            <div style="width:100%; height:1px; background:#333; margin: 5px 0;"></div>

            <input type="text" id="cmdInput" placeholder="Enter command...">
            <button class="btn btn-primary" onclick="sendCommand()">EXECUTE</button>
            <button class="btn btn-voice" id="voiceBtn">VOICE INPUT</button>
            
            <div id="log">--- Session Log ---</div>
        </div>

        <script>
            const statusDiv = document.getElementById('status');
            const logDiv = document.getElementById('log');

            async function sendCommand(override = null) {
                const cmd = override || document.getElementById('cmdInput').value;
                if (!cmd) return;
                
                statusDiv.innerText = "System: Sending...";
                logDiv.innerHTML += `<div>> ${cmd}</div>`;
                
                try {
                    const response = await fetch('/command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `command=${encodeURIComponent(cmd)}`
                    });
                    const data = await response.json();
                    statusDiv.innerText = "System: Command Queued.";
                    document.getElementById('cmdInput').value = "";
                } catch (e) {
                    statusDiv.innerText = "Error: Connection failed.";
                }
            }

            // Web Speech API Integration
            const voiceBtn = document.getElementById('voiceBtn');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.lang = 'ja-JP';
                
                voiceBtn.onclick = () => {
                    recognition.start();
                    statusDiv.innerText = "System: Listening...";
                    voiceBtn.innerText = "LISTENING...";
                };

                recognition.onresult = (event) => {
                    const speechToText = event.results[0][0].transcript;
                    statusDiv.innerText = "System: Processing Speech...";
                    voiceBtn.innerText = "VOICE INPUT";
                    sendCommand(speechToText);
                };

                recognition.onerror = () => {
                    statusDiv.innerText = "Error: Voice recognition failed.";
                    voiceBtn.innerText = "VOICE INPUT";
                };
            } else {
                voiceBtn.style.display = "none";
            }
        </script>
    </body>
    </html>
    """

# --- Pydantic Models ---
class CommandRequest(BaseModel):
    command: str

class ChatRequest(BaseModel):
    message: str

# --- Helper Functions ---
def _save_log(entry: dict):
    """Save log entry to JSON file securely."""
    # Ensure directory exists
    LOG_FILE = "activity_log.md" # Keeping consistent with other parts if needed, or json? 
    # Original code had json logic but variable was missing.
    # Let's fix this to be safe.
    LOG_JSON = "apps/mobile/logs.json"
    os.makedirs(os.path.dirname(LOG_JSON), exist_ok=True)
    
    logs = []
    if os.path.exists(LOG_JSON):
        try:
            with open(LOG_JSON, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception: 
            logs = []
            
    logs.insert(0, entry)
    
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def _get_agent():
    """Factory to get Agent instance."""
    import sys
    # Add root to sys.path if needed
    root_dir = os.path.abspath(os.path.dirname(__file__))
    if root_dir not in sys.path:
        sys.path.append(root_dir)
        
    from modules.researcher import ResearchAgent
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY missing")
        
    return ResearchAgent(gemini_key, groq_key)

# --- Endpoints ---

@app.post("/chat")
async def chat_gemini(message: str = Form(...)):
    """Chat with Gemini and auto-log the interaction."""
    import uuid
    from datetime import datetime

    try:
        # 1. Get Agent
        agent = _get_agent()
        
        # 2. Call LLM
        response_text = agent._call_llm(f"You are a helpful assistant. Reply in Japanese.\nUser: {message}")
        
        # 3. Create Log
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "raw_text": f"USER: {message}\nAI: {response_text}",
            "summary": f"[Auto-Chat] {message[:20]}...", 
            "type": "chat_client"
        }
        
        # 4. Save Log
        _save_log(log_entry)
            
        return {"status": "success", "reply": response_text}
        
    except Exception as e:
        print(f"Chat Error: {e}") # Log to stdout
        return {"status": "error", "message": str(e)}

@app.post("/command")
async def post_command(command: str = Form(...)):
    """Add a command to the queue file."""
    try:
        data = {"command": command, "timestamp": str(os.times())}
        with open(command_queue, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return {"status": "success", "queued": command}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Get Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    print("\n" + "="*50)
    print(f" VECTIS MOBILE BRIDGE IS RUNNING")
    print("="*50)
    print(f" [IMPORTANT] To connect from smartphone, enter this URL:")
    print(f" >> http://{local_ip}:8000")
    print(" (Note: 'localhost' will NOT work on your phone!)")
    print("="*50 + "\n")

    # Allow external access
    uvicorn.run(app, host="0.0.0.0", port=8000)
