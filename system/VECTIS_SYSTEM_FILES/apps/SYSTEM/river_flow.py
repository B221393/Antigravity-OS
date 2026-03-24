
import os
import json
import subprocess
import time
import sys
from pathlib import Path

# Force UTF-8 output for Windows console (Emojis)
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
VECTIS_ROOT = Path(r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES")
DATA_DIR = VECTIS_ROOT / "data"
COMPANIES_DIR = DATA_DIR / "companies"
TARGETS_FILE = DATA_DIR / "targets.json"

# Skill Paths
RESEARCHER_SCRIPT = Path(r"C:\Users\Yuto\.gemini\skills\skill-deep-researcher\scripts\batch_analyze.py")

def load_targets():
    if not TARGETS_FILE.exists():
        print(f"⚠️ Targets file not found at {TARGETS_FILE}")
        return []
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("targets", [])

def check_research_status(company_name):
    """Checks if the Soft Analysis report exists."""
    report_path = COMPANIES_DIR / company_name / "REPORT_Soft_Analysis.md"
    return report_path.exists()

def run_researcher(company_name):
    """Executes the Deep Researcher skill."""
    print(f"🌊 [River] Triggering Deep Research for {company_name}...")
    cmd = ["python", str(RESEARCHER_SCRIPT), "--company", company_name]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ [River] Research launched for {company_name}.")
    except subprocess.CalledProcessError as e:
        print(f"❌ [River] Research failed for {company_name}: {e}")

def main():
    print("🌊 VECTIS River Flow: Automating Career Operations 🌊")
    print("====================================================")
    
    targets = load_targets()
    print(f"📋 Loaded {len(targets)} targets.")
    
    for target in targets:
        name = target["name"]
        print(f"\n🔹 Processing: {name}")
        
        # Phase 1: Research
        if check_research_status(name):
             print(f"   ✅ Research: Report found.")
        else:
             print(f"   🚫 Research: Report MISSING. Initiating flow...")
             run_researcher(name)
             
        # Phase 2: ES Generation
        es_script = VECTIS_ROOT / "apps" / "CAREER" / "es_assistant" / "auto_generate_es.py"
        es_path = COMPANIES_DIR / name / "ES_DRAFT.md"
        
        if es_path.exists():
             print(f"   ✅ ES Draft: Found.")
        elif check_research_status(name):
             print(f"   ✍️ ES Draft: MISSING. Auto-writing...")
             try:
                 subprocess.run(["python", str(es_script), "--company", name], check=True)
             except Exception as e:
                 print(f"   ❌ ES Generation failed: {e}")
        else:
             print(f"   ⏳ ES Draft: Waiting for Research.")

        # Phase 3: Interview Prep
        strat_script = Path(r"C:\Users\Yuto\.gemini\skills\skill-interview-coach\scripts\generate_strategy.py")
        strat_path = COMPANIES_DIR / name / "INTERVIEW_STRATEGY.md"
        
        if strat_path.exists():
             print(f"   ✅ Strategy: Ready.")
        elif es_path.exists():
             print(f"   ♟️ Strategy: MISSING. Generating battle plan...")
             try:
                 subprocess.run(["python", str(strat_script), "--company", name], check=True)
             except Exception as e:
                  print(f"   ❌ Strategy failed: {e}")
        else:
             print(f"   ⏳ Strategy: Waiting for ES.")

    print("\n====================================================")
    print("🌊 River Flow Cycle Complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true", help="Run discovery engine before flow")
    args = parser.parse_args()
    
    if args.discover:
        print("🔭 Launching Discovery Engine...")
        DISCOVERY_SCRIPT = Path(r"C:\Users\Yuto\.gemini\skills\skill-deep-researcher\scripts\discover.py")
        subprocess.run(["python", str(DISCOVERY_SCRIPT)])
        print("----------------------------------------------------")

    main()
