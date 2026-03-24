
import os
from colorama import Fore

def run_camel_demo():
    print(Fore.CYAN + "🐫 CAMEL-AI Multi-Agent System Initializing..." + Fore.RESET)
    
    # Check for API Keys
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not groq_key and not openai_key:
        print(Fore.RED + "エラー: APIキーが見つかりません。.envファイルに GROQ_API_KEY または OPENAI_API_KEY を設定してください。" + Fore.RESET)
        return

    try:
        from camel.agents import ChatAgent
        from camel.configs import ChatGPTConfig
        from camel.messages import BaseMessage
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType
        
        print(Fore.GREEN + "✅ CAMEL-AI Libraries Loaded." + Fore.RESET)
        
        # Simple Role-Playing Demo
        print("\n--- タスク: Pythonでスネークゲームを作る ---\n")
        
        # Note: This is a placeholder for the actual CAMEL implementation.
        # Since CAMEL requires specific model setup which can be complex to auto-configure blindly,
        # we will set up the structure and ask the user to confirm the model usage.
        
        print("CAMEL-AIの「Role Playing」モードを開始する準備ができました。")
        print("アシスタント役とユーザー役のAIが協力してタスクを解決します。")
        print("設定ファイル: camel_config.py (作成予定)")
        
    except ImportError:
        print(Fore.RED + "CAMEL-AIがインストールされていません。'pip install camel-ai' を実行してください。" + Fore.RESET)
    except Exception as e:
        print(Fore.RED + f"初期化エラー: {e}" + Fore.RESET)

if __name__ == "__main__":
    run_camel_demo()
