import os
import re
from datetime import datetime

TARGET_DIR = r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES"
DASHBOARD_FILE = os.path.join(TARGET_DIR, "VECTIS_TASK_DASHBOARD.md")

tasks = []

# Walk through all markdown files
for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith(".md") and file != "VECTIS_TASK_DASHBOARD.md":
            filepath = os.path.join(root, file)
            # Make path relative for the dashboard link
            rel_path = os.path.relpath(filepath, TARGET_DIR)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        # Match uncompleted tasks: - [ ]
                        if re.match(r'^\s*-\s*\[ \]', line):
                            # extract the actual task text
                            match = re.match(r'^\s*-\s*\[ \]\s*(.*)', line)
                            if match:
                                task_content = match.group(1).strip()
                                tasks.append({
                                    "file": file,
                                    "rel_path": rel_path.replace("\\", "/"),
                                    "line": line_num,
                                    "content": task_content
                                })
            except Exception as e:
                # Skip files that can't be decoded
                pass

# Generate Dashboard
with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
    f.write("# 📋 VECTIS OS - 統合タスクダッシュボード (Obsidian風)\n\n")
    f.write(f"*最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
    f.write("> VECTIS内の全Markdownファイルから、未完了のタスク(`- [ ]`)を自動抽出して一覧化しています。\n\n")
    
    if not tasks:
        f.write("🎉 現在、未完了のタスクはありません！\n")
    else:
        # Group by file
        files_dict = {}
        for t in tasks:
            files_dict.setdefault(t['file'], []).append(t)
            
        for filename, tasks_in_file in files_dict.items():
            first_task = tasks_in_file[0]
            f.write(f"## 📁 [{filename}](./{first_task['rel_path']})\n")
            for t in tasks_in_file:
                # Create a markdown link that VS Code can click
                f.write(f"- [ ] {t['content']} *(行: {t['line']})*\n")
            f.write("\n")

print(f"Task dashboard generated with {len(tasks)} tasks.")
