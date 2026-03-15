import os
from datetime import datetime

class BloggerAgent:
    def __init__(self, log_file=os.path.join("outputs", "logs", "activity_log.md")):
        self.log_file = log_file
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not os.path.exists(self.log_file):
            self._initialize_log()

    def _initialize_log(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("# SYSTEM ACTIVITY LOG\n\n")
            f.write("Operational records for search and system actions.\n\n")

    def log_entry(self, user_instruction, research_process=None, actions=None, output=None, reflection=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"## [{timestamp}]\n\n"
        entry += f"### INPUT\n{user_instruction}\n\n"
        
        if research_process:
            entry += "### RESEARCH\n"
            if isinstance(research_process, list):
                for item in research_process:
                    entry += f"- {item}\n"
            else:
                entry += f"{research_process}\n"
            entry += "\n"

        if actions:
            entry += "### ACTIONS\n"
            if isinstance(actions, list):
                for action in actions:
                    entry += f"- {action}\n"
            else:
                entry += f"{actions}\n"
            entry += "\n"

        if output:
            entry += "### OUTPUT\n"
            entry += f"```\n{output}\n```\n\n"

        if reflection:
            entry += "### NOTES\n"
            entry += f"> {reflection}\n\n"

        entry += "---\n\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        
        print(f"Log updated: {self.log_file}")

    def deep_reflect(self, goal, history):
        """
        Synthesizes multiple actions into a single blog-like summary.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"## [BLOG] MISSION: {goal} ({timestamp})\n\n"
        entry += "### JOURNEY\n"
        for i, h in enumerate(history):
            entry += f"{i+1}. {h}\n"
        
        entry += "\n### FINAL THOUGHTS\n"
        entry += "> Captured insights from this sequence. Mission accomplished.\n\n"
        entry += "===\n\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"Deep Reflect saved: {self.log_file}")

if __name__ == "__main__":
    # Simple test
    blogger = BloggerAgent("test_log.md")
    blogger.log_entry(
        user_instruction="今日の天気を調べてメモ帳に書いて",
        research_process=["Google検索: 東京 天気", "知見: 晴れ、最高気温15度"],
        actions=["メモ帳を起動", "『本日の天気は晴れです』と入力"],
        output="メモ帳に保存完了",
        reflection="メモ帳の起動待ち時間をもう少し考慮すべきかもしれない"
    )
