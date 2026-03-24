
import sys
import json
import os
import argparse
from datetime import datetime

# Path to the shared command queue
QUEUE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/command_queue.json"))

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_queue(queue):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

def enqueue_command(target, action, args=None, priority="normal"):
    queue = load_queue()
    
    command = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "action": action,
        "args": args,
        "priority": priority,
        "status": "pending"
    }
    
    # Priority handling: insert high priority at start
    if priority == "high":
        queue.insert(0, command)
    else:
        queue.append(command)
        
    save_queue(queue)
    print(f"✅ Command Enqueued: [{target}] {action} (Args: {args})")

def main():
    parser = argparse.ArgumentParser(description="EGO Command Bridge for Cloudbot/Clawdbot")
    parser.add_argument("command", nargs="*", help="Direct command input (e.g. 'Search for Sony')")
    parser.add_argument("--target", default="shukatsu", help="Target core (shukatsu/racing)")
    parser.add_argument("--action", default="deep_dive", help="Action to perform")
    
    # Context Update Args
    parser.add_argument("--set-focus", help="Update current focus topics (comma separated)")
    parser.add_argument("--set-company", help="Update priority companies (comma separated)")
    
    args = parser.parse_args()
    
    if args.set_focus or args.set_company:
        try:
            context_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/user_context.json"))
            with open(context_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if args.set_focus:
                data['current_focus'] = [x.strip() for x in args.set_focus.split(",")]
                print(f"✅ Updated Focus: {data['current_focus']}")
                
            if args.set_company:
                data['priority_companies'] = [x.strip() for x in args.set_company.split(",")]
                print(f"✅ Updated Priority Companies: {data['priority_companies']}")
            
            data['last_updated'] = datetime.now().isoformat()
            
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Trigger immediate Deep Dive on new focus
            enqueue_command("shukatsu", "deep_dive", {"query": data['priority_companies'][0] if data['priority_companies'] else "General"}, priority="high")
            
        except Exception as e:
            print(f"❌ Failed to update context: {e}")
        return

    if args.command:
        # Simplified "Natural Language" style input
        input_str = " ".join(args.command)
        enqueue_command("shukatsu", "deep_dive", {"query": input_str}, priority="high")
    else:
        # Interactive Mode
        print("🤖 EGO COMMAND BRIDGE (Input Mode)")
        print("Type a command (or 'exit'):")
        while True:
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if user_input.strip():
                 enqueue_command("shukatsu", "deep_dive", {"query": user_input}, priority="high")

if __name__ == "__main__":
    main()
