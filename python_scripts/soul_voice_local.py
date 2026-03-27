import os
import sounddevice as sd
import numpy as np
import whisper
import requests
import json
import time
from datetime import datetime

# --- SETTINGS ---
# LINE Credentials from USER
LINE_CHANNEL_ACCESS_TOKEN = "639f7be2e10e82d7957ed45ab9bdeeff" # User provided secret
LINE_USER_ID = "U01e4b9da6cbe8b4b64e6503e39ad1514"

# Local Paths
VAULT_PATH = r"c:\Users\Yuto\Desktop\app\logs\ASSET_VAULT.md"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Models
WHISPER_MODEL = "base"
GEMMA_MODEL = "gemma:2b"
SAMPLE_RATE = 16000

def record_audio(duration=6, fs=SAMPLE_RATE):
    print(f"\n[RECORDING] {duration}秒間、あなたの『魂（思考）』を聴いています...")
    # Whisper expects float32 Mono at 16kHz
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("[DONE] 録音完了。")
    return recording.flatten()

def transcribe_whisper(audio_data):
    print("[SYSTEM] Whisperで解析中...")
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_data)
    return result["text"].strip()

def structure_with_gemma(text):
    print(f"[SYSTEM] Gemma ({GEMMA_MODEL}) で多次元構造化中...")
    prompt = f"""
    あなたは『Antigravity（統合思考OS）』の構造化エンジンです。
    以下の断片的な思考を、将来の自分にとって価値ある『資産（Asset）』として整理してください。
    
    思考: "{text}"
    
    以下の形式(JSON)で出力してください:
    - title: 思考のタイトル
    - core_philosophy: 本質的な思想(100文字以内)
    - action_item: 具体的なネクストアクション
    - asset_value: この思考の資産的価値
    """
    
    payload = {
        "model": GEMMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return json.loads(response.json()["response"])
    except Exception as e:
        print(f"[ERROR] Gemma integration failed: {e}")
        return {"title": "Error", "core_philosophy": text, "action_item": "N/A", "asset_value": "N/A"}

def speak_with_voicevox(text):
    print("[SYSTEM] VOICEVOXでフィードバック生成中...")
    # placeholder for actual VOICEVOX integration logic
    print(f"[VOICEVOX говорит]: {text[:30]}...")

def archive_to_vault(asset_json):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""
### {timestamp}: {asset_json.get('title')}
- **Core Philosophy**: {asset_json.get('core_philosophy')}
- **Action Item**: {asset_json.get('action_item')}
- **Asset Value**: {asset_json.get('asset_value')}

---
"""
    with open(VAULT_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[SUCCESS] {VAULT_PATH} に資産を永久保存しました。")

def main():
    try:
        audio = record_audio(duration=6) # 6秒
        text = transcribe_whisper(audio)
        if not text:
            print("音声が検出されませんでした。")
            return
            
        print(f"\n[YOU]: {text}")
        asset = structure_with_gemma(text)
        print(f"\n[ASSET]: {json.dumps(asset, indent=2, ensure_ascii=False)}")
        
        archive_to_vault(asset)
        speak_with_voicevox(asset.get("title", "資産化完了"))
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
