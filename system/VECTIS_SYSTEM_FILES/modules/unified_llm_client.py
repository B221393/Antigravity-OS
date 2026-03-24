"""
Unified LLM Client with Fallback Chain
=======================================
Gemini API → Groq API → Ollama の順でフォールバック

優先順位:
1. Gemini Pro (最高品質・無料枠大)
2. Groq (高速・無料枠中)
3. Ollama (ローカル・完全無料)
"""

import os
import time
import subprocess
from typing import Optional
from dotenv import load_dotenv

# Project root .env loading
# In VECTIS system, .env is usually at c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\.env
ENV_PATH = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\.env"
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    load_dotenv() # Fallback to standard loading

# === API Keys (環境変数から取得) ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# === Gemini ===
try:
    from google import genai
    from google.genai import types
    if GEMINI_API_KEY:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        HAS_GEMINI = True
        print("[LLM] ✅ Gemini Pro ready")
    else:
        HAS_GEMINI = False
        print("[LLM] ⚠️ Gemini API key not found")
except Exception as e:
    HAS_GEMINI = False
    print(f"[LLM] ⚠️ Gemini not available: {e}")

# === Groq ===
try:
    from groq import Groq
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        HAS_GROQ = True
        print("[LLM] ✅ Groq ready")
    else:
        HAS_GROQ = False
        print("[LLM] ⚠️ Groq API key not found")
except Exception as e:
    HAS_GROQ = False
    print(f"[LLM] ⚠️ Groq not available: {e}")

# === Ollama ===
try:
    from modules.ollama_smart_selector import ask_ollama as ollama_ask
    HAS_OLLAMA = True
    print("[LLM] ✅ Ollama ready (fallback)")
except Exception as e:
    HAS_OLLAMA = False
    print(f"[LLM] ❌ Ollama not available: {e}")

# === Anthropic (Claude) ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
try:
    import anthropic
    if ANTHROPIC_API_KEY:
        claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        HAS_CLAUDE = True
        print("[LLM] ✅ Claude (Anthropic) ready")
    else:
        HAS_CLAUDE = False
        print("[LLM] ⚠️ Claude API key not found")
except Exception as e:
    HAS_CLAUDE = False
    print(f"[LLM] ⚠️ Anthropic library not available: {e}")


def ask_gemini_cli(prompt: str) -> Optional[str]:
    """Gemini CLI (npm package) via subprocess"""
    try:
        # quote the prompt for shell safety (basic)
        # Using powershell escaping or just passing list to subprocess
        # Using 'gemini prompt "message"' format
        cmd = ["gemini", "prompt", prompt]
        
        # Run command (with timeout)
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            timeout=120,
            shell=True # Required for npm globals on windows sometimes
        )
        
        if result.returncode == 0:
            return filter_output(result.stdout.strip())
        else:
            print(f"[LLM] ⚠️ Gemini CLI error: {result.stderr}")
            return None
    except Exception as e:
        print(f"[LLM] ⚠️ Gemini CLI execution failed: {e}")
        return None

def ask_llm(prompt: str, max_retries: int = 2, timeout: int = 120) -> Optional[str]:
    """
    統合LLM呼び出し（フォールバックチェーン）
    
    Args:
        prompt: プロンプト
        max_retries: 各APIの最大リトライ回数
        timeout: タイムアウト秒数
    
    Returns:
        AIの応答（失敗時はNone）
    """
    
    # === 0. Gemini CLI (Disabled to prevent hanging) ===
    # print(f"[LLM] Trying Gemini CLI...")
    # cli_result = ask_gemini_cli(prompt)
    # if cli_result:
    #     print(f"[LLM] ✅ Gemini CLI success ({len(cli_result)} chars)")
    #     return cli_result
    
    # === 1. Gemini Pro (API Key) ===
    if HAS_GEMINI:
        # Retry with exponential backoff strategy
        wait_time = 5
        for attempt in range(max_retries):
            try:
                print(f"[LLM] Trying Gemini Pro (attempt {attempt + 1})...")
                
                # Model selection strategy: Flash 2.0 -> Pro 1.5 -> Flash 1.5
                # Using 'latest' aliases to avoid 404s on older versions
                try:
                    # Tier 1: Gemini 2.0 Flash (Fastest/Newest)
                    response = gemini_client.models.generate_content(
                        model='gemini-2.0-flash', 
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=8192)
                    )
                except Exception as e:
                    if "429" in str(e): raise e # Propagate 429 to outer loop
                    
                    # Tier 2: Gemini 1.5 Pro (High Intelligence)
                    print(f"[LLM] ⚠️ Gemini 2.0 failed. Falling back to 1.5 Pro...")
                    try:
                        response = gemini_client.models.generate_content(
                            model='gemini-1.5-pro-latest',
                            contents=prompt,
                            config=types.GenerateContentConfig(temperature=0.7)
                        )
                    except Exception as e2:
                        if "429" in str(e2): raise e2 # Propagate 429
                        
                        # Tier 3: Gemini 1.5 Flash (Economy/Backup)
                        print(f"[LLM] ⚠️ Gemini 1.5 Pro failed. Falling back to 1.5 Flash...")
                        response = gemini_client.models.generate_content(
                            model='gemini-1.5-flash-latest',
                            contents=prompt,
                            config=types.GenerateContentConfig(temperature=0.7)
                        )

                result = filter_output(response.text)
                print(f"[LLM] ✅ Gemini success ({len(result)} chars)")
                return result

            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    # Smart 429 Handling: Parsing "retry in X s"
                    import re
                    match = re.search(r"retry in (\d+(\.\d+)?)s", error_str)
                    if match:
                        wait = float(match.group(1)) + 2.0 # Add small buffer
                        print(f"[LLM] ⚠️ Rate Limit (429). Server requested wait: {wait:.1f}s")
                    else:
                        wait = wait_time * (2 ** attempt) # Exponential backoff
                        print(f"[LLM] ⚠️ Rate Limit (429). Backoff wait: {wait}s")
                    
                    time.sleep(wait)
                else:
                    print(f"[LLM] ⚠️ Gemini Error: {e}")
                    # If it's a 404 or other non-retriable error, maybe we shouldn't retry?
                    if "404" in error_str:
                        print("[LLM] ❌ Model not found (404). Checking next provider...")
                        break
                
                if attempt < max_retries - 1:
                    time.sleep(1)
    
    # === 2. Groq (次点) ===
    if HAS_GROQ:
        for attempt in range(max_retries):
            try:
                print(f"[LLM] Trying Groq (attempt {attempt + 1})...")
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",  # 最新の高性能モデル
                    temperature=0.7,
                    max_tokens=8192,
                )
                result = filter_output(chat_completion.choices[0].message.content)
                print(f"[LLM] ✅ Groq success ({len(result)} chars)")
                return result
            except Exception as e:
                print(f"[LLM] ⚠️ Groq failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
    
    # === 2.5. Claude (Anthropic) ===
    if HAS_CLAUDE:
        for attempt in range(max_retries):
            try:
                print(f"[LLM] Trying Claude 3.5 Sonnet (attempt {attempt + 1})...")
                message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = message.content[0].text
                print(f"[LLM] ✅ Claude success ({len(result)} chars)")
                return result
            except Exception as e:
                print(f"[LLM] ⚠️ Claude failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

    # === 3. Ollama (最終フォールバック) ===
    if HAS_OLLAMA:
        for attempt in range(max_retries):
            try:
                print(f"[LLM] Trying Ollama (attempt {attempt + 1})...")
                result = ollama_ask(prompt, timeout=timeout)
                if result and not result.startswith("❌"):
                    print(f"[LLM] ✅ Ollama success ({len(result)} chars)")
                    return result
                else:
                    raise Exception(result or "Empty response")
            except Exception as e:
                print(f"[LLM] ⚠️ Ollama failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
    
    # === すべて失敗 ===
    print("[LLM] ❌ All LLM providers failed")
    return None

def filter_output(text: str) -> str:
    """禁止ワードを置換するフィルター"""
    if not text: return text
    # VECTISの名前を出さないように徹底
    text = text.replace("VECTIS", "独自の知能基盤")
    text = text.replace("vectis", "独自の知能基盤")
    return text

def ask_llm_high_quality(prompt: str, max_retries: int = 1) -> Optional[str]:
    """高性能モデルのみを使用し、フォールバック（Ollama）を行わない"""
    # Gemini / Groq / Claude のみを試行
    if HAS_GEMINI:
        try:
            print("[LLM-HQ] Using Gemini Pro...")
            response = gemini_client.models.generate_content(
                model='gemini-2.0-flash', contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            return filter_output(response.text)
        except: pass
        
    if HAS_GROQ:
        try:
            print("[LLM-HQ] Using Groq...")
            chat = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            return filter_output(chat.choices[0].message.content)
        except: pass
        
    if HAS_CLAUDE:
        try:
            print("[LLM-HQ] Using Claude...")
            message = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return filter_output(message.content[0].text)
        except: pass

    print("[LLM-HQ] ⚠️ High quality providers unavailable/exhausted.")
    return None


def get_available_providers() -> list:
    """利用可能なLLMプロバイダーのリストを返す"""
    providers = []
    if HAS_GEMINI:
        providers.append("Gemini Pro")
    if HAS_GROQ:
        providers.append("Groq")
    if HAS_OLLAMA:
        providers.append("Ollama")
    return providers


# === テスト用 ===
if __name__ == "__main__":
    print("=" * 50)
    print("🧠 Unified LLM Client Test")
    print("=" * 50)
    
    providers = get_available_providers()
    print(f"\n📊 Available providers: {', '.join(providers)}")
    
    if not providers:
        print("\n❌ No LLM providers available!")
        exit(1)
    
    print("\n📝 Test: Simple question")
    result = ask_llm("日本の首都はどこですか？1文で答えてください。")
    
    if result:
        print(f"\n✅ Success!")
        print(f"Response: {result[:200]}...")
    else:
        print("\n❌ All providers failed")
