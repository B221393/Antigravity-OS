import os
import sys
from dotenv import load_dotenv
from colorama import Fore

def run_agent_team():
    print(Fore.CYAN + "🐫 CAMEL-AI: EGO AGENT TEAM INITIALIZING..." + Fore.RESET)
    
    # Load Environment Variables
    try:
        root_path = r"c:\Users\Yuto\Desktop\app"
        env_path = os.path.join(root_path, ".env")
        load_dotenv(env_path)
        print(f"Loading .env from: {env_path}")
    except:
        pass

    # API Configuration
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("GROQ_API_KEY="):
                        groq_key = line.split("=")[1].strip()
        except:
            pass

    if not groq_key:
        print(Fore.RED + "❌ GROQ_API_KEY not found in .env" + Fore.RESET)
        return

    # Configure for Groq
    os.environ["OPENAI_API_KEY"] = groq_key
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    
    print(Fore.GREEN + f"✅ API Configured: Groq (via OpenAI Compat)" + Fore.RESET)
    
    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType
        
        # Simple Two-Agent Chat Demo
        print(Fore.YELLOW + "\n📢 Starting Simple Agent Conversation\n" + Fore.RESET)
        
        # Create two agents with different roles
        system_msg_1 = BaseMessage.make_assistant_message(
            role_name="UI Designer",
            content="You are a creative UI/UX designer specializing in futuristic interfaces."
        )
        
        system_msg_2 = BaseMessage.make_assistant_message(
            role_name="Software Architect", 
            content="You are a software architect focused on system design and technical feasibility."
        )
        
        # Create Agent 1 (Designer)
        agent_1 = ChatAgent(
            system_message=system_msg_1,
            model=ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=ModelType.GPT_3_5_TURBO,
            )
        )
        
        # Create Agent 2 (Architect)
        agent_2 = ChatAgent(
            system_message=system_msg_2,
            model=ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=ModelType.GPT_3_5_TURBO,
            )
        )
        
        print(Fore.CYAN + "🚀 STARTING DIALOGUE...\n" + Fore.RESET)
        
        # Initial message from Designer
        user_msg = BaseMessage.make_user_message(
            role_name="User",
            content="Design a futuristic dashboard for EGO OS. What are your initial ideas?"
        )
        
        # Conversation loop
        for turn in range(5):
            print(Fore.BLUE + f"\n--- Turn {turn + 1} ---" + Fore.RESET)
            
            # Agent 1 responds
            response_1 = agent_1.step(user_msg)
            print(Fore.MAGENTA + f"🎨 UI Designer: {response_1.msg.content[:200]}..." + Fore.RESET)
            
            # Agent 2 responds to Agent 1
            response_2 = agent_2.step(response_1.msg)
            print(Fore.CYAN + f"🏗️ Architect: {response_2.msg.content[:200]}..." + Fore.RESET)
            
            # Update message for next iteration
            user_msg = response_2.msg
            
            if response_1.terminated or response_2.terminated:
                print(Fore.YELLOW + "\n✅ Conversation completed." + Fore.RESET)
                break

    except Exception as e:
        print(Fore.RED + f"💥 Error: {e}" + Fore.RESET)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_agent_team()
