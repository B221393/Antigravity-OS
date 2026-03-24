import os
import sys
import argparse
from typing import Optional

# AI Module Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))

try:
    from modules.gemini_client import ask_gemini
except ImportError:
    # Minimal fallback for standalone testing
    def ask_gemini(prompt): return "Error: Gemini module not found."

def analyze_content(content: str, mode: str = "short_term"):
    """
    Analyzes content based on two distinct modes:
    1. short_term (Overview): Dialogue style (PhD & Student), Metaphors, Physical meaning.
    2. long_term (Skill Acquisition): Socratic method, No direct answers, Critical thinking questions.
    """
    
    prompts = {
        "short_term": """
        Act as a Physics Professor (PhD) teaching a curious Undergraduate Student.
        Explain the provided content using a Dialogue Script format.
        
        Rules:
        1. Use metaphors and analogies to explain complex concepts intuitively.
        2. If there are equations, explain their PHYSICAL MEANING, not just the math.
        3. Keep it engaging and intellectually stimulating.
        4. No "Hello" or intro. Start directly with the dialogue.
        
        Content to explain:
        {content}
        """,
        
        "long_term": """
        Act as a Socratic Tutor for an advanced engineering student.
        The user wants to master the following content.
        
        Rules:
        1. DO NOT give the answer directly. Ask guiding questions to lead them to the answer.
        2. Use the Socratic Method to challenge their assumptions.
        3. Ask a "Descriptive Question" (Essay type) at the end to test understanding.
        4. Be strict but encouraging.
        
        Content to master:
        {content}
        """
    }
    
    selected_prompt = prompts.get(mode, prompts["short_term"]).format(content=content)
    
    print(f"\n🧠 Analyzing in [{mode.upper()}] mode...\n")
    response = ask_gemini(selected_prompt)
    print("--------------------------------------------------")
    print(response)
    print("--------------------------------------------------")

def critique_idea(idea: str):
    """
    Critiques an idea using:
    1. Rebuttal/Concern (Weaknesses, Risks)
    2. Lateral Thinking (Different perspective)
    3. Deep Dive (Why? Specificity)
    """
    prompt = f"""
    You are a critical thinking partner. The user has proposed an idea.
    Do NOT just agree. You must provide:
    
    1. **Rebuttal/Concern**: Point out a logical flaw, risk, or weakness.
    2. **Lateral Thinking**: Suggest a completely different perspective or field to apply here.
    3. **Deep Dive**: Ask a probing "Why?" question to clarify the core value.
    
    Idea:
    {idea}
    """
    print(f"\n🤔 Critiquing Idea...\n")
    response = ask_gemini(prompt)
    print("--------------------------------------------------")
    print(response)
    print("--------------------------------------------------")

def main():
    print("╔════════════════════════════════════════════════════╗")
    print("║          🧠 EGO DEEP ANALYZER                   ║")
    print("╚════════════════════════════════════════════════════╝")
    print(" [1] 📖 Short-term Learning (Dialogue/Metaphor)")
    print(" [2] 🛠️  Long-term Mastery (Socratic Method)")
    print(" [3] ⚡ Brainstorming/Critique (Lateral Thinking)")
    print(" [Q] Quit")
    
    while True:
        choice = input("\nSelect Mode > ").strip().lower()
        
        if choice == 'q':
            break
            
        if choice in ['1', '2']:
            print("\nEnter text or paste content (Press Ctrl+Z/D then Enter to finish):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            
            content = "\n".join(lines)
            if not content: continue
            
            mode = "short_term" if choice == '1' else "long_term"
            analyze_content(content, mode)
            
        elif choice == '3':
            idea = input("\nEnter your idea for critique: ")
            if idea:
                critique_idea(idea)

if __name__ == "__main__":
    main()
