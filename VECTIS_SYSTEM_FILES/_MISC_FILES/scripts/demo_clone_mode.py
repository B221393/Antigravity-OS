import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.persona import PersonaAgent
from modules.gemini_client import GenerativeModel

# Load Env
load_dotenv()

def run_demo():
    print("🤖 初始化: 分身エージェント (Clone Agent)...")
    agent = PersonaAgent()
    
    print("\n📚 記憶の読み込み中...")
    logs = agent.load_chat_logs()
    print(f"   => {len(logs)} 件の会話ログを発見")
    if logs:
        print(f"   => 最新ログ: {logs[0].get('summary')}")
    
    print("\n🧬 人格プロンプト生成中...")
    prompt = agent.get_persona_prompt()
    print(f"   => プロンプトサイズ: {len(prompt)}文字")
    
    print("\n📝 執筆開始: テーマ『自己PR』...")
    
    # Use unified Gemini client
    model = GenerativeModel('gemini-2.0-flash-exp')
    
    final_prompt = f"""
    {prompt}
    
    【指令】
    私の分身として、以下のテーマでES（400文字）を書いてください。
    特に、直近の会話ログにある「リーダーシップ論」の視点を強く反映させてください。
    
    テーマ: 学生時代に力を入れたこと（自己PR）
    """
    
    print("   => Gemini 2.0 に送信中...")
    response = model.generate_content(final_prompt)
    
    print("\n" + "="*50)
    print("🧞‍♂️ 分身(Clone)の回答")
    print("="*50)
    print(response.text)
    print("="*50)

if __name__ == "__main__":
    run_demo()
