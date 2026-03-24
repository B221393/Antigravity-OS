"""
EGO AUTONOMOUS AGENT (Ollama版)
24時間稼働・就活＆研究情報収集システム
ローカルLLM (Ollama) で要約機能付き
"""

import time
import os
import json
import requests
from datetime import datetime
from pathlib import Path

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Missing: pip install duckduckgo-search")
    exit(1)

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma:2b"

# Output directories
OUTPUT_DIR = Path(r"C:\Users\Yuto\clawd")
OUTPUT_DIR.mkdir(exist_ok=True)

JOB_EVENTS_FILE = OUTPUT_DIR / "job_events.md"
RESEARCH_FILE = OUTPUT_DIR / "research_notes.md"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def check_ollama():
    """Check if Ollama is running."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False

def ollama_generate(prompt, max_tokens=500):
    """Generate text using Ollama."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens}
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return None
    except Exception as e:
        log(f"Ollama error: {e}")
        return None

def search_web(query, max_results=5):
    """Search the web and return results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return results
    except Exception as e:
        log(f"Search error: {e}")
        return []

def collect_job_events(use_llm=True):
    """Collect job events from Mynavi."""
    log("🔍 Collecting job events from Mynavi...")
    
    queries = [
        "マイナビ2027 就活イベント セミナー",
        "マイナビ IT テクノロジー 説明会 2027",
        "就活イベント 2027卒 IT エンジニア"
    ]
    
    all_results = []
    for q in queries:
        results = search_web(q)
        for r in results:
            all_results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "body": r.get("body", "")[:150]
            })
    
    # Format raw results
    raw_text = "\n".join([
        f"- **{r['title']}**\n  {r['url']}\n  {r['body']}"
        for r in all_results
    ]) if all_results else "検索結果なし"
    
    # Summarize with Ollama
    summary = None
    if use_llm and all_results:
        log("🤖 Summarizing with Ollama...")
        prompt = f"""以下の就活イベント検索結果を日本語で簡潔にまとめてください：

{raw_text}

IT/テクノロジー業界を優先して、重要なイベントをリストアップしてください。"""
        summary = ollama_generate(prompt)
    
    final_content = summary if summary else raw_text
    
    # Append to file
    with open(JOB_EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n---\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} 収集\n")
        f.write(final_content)
    
    log(f"✅ Job events saved to {JOB_EVENTS_FILE}")

def collect_research(use_llm=True):
    """Collect AI/ML research notes."""
    log("🧠 Collecting AI/ML research...")
    
    queries = [
        "local LLM agent 2026",
        "autonomous AI agent",
        "Clawdbot AI assistant"
    ]
    
    all_results = []
    for q in queries:
        results = search_web(q)
        for r in results:
            all_results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "body": r.get("body", "")[:150]
            })
    
    raw_text = "\n".join([
        f"- **{r['title']}**\n  {r['url']}\n  {r['body']}"
        for r in all_results
    ]) if all_results else "検索結果なし"
    
    # Summarize with Ollama
    summary = None
    if use_llm and all_results:
        log("🤖 Summarizing with Ollama...")
        prompt = f"""以下のAI研究の検索結果から重要なトレンドを日本語で要約してください：

{raw_text}"""
        summary = ollama_generate(prompt)
    
    final_content = summary if summary else raw_text
    
    # Append to file
    with open(RESEARCH_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n---\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} 収集\n")
        f.write(final_content)
    
    log(f"✅ Research saved to {RESEARCH_FILE}")

def main():
    print("=" * 60)
    print("  EGO AUTONOMOUS AGENT SYSTEM (Ollama Edition)")
    print("  Mode: 24/7 Job Hunt + Deep Research")
    print(f"  LLM: {OLLAMA_MODEL} (Local)")
    print("  Interval: 30 minutes")
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    
    # Check Ollama
    use_llm = check_ollama()
    if use_llm:
        log(f"✅ Ollama connected: {OLLAMA_MODEL}")
    else:
        log("⚠️ Ollama not running. Starting in search-only mode.")
        log("   To enable LLM: run 'ollama serve' in another terminal.")
    
    cycle = 1
    while True:
        log(f"=== CYCLE {cycle} START ===")
        
        try:
            # Re-check Ollama each cycle in case it was started later
            use_llm = check_ollama()
            
            collect_job_events(use_llm)
            collect_research(use_llm)
        except Exception as e:
            log(f"❌ Cycle error: {e}")
        
        log(f"=== CYCLE {cycle} COMPLETE ===")
        log("Sleeping for 30 minutes...")
        
        cycle += 1
        time.sleep(1800)

if __name__ == "__main__":
    main()
