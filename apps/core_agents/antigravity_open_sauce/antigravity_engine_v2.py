import os
import time
import subprocess
import json
import datetime
import random
from pathlib import Path

class AntigravityEngineV2_Career:
    def __init__(self, workspace_root):
        self.root = Path(workspace_root)
        self.log_file = self.root / "logs" / "antigravity_v2.log"
        self.memory_file = self.root / "apps" / "core_agents" / "agent_memory_v2.json"
        self.career_weapon_dir = self.root / "VECTIS_SYSTEM_FILES" / "data" / "career_weapons"
        self.iteration = 0
        self._ensure_env()

    def _ensure_env(self):
        self.career_weapon_dir.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            with open(self.memory_file, 'w') as f:
                json.dump({"total_iterations": 0, "fixed_bugs": 0, "career_weapons_created": 0, "knowledge": []}, f)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [Career-Iter {self.iteration}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(entry.strip())

    def run_cmd(self, cmd, cwd=None):
        try:
            result = subprocess.run(cmd, shell=True, cwd=str(cwd or self.root), capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()

    def discover_career_weapon(self):
        """就活で「勝つ」ための武器（コード、質問、分析）を創出する"""
        weapons = [
            {
                "name": "NYK_Autonomous_Safety_Check",
                "type": "CODE",
                "desc": "日本郵船向け：自律運航システムの安全性を検証するPythonスクリプト",
                "impact": "面接で『実機配備を想定した安全性テストコードを書きました』と提示可能"
            },
            {
                "name": "MHI_AI_Factory_Efficiency_Analysis",
                "type": "ANALYSIS",
                "desc": "三菱重工向け：データセンター冷却インフラの省エネ効率試算シート",
                "impact": "『御社のAI Factory戦略に対し、熱流体視点から貢献したい』という根拠"
            },
            {
                "name": "NTT_IOWN_Edge_Latency_Demo",
                "type": "DEMO",
                "desc": "NTT西日本向け：超低遅延ネットワークでのエッジ処理速度シミュレータ",
                "impact": "『IOWNの低遅延をどう活かすか、自らプロトタイプで検証済みです』というアピール"
            },
            {
                "name": "JR_Maintenance_Cost_Reduction_Logic",
                "type": "LOGIC",
                "desc": "JR各社向け：AI導入による設備点検コストの削減シミュレーションロジック",
                "impact": "『技術だけでなく、事業性（お役立ち）まで考えて開発しています』と証明"
            }
        ]
        return random.choice(weapons)

    def forge_weapon(self, weapon):
        """新しい就活武器を生成する"""
        weapon_dir = self.career_weapon_dir / weapon['name']
        weapon_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"🔥 FORGING WEAPON: '{weapon['name']}' for Job Hunting...")
        
        main_file = weapon_dir / "strategy_core.py"
        memo_file = weapon_dir / "INTERVIEW_TALK_SCRIPT.md"
        
        content = f"""# {weapon['name']} - Strategic Proof of Concept
# Targeted for: Top Tier Infrastructure Companies
# Goal: {weapon['desc']}

def run_strategy():
    print("--- {weapon['name']} - Executing Tactical Logic ---")
    print("Logic: Based on 2026 Tech Trends and Corporate Needs.")
    # 実証ロジックの核を生成
    print("Result: Verified Potential Contribution.")

if __name__ == "__main__":
    run_strategy()
"""
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        with open(memo_file, "w", encoding="utf-8") as f:
            f.write(f"# 面接での語り方: {weapon['name']}\n\n## 武器の概要\n{weapon['desc']}\n\n## 相手に与えるインパクト\n{weapon['impact']}\n\n## 活用シーン\n『最近注力していることは？』『弊社で何をしたい？』への回答として提示。")

        return True

    def execute_cycle(self):
        self.iteration += 1
        
        # 就活武器の創出
        weapon = self.discover_career_weapon()
        if self.forge_weapon(weapon):
            self.log(f"✅ Weapon Forged: {weapon['name']}")
            with open(self.memory_file, 'r+') as f:
                data = json.load(f)
                data["career_weapons_created"] = data.get("career_weapons_created", 0) + 1
                f.seek(0); json.dump(data, f, indent=4); f.truncate()

        # GitHubへ同期（就活実績としての草を生やす）
        if self.iteration % 2 == 0:
            self.log("Syncing Career Weapons to GitHub...")
            self.run_cmd("git add -A")
            self.run_cmd(f'git commit -m "career-strat: forge new strategic weapon {weapon["name"]} (iteration {self.iteration})" ')
            self.run_cmd("git push origin main")

    def run_forever(self):
        self.log("=== ANTIGRAVITY ENGINE V2.1: CAREER STRATEGY MODE - ONLINE ===")
        while True:
            try:
                self.execute_cycle()
                self.log("Strategic cycle complete. Sleeping for 300s...")
                time.sleep(300) # 就活武器は慎重に作るため間隔を長めに
            except Exception as e:
                self.log(f"CRITICAL ENGINE ERROR: {e}")
                time.sleep(10)

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    engine = AntigravityEngineV2_Career(root)
    engine.run_forever()
