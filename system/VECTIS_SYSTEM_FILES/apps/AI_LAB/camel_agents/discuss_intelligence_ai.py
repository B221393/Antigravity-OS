"""
EGO Multi-Agent Discussion: Intelligence Gathering System
Two AI agents discuss and design the information collection architecture
"""
import os
from dotenv import load_dotenv
from colorama import Fore
import sys
sys.path.append(r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\modules")

# Load environment
load_dotenv(r"c:\Users\Yuto\Desktop\app\.env")

print(Fore.CYAN + "🤖 EGO Multi-Agent Discussion: Intelligence System Design" + Fore.RESET)

try:
    from unified_llm_client import ask_llm
    
    print(Fore.GREEN + "✅ LLM Client Ready\n" + Fore.RESET)
    
    # Define agent roles
    agents = {
        "AI_RESEARCHER": {
            "name": "AI Research Specialist",
            "role": "あなたは最先端のAI研究者で、情報収集・知識管理システムの専門家です。学術的で構造的なアプローチを好みます。",
            "icon": "🔬"
        },
        "SYSTEM_ARCHITECT": {
            "name": "System Architect",
            "role": "あなたは実践的なシステム設計者で、スケーラビリティとメンテナンス性を重視します。実装可能な具体案を提示します。",
            "icon": "🏗️"
        }
    }
    
    # Discussion topic
    topic = """
現在のEGOの情報収集システムについて、以下の観点で議論してください：

【現状】
- YouTube動画の要約収集
- ニュース記事の自動取得
- 就活情報の定期監視
- Deep Knowledge収集（30分間隔で本1章レベルの知識生成）

【課題】
1. Gemini APIのレート制限（429エラー）が頻発
2. Ollamaは文字数制限が厳しく、長文処理に不向き
3. 複数のコレクターが同時実行すると負荷が高い
4. 生成される知識の品質がばらつく

【目標】
- より安定した情報収集
- 高品質な知識ベース構築
- システムリソースの最適化

この状況をどう改善すべきか、具体的な提案を出してください。
"""
    
    print(Fore.YELLOW + f"📢 Discussion Topic:\n{topic}\n" + Fore.RESET)
    print(Fore.CYAN + "🚀 Starting Multi-Agent Discussion...\n" + Fore.RESET)
    
    conversation_history = []
    current_prompt = topic
    
    for turn in range(4):
        print(Fore.BLUE + f"\n{'='*60}\n Turn {turn + 1}\n{'='*60}" + Fore.RESET)
        
        # AI Researcher's turn
        researcher_prompt = f"{agents['AI_RESEARCHER']['role']}\n\n{current_prompt}\n\n簡潔に3-4つのポイントで答えてください。"
        print(Fore.MAGENTA + f"\n{agents['AI_RESEARCHER']['icon']} {agents['AI_RESEARCHER']['name']} is thinking..." + Fore.RESET)
        
        researcher_response = ask_llm(researcher_prompt)
        if researcher_response:
            print(Fore.MAGENTA + f"\n{agents['AI_RESEARCHER']['icon']} {agents['AI_RESEARCHER']['name']}:\n{researcher_response}\n" + Fore.RESET)
            conversation_history.append(f"Researcher: {researcher_response}")
        else:
            print(Fore.RED + "Researcher failed to respond" + Fore.RESET)
            break
        
        # System Architect responds
        architect_prompt = f"{agents['SYSTEM_ARCHITECT']['role']}\n\n研究者の提案:\n{researcher_response}\n\nこの提案に対する技術的な実装案とフィードバックを、3-4つのポイントで答えてください。"
        print(Fore.CYAN + f"\n{agents['SYSTEM_ARCHITECT']['icon']} {agents['SYSTEM_ARCHITECT']['name']} is thinking..." + Fore.RESET)
        
        architect_response = ask_llm(architect_prompt)
        if architect_response:
            print(Fore.CYAN + f"\n{agents['SYSTEM_ARCHITECT']['icon']} {agents['SYSTEM_ARCHITECT']['name']}:\n{architect_response}\n" + Fore.RESET)
            conversation_history.append(f"Architect: {architect_response}")
        else:
            print(Fore.RED + "Architect failed to respond" + Fore.RESET)
            break
        
        # Prepare next iteration
        current_prompt = f"前回の議論:\n研究者: {researcher_response}\n設計者: {architect_response}\n\nさらに深掘りして、次のステップを提案してください。"
    
    print(Fore.GREEN + "\n" + "="*60 + Fore.RESET)
    print(Fore.GREEN + "✅ Multi-Agent Discussion Complete!" + Fore.RESET)
    print(Fore.GREEN + "="*60 + "\n" + Fore.RESET)
    
    # Save discussion summary
    summary_path = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\AI_LAB\camel_agents\discussion_summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# EGO Intelligence System Design Discussion\n\n")
        f.write(f"## Topic\n{topic}\n\n")
        f.write("## Conversation History\n\n")
        for i, entry in enumerate(conversation_history, 1):
            f.write(f"### Turn {(i+1)//2}\n{entry}\n\n")
    
    print(Fore.YELLOW + f"📝 Discussion saved to: {summary_path}" + Fore.RESET)
    
except Exception as e:
    print(Fore.RED + f"💥 Error: {e}" + Fore.RESET)
    import traceback
    traceback.print_exc()
