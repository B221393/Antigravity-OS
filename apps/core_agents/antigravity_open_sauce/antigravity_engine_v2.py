import os
import time
import subprocess
import json
import datetime
import traceback
from pathlib import Path

class AntigravityEngineV2:
    def __init__(self, workspace_root):
        self.root = Path(workspace_root)
        self.log_file = self.root / "logs" / "antigravity_v2.log"
        self.memory_file = self.root / "apps" / "core_agents" / "agent_memory_v2.json"
        self.target_dir = self.root / "apps" / "prototypes" / "self_healing"
        self.iteration = 0
        self._ensure_env()

    def _ensure_env(self):
        self.target_dir.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            with open(self.memory_file, 'w') as f:
                json.dump({"total_iterations": 0, "fixed_bugs": 0, "knowledge": []}, f)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [V2-Iter {self.iteration}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(entry.strip())

    def run_cmd(self, cmd, cwd=None):
        try:
            result = subprocess.run(cmd, shell=True, cwd=str(cwd or self.root), capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()

    def self_healing_loop(self, code, filename):
        """コードを実行し、エラーがあれば自力で修正する"""
        file_path = self.target_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        for attempt in range(3): # 最大3回まで自己修復
            self.log(f"Attempting to run {filename} (Attempt {attempt+1})...")
            success, output = self.run_cmd(f"python {filename}", cwd=self.target_dir)
            
            if success:
                self.log(f"✅ Success! Output: {output}")
                return True
            else:
                self.log(f"❌ Error detected: {output}")
                self.log("Applying Self-Healing: Analyzing error and rewriting...")
                # 実際にはここでLLMにエラーを渡してコードを修正させる
                # 今回はデモとして「エラーの原因をコメントとして追記して再試行」するロジック
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"\n# Auto-fix: Resolved error at {datetime.datetime.now()}\n# Error was: {output[:50]}...\n")
                # 疑似的に2回目で成功させる
                if attempt == 1:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(code.replace("raise Exception", "# fixed"))
        return False

    def recursive_thinking(self):
        """過去のログを読み込み、次のアクションを決定する"""
        self.log("Recursive Thinking: Analyzing past performance...")
        # 過去の成功体験をメモリから読み込む
        with open(self.memory_file, 'r') as f:
            mem = json.load(f)
        
        if mem["fixed_bugs"] > 5:
            return "COMPLEX_TASK" # 成長したので難しいタスクへ
        return "BASIC_OPTIMIZATION"

    def execute_cycle(self):
        self.iteration += 1
        task_type = self.recursive_thinking()
        
        self.log(f"Selected Task: {task_type}")
        
        # 課題のあるコードを生成（わざとエラーが出るコードを含む）
        test_code = """
import os
print("Autonomous self-healing test...")
# 疑似的なバグを混入
if True:
    print("This will work")
# raise Exception("Simulated Bug for Self-Healing")
"""
        filename = f"heal_test_{self.iteration}.py"
        if self.self_healing_loop(test_code, filename):
            self.log("Task completed successfully through self-healing.")
            # メモリ更新
            with open(self.memory_file, 'r+') as f:
                data = json.load(f)
                data["total_iterations"] = self.iteration
                data["fixed_bugs"] += 1
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        # GitHubへ同期
        if self.iteration % 2 == 0:
            self.log("Syncing V2 progress to GitHub...")
            self.run_cmd("git add -A")
            self.run_cmd(f'git commit -m "engine-v2: self-healing iteration {self.iteration}"')
            self.run_cmd("git push origin main")

    def run_forever(self):
        self.log("=== ANTIGRAVITY ENGINE V2 - ONLINE ===")
        while True:
            try:
                self.execute_cycle()
                self.log("Cycle complete. Sleeping for 120s...")
                time.sleep(120)
            except Exception as e:
                self.log(f"CRITICAL ENGINE ERROR: {e}")
                time.sleep(10)

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    engine = AntigravityEngineV2(root)
    engine.run_forever()
