
import sys
import os
import argparse
import time

# Add modules to path to import gemini_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../modules")))

try:
    import gemini_client
except ImportError:
    print("Error: Could not import gemini_client module.")
    print("Ensure VECTIS modules are correctly set up.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI - Command Line AI Assistant")
    parser.add_argument("prompt", nargs="*", help="Optional prompt to send immediately")
    parser.add_argument("--web", "-w", action="store_true", help="Enable Google Search capability")
    
    args = parser.parse_args()
    
    # Header
    print("\033[1;36m========================================")
    print("   ✨ VECTIS GEMINI TERMINAL v1.0 ✨")
    print("========================================\033[0m")
    
    model_name = "gemini-2.0-flash-exp"
    print(f"\033[90mModel: {model_name}\033[0m")
    
    # Single shot mode
    if args.prompt:
        prompt = " ".join(args.prompt)
        print(f"\n\033[1;32mUser:\033[0m {prompt}")
        print("\033[1;34mGemini:\033[0m ...", end="\r")
        try:
            start_time = time.time()
            response = gemini_client.generate_content(prompt, use_search=args.web)
            elapsed = time.time() - start_time
            print(f"\r\033[1;34mGemini ({elapsed:.2f}s):\033[0m \n{response}")
        except Exception as e:
            print(f"\n\033[1;31mError:\033[0m {e}")
        return

    # Interactive mode
    print("\n\033[90mType 'exit', 'quit' or Ctrl+C to stop.\033[0m")
    
    history = [] # Note: gemini_client currently doesn't support chat history persistence in the simple wrapper, 
                 # this CLI is valid for single-turn or simple interaction. 
                 # For multi-turn, we would need to use the generative model object directly.
    
    # To support chat properly, we should instantiate the client
    # But let's stick to the simple wrapper for now or upgrade if needed.
    
    while True:
        try:
            prompt = input("\n\033[1;32mUser>\033[0m ")
            if prompt.lower() in ['exit', 'quit']:
                break
            if not prompt.strip():
                continue
                
            print("\033[1;34mGemini:\033[0m ...", end="\r")
            
            start_time = time.time()
            # For now, simplistic single-turn (or the wrapper handles it if it was stateful, but it's not)
            # If the user wants context, we might need to append history manually or use ChatSession
            response = gemini_client.generate_content(prompt, use_search=args.web)
            elapsed = time.time() - start_time
            
            print(f"\r\033[1;34mGemini ({elapsed:.2f}s):\033[0m \n{response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n\033[1;31mError:\033[0m {e}")

if __name__ == "__main__":
    main()
