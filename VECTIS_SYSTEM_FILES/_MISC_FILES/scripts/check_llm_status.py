"""
VECTIS OS - LLM Status Checker
==============================
全LLMプロバイダーの状態を確認するユーティリティ
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.unified_llm import create_llm_client
from modules.keyboard_layout import get_layout_manager
import json

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text):
    """Print section header"""
    print(f"\n[*] {text}")
    print("-" * 70)

def check_ollama_models():
    """Check available Ollama models"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            return [m.get("name", "unknown") for m in models]
    except:
        pass
    return []

def main():
    print_header("VECTIS OS - LLM & Configuration Status")
    
    # 1. Check LLM providers
    print_section("LLM Provider Status")
    
    try:
        llm = create_llm_client()
        
        # Check each provider
        status = llm.check_provider_status()
        for provider_name, is_available in status.items():
            icon = "[OK]" if is_available else "[X]"
            status_text = "Available" if is_available else "Unavailable"
            print(f"  {icon} {provider_name.upper():15} {status_text}")
            
            # Show Ollama models if available
            if provider_name == "ollama" and is_available:
                models = check_ollama_models()
                if models:
                    print(f"      Models: {', '.join(models)}")
        
        # Show default provider
        default = llm.config.get_default_provider()
        print(f"\n  [>] Default Provider: {default.upper()}")
        
        # Show auto-fallback status
        auto_fallback = llm.config.config.get("features", {}).get("auto_fallback", True)
        fallback_icon = "[OK]" if auto_fallback else "[X]"
        print(f"  {fallback_icon} Auto-Fallback: {'Enabled' if auto_fallback else 'Disabled'}")
        
    except Exception as e:
        print(f"  [X] Error checking LLM status: {e}")
    
    # 2. Check keyboard layout
    print_section("Keyboard Layout")
    
    try:
        layout_manager = get_layout_manager()
        info = layout_manager.get_layout_info()
        
        current = info['current_layout'].upper()
        is_onishi = info['is_onishi'] == 'True'
        icon = "[JP]" if is_onishi else "[US]"
        
        print(f"  {icon} Current Layout: {current}")
        if is_onishi:
            print(f"      Mapping Size: {info['mapping_size']} keys")
        
    except Exception as e:
        print(f"  [X] Error checking keyboard layout: {e}")
    
    # 3. Check TOEIC priority
    print_section("Application Priorities")
    
    try:
        config_path = Path(__file__).parent.parent / "config" / "llm_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        toeic_priority = config.get("features", {}).get("toeic_priority", "medium")
        
        priority_icons = {
            "high": "[HIGH]",
            "medium": "[MED]",
            "low": "[LOW]",
            "disabled": "[OFF]"
        }
        
        icon = priority_icons.get(toeic_priority, "[?]")
        print(f"  {icon} TOEIC Priority: {toeic_priority.upper()}")
        
    except Exception as e:
        print(f"  [X] Error checking priorities: {e}")
    
    # 4. Quick test
    print_section("Quick Connection Test")
    
    try:
        llm = create_llm_client()
        test_prompt = "Say 'OK' if you can read this."
        
        print("  [TEST] Testing generation...")
        response = llm.generate(test_prompt, allow_fallback=True)
        
        print(f"  [OK] Response received: {response[:50]}...")
        
        # Show which provider was used
        stats = llm.get_stats()
        if stats['by_provider']:
            used_provider = list(stats['by_provider'].keys())[0]
            print(f"  [AI] Provider used: {used_provider.upper()}")
        
    except Exception as e:
        print(f"  [X] Test failed: {e}")
        print(f"\n  [!] Tips:")
        print(f"     - If Ollama fails: Run 'ollama serve' in terminal")
        print(f"     - If Gemini fails: Check GEMINI_API_KEY environment variable")
        print(f"     - Enable auto-fallback in config for redundancy")
    
    # 5. Configuration file location
    print_section("Configuration")
    
    config_path = Path(__file__).parent.parent / "config" / "llm_config.json"
    print(f"  [FILE] Config File: {config_path}")
    print(f"  {'[OK]' if config_path.exists() else '[X]'} File exists: {config_path.exists()}")
    
    if config_path.exists():
        size = config_path.stat().st_size
        print(f"  [INFO] File size: {size} bytes")
    
    # 6. Recommendations
    print_section("Recommendations")
    
    try:
        llm = create_llm_client()
        status = llm.check_provider_status()
        
        # Check if any provider is available
        if not any(status.values()):
            print("  [!] No providers available!")
            print("     -> Install Ollama: https://ollama.com/download")
            print("     -> Or set GEMINI_API_KEY environment variable")
        
        # Check if Ollama is available but not default
        elif status.get("ollama", False) and llm.config.get_default_provider() != "ollama":
            print("  [!] Ollama is available - consider making it default for offline use")
            print("     -> Edit config/llm_config.json: 'default_provider': 'ollama'")
        
        # Check if only API providers
        elif not status.get("ollama", False):
            print("  [!] Consider installing Ollama for offline capability")
            print("     -> No rate limits")
            print("     -> Works offline")
            print("     -> Free forever")
        
        else:
            print("  [OK] Configuration looks good!")
            if llm.config.config.get("features", {}).get("auto_fallback", True):
                print("  [OK] Auto-fallback enabled - resilient to API failures")
        
    except Exception as e:
        print(f"  [X] Error generating recommendations: {e}")
    
    print("\n" + "=" * 70)
    print()

if __name__ == "__main__":
    main()
