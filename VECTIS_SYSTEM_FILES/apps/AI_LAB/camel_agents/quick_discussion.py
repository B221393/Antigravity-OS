"""
AI Discussion: EGO Intelligence System Improvement
"""
from colorama import Fore
import os
from dotenv import load_dotenv

# Load API key
load_dotenv(r"c:\Users\Yuto\Desktop\app\.env")
gemini_key = os.getenv("GEMINI_API_KEY")

if not gemini_key:
    print(Fore.RED + "❌ GEMINI_API_KEY not found" + Fore.RESET)
    exit(1)

print(Fore.CYAN + "\n🤖 EGO Intelligence System - AI Discussion\n" + Fore.RESET)

from google import generativeai as genai
genai.configure(api_key=gemini_key)

model = genai.GenerativeModel('gemini-1.5-flash')

# Research Specialist's Analysis
print(Fore.YELLOW + "🔬 AI Research Specialist analyzing...\n" + Fore.RESET)
researcher_prompt = """あなたは最先端のAI研究者です。

【EGOの情報収集システムの課題】
1. Gemini API のレート制限（429エラー）が頻発
2. Ollamaは文字数制限が厳しく、長文処理に不向き
3. 複数コレクターの同時実行で負荷が高い
4. 生成知識の品質がばらつく

この状況を改善するための**3つの具体的提案**を述べてください。簡潔に。"""

try:
    researcher_response = model.generate_content(researcher_prompt)
    researcher_text = researcher_response.text
    print(Fore.MAGENTA + f"💡 Research Specialist:\n{researcher_text}\n" + Fore.RESET)
except Exception as e:
    print(Fore.RED + f"Error: {e}" + Fore.RESET)
    exit(1)

# System Architect's Implementation Plan
print(Fore.YELLOW + "🏗️ System Architect evaluating...\n" + Fore.RESET)
architect_prompt = f"""あなたは実践的なシステム設計者です。

研究者の提案:
{researcher_text}

この提案を**EGOに実装する具体的な方法**を3つのステップで述べてください。技術的に。"""

try:
    architect_response = model.generate_content(architect_prompt)
    architect_text = architect_response.text
    print(Fore.CYAN + f"🔧 System Architect:\n{architect_text}\n" + Fore.RESET)
except Exception as e:
    print(Fore.RED + f"Error: {e}" + Fore.RESET)
    exit(1)

print(Fore.GREEN + "✅ Discussion Complete!\n" + Fore.RESET)

# Save
output_file = r"c:\Users\Yuto\Desktop\app\intelligence_ai_discussion.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("=== EGO Intelligence System - AI Discussion ===\n\n")
    f.write("🔬 AI Research Specialist:\n")
    f.write(researcher_text + "\n\n")
    f.write("="*60 + "\n\n")
    f.write("🏗️ System Architect:\n")
    f.write(architect_text + "\n")

print(Fore.YELLOW + f"📝 Saved to: {output_file}" + Fore.RESET)
