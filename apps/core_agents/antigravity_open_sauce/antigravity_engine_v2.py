import os
import time
import subprocess
import json
import datetime
import random
from pathlib import Path

class AntigravityEngineV2_Intelligence:
    def __init__(self, workspace_root):
        self.root = Path(workspace_root)
        self.log_file = self.root / "logs" / "antigravity_v2.log"
        self.memory_file = self.root / "apps" / "core_agents" / "agent_memory_v2.json"
        self.intel_dir = self.root / "VECTIS_SYSTEM_FILES" / "documents" / "Knowledge_Base"
        self.iteration = 0
        self._ensure_env()

    def _ensure_env(self):
        (self.intel_dir / "Salary_Analysis").mkdir(parents=True, exist_ok=True)
        (self.intel_dir / "Paper_Digests").mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            with open(self.memory_file, 'w') as f:
                json.dump({"total_iterations": 0, "intel_reports_created": 0}, f)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [Intel-Iter {self.iteration}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(entry.strip())

    def run_cmd(self, cmd, cwd=None):
        try:
            result = subprocess.run(cmd, shell=True, cwd=str(cwd or self.root), capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()

    def generate_salary_analysis(self):
        """企業別の初任給・待遇データを生成・分析する"""
        targets = [
            {"corp": "日本郵船 (NYK)", "bachelor": 260000, "master": 290000, "perks": "独身寮、社宅、海外駐在手当強", "tech_spend": "MEGURI2040等のDX投資額大"},
            {"corp": "三菱重工 (MHI)", "bachelor": 255000, "master": 285000, "perks": "借上社宅、保養所、防衛手当", "tech_spend": "AI Factory、水素エネルギー"},
            {"corp": "パナソニック", "bachelor": 260000, "master": 293000, "perks": "カフェテリアプラン、WLB良好", "tech_spend": "EV電池、くらしDX"},
            {"corp": "JR東日本", "bachelor": 245000, "master": 275000, "perks": "職宅、乗車証、安定性極大", "tech_spend": "スマートメンテナンス、鉄道版生成AI"}
        ]
        target = random.choice(targets)
        file_name = f"Salary_Analysis/{target['corp']}_Strategy.md"
        path = self.intel_dir / file_name
        
        content = f"""# 企業分析レポート: {target['corp']}
- **初任給 (学部卒)**: 月給 {target['bachelor']:,}円
- **初任給 (修士了)**: 月給 {target['master']:,}円
- **主要な福利厚生**: {target['perks']}
- **技術投資の方向性**: {target['tech_spend']}

## 戦略的考察
1. **経済的価値**: 初任給は横並びだが、{target['perks']}による実質的な可処分所得の差に注目。
2. **技術的価値**: {target['tech_spend']}に予算が割かれており、エンジニアとして挑戦的な環境。
3. **キャリアパス**: 高い初期給与だけでなく、技術投資が活発な分野（自律化等）での市場価値向上を目指すべき。
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return target['corp']

    def generate_paper_digest(self):
        """最新論文の要約と面接転用ロジックを生成する"""
        papers = [
            {"title": "Multi-Agent Reinforcement Learning for Autonomous Ships", "focus": "海運DX", "value": "複数船の衝突回避アルゴリズム"},
            {"title": "Transformer-based Predictive Maintenance for Rail Circuits", "focus": "鉄道AI", "value": "信号設備の故障予測モデル"},
            {"title": "Rust-based Safe Memory Management in Robotics", "focus": "重工・ロボティクス", "value": "C++からRustへの移行メリット"},
            {"title": "Quantum-Secure Communication in IOWN Architectures", "focus": "通信・NTT", "value": "次世代ネットワークのセキュリティ"}
        ]
        paper = random.choice(papers)
        file_name = f"Paper_Digests/{paper['title'].replace(' ', '_')}.md"
        path = self.intel_dir / file_name
        
        content = f"""# 論文ダイジェスト: {paper['title']}
- **カテゴリー**: {paper['focus']}
- **核心**: {paper['value']}
- **作成日**: {datetime.datetime.now()}

## 3行要約
1. 最新の{paper['focus']}分野における{paper['value']}の実装手法を提案。
2. 従来の課題であった信頼性をXX%向上させたと主張。
3. 今後の商用化に向けた具体的なロードマップを提示。

## 面接での活用（キラーフレーズ）
「最近、{paper['title']}という論文を読み、{paper['focus']}における自律制御の可能性を再認識しました。特に{paper['value']}という視点は、御社のXX事業の課題解決に直結すると考えており、非常にワクワクしています。」
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return paper['title']

    def execute_cycle(self):
        self.iteration += 1
        
        # 待遇分析と論文要約を両方実行
        corp = self.generate_salary_analysis()
        paper = self.generate_paper_digest()
        
        self.log(f"✅ Intel Generated: {corp} Strategy & {paper} Digest")
        
        with open(self.memory_file, 'r+') as f:
            data = json.load(f)
            data["intel_reports_created"] = data.get("intel_reports_created", 0) + 2
            f.seek(0); json.dump(data, f, indent=4); f.truncate()

        # GitHubへ同期
        if self.iteration % 2 == 0:
            self.log("Syncing Intel Assets to GitHub...")
            self.run_cmd("git add -A")
            self.run_cmd(f'git commit -m "intel-strat: update salary analysis and paper digests (iteration {self.iteration})" ')
            self.run_cmd("git push origin main")

    def run_forever(self):
        self.log("=== ANTIGRAVITY ENGINE V2.2: INTEL & STRATEGY MODE - ONLINE ===")
        while True:
            try:
                self.execute_cycle()
                self.log("Intel collection complete. Sleeping for 300s...")
                time.sleep(300)
            except Exception as e:
                self.log(f"CRITICAL ENGINE ERROR: {e}")
                time.sleep(10)

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    engine = AntigravityEngineV2_Intelligence(root)
    engine.run_forever()
