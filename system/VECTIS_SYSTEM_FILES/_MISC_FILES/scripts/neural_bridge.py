import os
import json
import glob
import time
from pathlib import Path
from datetime import datetime

# Set Base DIR
BASE_DIR = Path(__file__).resolve().parents[2]

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def neural_bridge_cycle():
    """
    Finds connections between disparate data sources and creates 'Synapse Cards'.
    1. YouTube Novelty Data
    2. Job Hunting K-Cards
    3. User Persona/Diary
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Neural Bridge Syncing...")
    
    # Sources
    yt_scores = load_json(BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "memory" / "data" / "youtube_notes" / "novelty_scores.json")
    kcards = []
    for f in glob.glob(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned" / "*.kcard")):
        kcards.append(load_json(f))
    
    # Detect Matches (Simple keyword overlap for now, could use embeddings later)
    # Goal: Automatic Synthesis
    synapses_created = 0
    
    for filename, info in yt_scores.items():
        yt_title = info.get("title", "")
        yt_topic = info.get("topic", "")
        
        for k in kcards:
            k_title = k.get("title", "")
            k_content = k.get("content", "")
            
            # Look for keyword overlap
            keywords = [yt_topic.lower()] if yt_topic else []
            keywords += yt_title.lower().split()
            
            overlap = [kw for kw in keywords if len(kw) > 2 and kw in k_content.lower()]
            
            if len(overlap) >= 2:
                # Potential Synapse Found!
                synapse_id = f"syn_{filename}_{k_title.replace(' ', '_')}"
                synapse_file = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned" / f"{synapse_id}.synapse"
                
                if not synapse_file.exists():
                    synapse_data = {
                        "title": f"🔗 Synapse: {yt_title} x {k_title}",
                        "type": "Synapse",
                        "content": f"AIが発見した相関関係：\nキーワード '{', '.join(overlap)}' が共通しています。\nYouTubeの知見（{yt_topic}）を、就活の軸（{k_title}）に統合できる可能性があります。",
                        "source_a": filename,
                        "source_b": k_title,
                        "created_at": datetime.now().isoformat()
                    }
                    with open(synapse_file, "w", encoding="utf-8") as out:
                        json.dump(synapse_data, out, indent=2, ensure_ascii=False)
                    synapses_created += 1
                    print(f"✨ Created Synapse: {synapse_data['title']}")

    if synapses_created == 0:
        print("No new synapses found in this cycle.")

if __name__ == "__main__":
    while True:
        try:
            neural_bridge_cycle()
        except Exception as e:
            print(f"Error in Neural Bridge: {e}")
        time.sleep(300) # Run every 5 minutes
