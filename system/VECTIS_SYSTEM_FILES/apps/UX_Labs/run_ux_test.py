
import time
from mock_app import MockApp
from user_agent import UXAgent
from report_generator import ReportGenerator

def run_simulation():
    print("🚀 Initializing Universal UX Architect v1.1...")
    print("==============================================")
    
    app = MockApp()
    reporter = ReportGenerator()
    
    # Initialize Agents
    agents = [
        UXAgent("GRANDMOTHER"),
        UXAgent("UI_DESIGNER"),
        UXAgent("HACKER"),
        UXAgent("GEN_Z") # New!
    ]
    
    # Simulation Loop
    for agent in agents:
        print(f"\n👤 [Agent: {agent.persona}] starts using Twutter...")
        
        # Reset App for each user
        app = MockApp() 
        state = app.get_state()
        
        step = 0
        max_steps = 5 # Increased steps for navigation
        
        while step < max_steps:
            print(f"   👁️ Viewing Screen: {state.get('title')}")
            
            # 1. Critique
            review = agent.critique(state)
            if review:
                print(f"      💭 Internal Voice: \"{review}\"")
                reporter.log_issue(agent.persona, state['screen_id'], review)
            
            # 2. Act
            decision = agent.act(state)
            print(f"      👉 Action: {decision['action']} on {decision['target']} ({decision['reason']})")
            reporter.log_interaction(agent.persona, state['screen_id'], decision['action'], decision['reason'])
            
            # 3. Simulate Interaction
            if decision['action'] != "wait":
                feedback = app.interact(decision['action'], decision['target'])
                print(f"      💻 App Response: {feedback}")
                
                if "Error" in feedback:
                    reporter.log_issue(agent.persona, state['screen_id'], f"System Crash: {feedback}", "Critical")
                
                if "App Closed" in feedback:
                    print("      ❌ User Left the App.")
                    break
            else:
                print("      💤 Waiting...")
                
            state = app.get_state()
            step += 1
            time.sleep(0.3) 

    print("\n==============================================")
    print("✅ UX Simulation Complete.")
    
    report_path = reporter.generate_markdown()
    print(f"📄 Report Saved: {report_path}")

if __name__ == "__main__":
    run_simulation()
