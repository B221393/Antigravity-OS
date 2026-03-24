"""
CAMEL-AI Session: EGO MAPPER Improvement
Using UnifiedLLM (Ollama/Cohere/Gemini)
"""
import sys
import os

# Add parent path to allow importing EGO modules
# Add parent path (Root 'app' directory)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))) # Reach 'app' folder

from EGO_SYSTEM_FILES.modules.unified_llm import UnifiedLLM

def run_camel_session():
    print("🐫 Starting CAMEL Session: EGO MAPPER Improvement")
    
    # Initialize agents (Both use UnifiedLLM router)
    llm = UnifiedLLM() 
    
    # Roles
    visualizer_role = "Visualization Expert (D3.js Specialist)"
    ux_role = "UX Researcher"
    
    # Context
    topic = "Improving 'EGO MAPPER' (2D Knowledge Graph Visualizer)."
    current_state = """
    Current Implementation:
    - D3.js tree layout
    - Simple circles for nodes
    - Genre-based color classes
    - Basic zoom/pan
    - Hover effect
    """
    
    print(f"Topic: {topic}")
    
    # Initial Prompt
    msg = f"""
    {current_state}
    
    As a {ux_role}, propose 3 high-impact features to make this tool more useful for exploring a large knowledge base.
    """
    
    history = []
    
    # Simulation Loop (2 Turns)
    for i in range(2):
        print(f"\n--- Turn {i+1} ---")
        
        # 1. UX Researcher speaks
        print(f"👤 {ux_role} thinking...")
        prompt_ux = f"Role: {ux_role}\nTask: {topic}\nContext: {msg}\n\nSpeak as the {ux_role}."
        res_ux = llm.generate(prompt_ux)
        print(f"👤 {ux_role}: {res_ux[:300]}...\n")
        history.append(f"{ux_role}: {res_ux}")
        
        # 2. Visualizer responds
        print(f"🎨 {visualizer_role} thinking...")
        prompt_vis = f"""
        Role: {visualizer_role}
        Task: {topic}
        Context: The {ux_role} suggested: {res_ux}
        
        Propose technical D3.js implementation details for these suggestions. Be specific.
        """
        res_vis = llm.generate(prompt_vis)
        print(f"🎨 {visualizer_role}: {res_vis[:300]}...\n")
        history.append(f"{visualizer_role}: {res_vis}")
        
        # Update msg for next turn
        msg = f"Based on the technical proposal: {res_vis}\n\nRefine the user experience further."

    # Save Log
    with open("mapper_improvement_plan.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(history))
    print("✅ Session saved to mapper_improvement_plan.txt")

if __name__ == "__main__":
    run_camel_session()
