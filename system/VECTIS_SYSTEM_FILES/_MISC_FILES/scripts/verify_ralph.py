import os
import sys
from pathlib import Path

# Setup Path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "VECTIS_SYSTEM_FILES"))

from _SYSTEM.scripts.orchestrator import SecretaryOrchestrator
from dotenv import load_dotenv

def run_verification():
    load_dotenv(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / ".env"))
    orch = SecretaryOrchestrator()
    
    # Ralph Mode Mission Goal
    goal = "VECTISダッシュボード(http://localhost:8501)にアクセスして『Mission Status』が正常に更新されているか確認し、その後 Memory 3D (http://localhost:8512) を開いて、先程生成されたInternシップのシナプス（金色のノード）が存在することを視覚的に確認せよ。"
    
    orch.run_autonomous_loop(goal)

if __name__ == "__main__":
    run_verification()
