import os
import json
import glob
import time
import random
import sys
import requests
from datetime import datetime

# ==========================================
# 🧠 EGO DEEP THINKER (Tier 2 AI)
# ==========================================
# "Ordinary AI collects. Smart AI connects."
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IDENTITY_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../data/IDENTITY"))
INBOX_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../data/task_inbox.json")) # Raw items end up here
KIWIX_URL = "http://localhost:8080" # Local Kiwix Serve

def query_kiwix(query):
    """Query the local Kiwix server for context"""
    try:
        # Use specific ZIM prefix for reliable search in 3.x+
        # wikipedia_ja_mini is the ID we set in kiwix_manager.py
        target_id = "wikipedia_ja_mini"
        response = requests.get(f"{KIWIX_URL}/{target_id}/search?q={query}", timeout=2)
        if response.status_code == 200:
            return f"Offline Knowledge Match for '{query}': Found in Wikipedia (JA)."
    except:
        pass
    return None

def load_identity():
    """Load all identity fragments (Values, Episodes)"""
    identity_context = ""
    
    # Load Values
    val_files = glob.glob(os.path.join(IDENTITY_DIR, "VALUES/*.md"))
    for f in val_files:
        with open(f, 'r', encoding='utf-8') as file:
            identity_context += f"\n--- VALUE: {os.path.basename(f)} ---\n{file.read()}"

    # Load Episodes
    ep_files = glob.glob(os.path.join(IDENTITY_DIR, "EPISODES/*.md"))
    for f in ep_files:
        with open(f, 'r', encoding='utf-8') as file:
            identity_context += f"\n--- EPISODE: {os.path.basename(f)} ---\n{file.read()}"
            
    return identity_context

def load_fresh_intel():
    """Load raw intelligence from Patrol Inbox"""
    if not os.path.exists(INBOX_FILE):
        return []
    try:
        with open(INBOX_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            inbox = data.get('inbox', []) if isinstance(data, dict) else data
            # Return last 5 items
            return inbox[:5] if isinstance(inbox, list) else []
    except:
        return []

def think_and_synthesize():
    """The Core Thinking Loop"""
    print("\n🧠 DEEP THINKER: Awakening...")
    
    identity = load_identity()
    intel = load_fresh_intel()
    
    if not intel:
        print("   💤 No fresh intel to process. Sleeping.")
        return

    print(f"   📥 Absorbed {len(intel)} raw intelligence items.")
    print("   🔄 Connecting dots between [Identity] and [World]...")
    
    # In a real scenario, this would call an LLM API.
    # Here, we simulate the "Connection" logic for the prototype.
    
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        f.write(f"\n\n## 💡 Synthesis Log ({timestamp})\n")
        
        for item in intel:
            title = item.get('title', 'Unknown Intel')
            f.write(f"\n### Target: {title}\n")
            
            # Simulated Logic: Connect specific keywords
            if "AI" in title or "Data" in title or "Prediction" in title:
                f.write(f"- **Strat**: Use [Predictive Modeling] episode. Frame the news as 'Dealing with Uncertainty', just like your Horse Racing AI.\n")
                f.write(f"- **Appeal**: 'I understand this difficulty because I built a model to predict chaotic variables.'\n")
            elif "UX" in title or "Interface" in title or "Device" in title:
                f.write(f"- **Strat**: Use [Cybernetic Interface] episode (Onishi). Discuss 'Input Bottlenecks' in this device/software.\n")
                f.write(f"- **Appeal**: 'I optimize the human layer (HCI) before the software layer.'\n")
            elif "Strategy" in title or "Report" in title:
                f.write(f"- **Strat**: General Optimizer view. How does this strategy improve efficiency?\n")
            else:
                f.write(f"- **Strat**: Highlight 'Bridge Builder' value. Connecting this news to Physical Systems.\n")
            
            # --- Kiwix Context Injection ---
            kiwix_context = query_kiwix(title.split()[0]) # Try first word as keyword
            if kiwix_context:
                f.write(f"- **Offline Logic**: {kiwix_context}\n")

    # === INTERSECTION HYPOTHESIS GENERATOR ===
    # "Dig until you find the connection."
    # =========================================
    
    # 1. Define Knowledge Bases
    companies = ["Toyota", "Sony", "KDDI", "Keyence", "Nintendo", "SoftBank"]
    concepts = [
        "Cybernetics", "Animism", "Post-Structuralism", "Phenomenology", 
        "Complex Systems", "Game Theory", "Behavioral Economics", 
        "Sustainability", "Ethics of AI",
        "Operations Research", "Control Theory", "Reliability Engineering"
    ]
    
    # 2. Generate Hypothesis (Random Pair)
    target_company = random.choice(companies)
    target_concept = random.choice(concepts)
    
    # 3. Formulate Query (Japanese)
    # e.g. "Toyota Cybernetics Strategy", "Sony Animism Philosophy"
    query = f"{target_company} {target_concept} 思想 戦略"
    
    print(f"   🧪 Hypothesis: Does {target_company} intersect with {target_concept}?")
    
    # 4. Enqueue Command for Patrol
    queue_file = os.path.abspath(os.path.join(BASE_DIR, "../../../data/command_queue.json"))
    
    new_cmd = {
        "target": "shukatsu",
        "action": "deep_dive",
        "args": {"query": query, "type": "intersection_search"},
        "status": "pending",
        "timestamp": time.time()
    }
    
    try:
        current_queue = []
        if os.path.exists(queue_file):
            with open(queue_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    current_queue = json.loads(content)
        
        # Avoid duplicates (simple check)
        if not any(c.get('args', {}).get('query') == query for c in current_queue):
            current_queue.append(new_cmd)
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(current_queue, f, indent=2, ensure_ascii=False)
            print(f"   📨 Enqueued Deep Search: '{query}'")
        else:
            print("   ⏩ Hypothesis already in queue. Skipping.")
            
    except Exception as e:
        print(f"   ❌ Queue Error: {e}")

    # === ANALOGY HUNTER (INTELLECTUAL EXPANSION) ===
    # "What if X is like Y?"
    # ===============================================
    if random.random() < 0.3: # 30% chance to run analogy hunt
        fields = ["Biology", "Physics", "Economics", "Architecture", "Military Strategy"]
        user_skills = ["Rust Programming", "Keyboard Optimization", "Predictive Modeling"]
        
        target_skill = random.choice(user_skills)
        target_field = random.choice(fields)
        
        # Query: "Comparison between Rust and Architecture", "Biology of Keyboard Layouts"
        analogy_query = f"{target_skill} {target_field} common ground analogy"
        
        print(f"   🔭 Analogy Hunt: Is [{target_skill}] like [{target_field}]?")
        
        analogy_cmd = {
            "target": "shukatsu",
            "action": "deep_dive",
            "args": {"query": analogy_query, "type": "analogy_search"},
            "status": "pending",
            "timestamp": time.time()
        }
        
        # Enqueue (Simplified logic to merge with existing queue handling)
        try:
             current_queue = []
             if os.path.exists(queue_file):
                 with open(queue_file, 'r', encoding='utf-8') as f:
                     content = f.read().strip()
                     if content:
                         current_queue = json.loads(content)
             
             if not any(c.get('args', {}).get('query') == analogy_query for c in current_queue):
                 current_queue.append(analogy_cmd)
                 with open(queue_file, 'w', encoding='utf-8') as f:
                     json.dump(current_queue, f, indent=2, ensure_ascii=False)
                 print(f"   📨 Enqueued Analogy Search: '{analogy_query}'")
        except Exception as ae:
             print(f"   ❌ Analogy Queue Error: {ae}")

    print(f"   ✅ Thoughts crystalized in {OUTPUT_FILE}")

def main_loop():
    """Main Daemon Loop for Deep Thinker"""
    print("🧠 EGO DEEP THINKER (Tier 2 AI) Initialized.")
    print("   Mode: Continuous Thought Stream")
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Thinking Cycle Start...")
            think_and_synthesize()
            
            sleep_time = 60 # 1 minute
            print(f"   💤 Contemplating for {sleep_time} seconds (Holding Memory)...")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            print("\n👋 Deep Thinker Stopped.")
            break
        except Exception as e:
            print(f"❌ Error in thought loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    if "--one-shot" in sys.argv:
        think_and_synthesize()
    else:
        main_loop()
