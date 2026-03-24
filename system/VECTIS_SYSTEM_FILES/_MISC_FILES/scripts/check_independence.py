"""
VECTIS OS - Independence Check
===============================
システムの独立性（APIキー不要・オフライン動作）を確認
"""

import sys
import os
import json
import requests
from pathlib import Path

# Windows console encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_ollama():
    """Ollamaの稼働状況確認"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            return True, [m.get("name", "unknown") for m in models]
        return False, []
    except:
        return False, []

def check_config():
    """設定ファイルで独立性確認"""
    config_path = Path(__file__).parent.parent / "config" / "llm_config.json"
    
    if not config_path.exists():
        return {
            "config_exists": False,
            "default_is_ollama": False,
            "external_disabled": False,
            "auto_fallback_disabled": False
        }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # チェック項目
        default_provider = config.get("default_provider", "")
        providers = config.get("providers", {})
        auto_fallback = config.get("auto_fallback", True)
        
        # 外部APIが無効化されているか
        gemini_disabled = not providers.get("gemini", {}).get("enabled", False)
        groq_disabled = not providers.get("groq", {}).get("enabled", False)
        
        return {
            "config_exists": True,
            "default_is_ollama": default_provider == "ollama",
            "ollama_enabled": providers.get("ollama", {}).get("enabled", False),
            "external_disabled": gemini_disabled and groq_disabled,
            "auto_fallback_disabled": not auto_fallback,
            "config": config
        }
    except:
        return {
            "config_exists": False,
            "default_is_ollama": False,
            "external_disabled": False,
            "auto_fallback_disabled": False
        }

def check_env_vars():
    """APIキーの環境変数確認"""
    api_keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
    
    has_keys = any(v is not None for v in api_keys.values())
    return has_keys, api_keys

def main():
    """独立性チェック実行"""
    print("=" * 60)
    print("  VECTIS INDEPENDENCE CHECK")
    print("=" * 60)
    print()
    
    # 1. Ollama確認
    print("[CHECK 1] Ollama Service")
    ollama_running, models = check_ollama()
    
    if ollama_running:
        print("  [OK] Ollama: Running")
        if models:
            print(f"  [OK] Models: {', '.join(models[:3])}")
            if len(models) > 3:
                print(f"       ... and {len(models) - 3} more")
        else:
            print("  [WARN] No models installed")
            print("        Run: ollama pull llama3.2")
    else:
        print("  [X] Ollama: Not running")
        print("      Start with: ollama serve")
    print()
    
    # 2. 設定ファイル確認
    print("[CHECK 2] Configuration")
    config_status = check_config()
    
    if not config_status["config_exists"]:
        print("  [X] Config file not found")
        print("      Expected: config/llm_config.json")
    else:
        if config_status["default_is_ollama"]:
            print("  [OK] Default provider: Ollama")
        else:
            print("  [WARN] Default provider is not Ollama")
            print("        Change default_provider to 'ollama'")
        
        if config_status["ollama_enabled"]:
            print("  [OK] Ollama: Enabled")
        else:
            print("  [X] Ollama: Disabled")
        
        if config_status["external_disabled"]:
            print("  [OK] External APIs: All disabled")
        else:
            print("  [WARN] External APIs still enabled")
            print("        Disable Gemini and Groq in config")
        
        if config_status["auto_fallback_disabled"]:
            print("  [OK] Auto-fallback: Disabled")
        else:
            print("  [WARN] Auto-fallback enabled")
            print("        Set auto_fallback to false")
    print()
    
    # 3. 環境変数確認
    print("[CHECK 3] API Keys")
    has_keys, api_keys = check_env_vars()
    
    if has_keys:
        print("  [INFO] API keys detected:")
        for key, value in api_keys.items():
            if value:
                print(f"        {key}: Set (not needed for independence)")
    else:
        print("  [OK] No API keys found (perfect for independence!)")
    print()
    
    # 4. 総合判定
    print("=" * 60)
    print("  INDEPENDENCE STATUS")
    print("=" * 60)
    print()
    
    independence_score = 0
    max_score = 4
    
    if ollama_running and models:
        independence_score += 1
        print("[OK] Ollama ready with models")
    else:
        print("[X] Ollama not ready")
    
    if config_status.get("default_is_ollama"):
        independence_score += 1
        print("[OK] Default provider is Ollama")
    else:
        print("[X] Default provider not Ollama")
    
    if config_status.get("external_disabled"):
        independence_score += 1
        print("[OK] External APIs disabled")
    else:
        print("[X] External APIs still enabled")
    
    if config_status.get("auto_fallback_disabled"):
        independence_score += 1
        print("[OK] Auto-fallback disabled")
    else:
        print("[X] Auto-fallback enabled")
    
    print()
    print("=" * 60)
    
    if independence_score == max_score:
        print("  100% INDEPENDENT! [OK]")
        print("  No API keys needed, fully offline capable!")
    elif independence_score >= 2:
        print(f"  {int(independence_score/max_score*100)}% Independent [PARTIAL]")
        print("  Almost there! Check warnings above.")
    else:
        print("  DEPENDENT [X]")
        print("  Follow INDEPENDENCE_GUIDE.md for setup.")
    
    print("=" * 60)
    print()
    
    if independence_score < max_score:
        print("Next steps:")
        print("  1. Read: docs/INDEPENDENCE_GUIDE.md")
        print("  2. Install Ollama if needed")
        print("  3. Edit: config/llm_config.json")
        print("  4. Run this check again")
        print()
    else:
        print("You're fully independent! Enjoy offline AI! [OK]")
        print()

if __name__ == "__main__":
    main()
