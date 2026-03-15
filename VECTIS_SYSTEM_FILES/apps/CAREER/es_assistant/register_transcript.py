
import json
import csv
import os
import datetime

# Paths
BASE_DIR = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES"
CSV_PATH = os.path.join(BASE_DIR, r"apps\es_assistant\data\submission_materials\transcript_db_alpha.csv")
UNIVERSE_PATH = os.path.join(BASE_DIR, r"apps\MEDIA\INTELLIGENCE_HUB\data\universe.json")

def register_transcript():
    print("🚀 Starting Transcript Registration to EGO Universe DB...")
    
    # 1. Read CSV
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: CSV not found at {CSV_PATH}")
        return

    courses = []
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                courses.append(row)
        print(f"✅ Loaded {len(courses)} courses from CSV.")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # 2. Prepare Node
    transcript_node = {
        "id": "USER_ACADEMIC_RECORD_2026",
        "type": "ACADEMIC_RECORD",
        "title": "Yuto's Academic Transcript (Hiroshima University)",
        "summary": "Full academic record including grades for Engineering, Physics, Math, and Communication courses.",
        "group": "USER_PROFILE",
        "importance": 10,
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": {
            "university": "Hiroshima University",
            "department": "Engineering Cluster 1 (Mechanical Systems)",
            "total_courses": len(courses),
            "courses": courses
        }
    }

    # 3. Update Universe
    if not os.path.exists(UNIVERSE_PATH):
        print(f"❌ Error: Universe DB not found at {UNIVERSE_PATH}")
        return

    try:
        with open(UNIVERSE_PATH, 'r', encoding='utf-8') as f:
            universe = json.load(f)
        
        # Check for existing node and update/append
        nodes = universe.get("nodes", [])
        existing_index = next((index for (index, d) in enumerate(nodes) if d["id"] == "USER_ACADEMIC_RECORD_2026"), None)
        
        if existing_index is not None:
             print("ℹ️ Updating existing transcript record...")
             nodes[existing_index] = transcript_node
        else:
             print("ℹ️ Creating new transcript record...")
             nodes.append(transcript_node)
        
        universe["nodes"] = nodes
        
        with open(UNIVERSE_PATH, 'w', encoding='utf-8') as f:
            json.dump(universe, f, indent=2, ensure_ascii=False)
            
        print("YOUR DATA HAS BEEN REGISTERED TO THE UNIVERSE DB. 🌌")
        print(f"Saved to: {UNIVERSE_PATH}")
        
    except Exception as e:
        print(f"❌ Error updating Universe DB: {e}")

if __name__ == "__main__":
    register_transcript()
