"""
CAMEL-AI Multi-Agent Demo for EGO
Using Gemini API (most reliable)
"""
import os
import sys
from dotenv import load_dotenv
from colorama import Fore

# Force UTF-8 stdout for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv(r"c:\Users\Yuto\Desktop\app\.env")

gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    print(Fore.RED + "❌ GEMINI_API_KEY not found" + Fore.RESET)
    exit(1)

print(Fore.CYAN + "🐫 EGO Multi-Agent System (Gemini Backend)" + Fore.RESET)
print(Fore.GREEN + f"✅ API Key Loaded" + Fore.RESET)

try:
    from google import generativeai as genai
    genai.configure(api_key=gemini_key)
    
    # Create two agents with different system instructions
    designer = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="You are a creative UI/UX designer specializing in futuristic, sci-fi interfaces. Be concise."
    )
    
    architect = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="You are a pragmatic software architect. Evaluate ideas for technical feasibility. Be concise."
    )
    
    print(Fore.YELLOW + "\n📢 Task: Design EGO OS Dashboard\n" + Fore.RESET)
    print(Fore.CYAN + "🚀 Starting Multi-Agent Dialogue...\n" + Fore.RESET)
    
    # Initial prompt
    current_message = "Design a futuristic dashboard UI for EGO OS. What are your initial ideas?"
    
    for turn in range(3):
        print(Fore.BLUE + f"\n--- Turn {turn + 1} ---" + Fore.RESET)
        
        # Designer's turn
        designer_response = designer.generate_content(current_message)
        designer_text = designer_response.text
        print(Fore.MAGENTA + f"🎨 UI Designer:\n{designer_text}\n" + Fore.RESET)
        
        # Architect responds to designer
        architect_prompt = f"The UI Designer proposed: {designer_text}\n\nProvide technical feedback and suggestions."
        architect_response = architect.generate_content(architect_prompt)
        architect_text = architect_response.text
        print(Fore.CYAN + f"🏗️ Architect:\n{architect_text}\n" + Fore.RESET)
        
        # Update message for next iteration
        current_message = f"Based on the architect's feedback: {architect_text}\n\nRefine your design."
    
    print(Fore.GREEN + "\n✅ Multi-Agent Session Complete!" + Fore.RESET)
    
except Exception as e:
    print(Fore.RED + f"💥 Error: {e}" + Fore.RESET)
    import traceback
    traceback.print_exc()
