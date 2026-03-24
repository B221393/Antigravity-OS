import os
import requests
import json
import textwrap

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # Rustのコードに合わせた
KNOWLEDGE_FILES = [
    r"STRATEGIC_INTEL_LOG.md",
    r"User_Profile\User_Profile.md",
    r"User_Profile\REFINED_INTERVIEW_ANSWERS.md"
]

def load_knowledge():
    """Load knowledge from markdown files."""
    knowledge = ""
    for file_path in KNOWLEDGE_FILES:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                knowledge += f"
--- SOURCE: {file_path} ---
{content}
"
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return knowledge

def ask_local_brain(query, context):
    """Ask Ollama using knowledge as context."""
    system_prompt = f"""
    You are 'Antigravity', the core intelligence of the User's Integrated Thinking OS.
    Your mission is to support the User (Optimizer/Aggressive Visionary) to achieve his 'Historical Ambition'.
    
    ### CONTEXT (USER'S EXTERNAL BRAIN):
    {context}
    
    ### INSTRUCTION:
    - Use the context above to answer.
    - Be professional, logical, and concise.
    - NEVER use real names or specific university names in your response (Abstractions only).
    - If the answer is not in the context, use your general intelligence but keep the User's persona.
    - Respond in Japanese.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}

User Question: {query}

Antigravity's Answer:",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "Error: No response.")
    except Exception as e:
        return f"Error contacting Ollama: {e}"

def main():
    print("--- [Antigravity Local Brain Core] ---")
    print("Loading Knowledge (STRATEGIC_INTEL_LOG.md, User_Profile)...")
    context = load_knowledge()
    
    while True:
        query = input("
[USER] > ")
        if query.lower() in ["exit", "quit", "bye"]:
            break
        
        print("
[Antigravity] (Thinking...)
")
        answer = ask_local_brain(query, context)
        
        # Format for terminal
        print(textwrap.fill(answer, width=80))

if __name__ == "__main__":
    main()
