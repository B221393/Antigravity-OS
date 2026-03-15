"""
EGO AUTO-FIXER (Autonomous Execution Agent)
==============================================
CAMELエージェントからの「緊急指令」を読み取り、
それを実行可能なプロンプトに変換してOSコマンドとして実行する、
EGOの「自律的な手」となるスクリプト。
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from colorama import Fore, init

init()

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../.."))
BRIDGE_FILE = os.path.join(ROOT_DIR, "EGO_SYSTEM_FILES/AI_CONTEXT_BRIDGE.md")

# API設定
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

sys.path.insert(0, os.path.join(ROOT_DIR, "EGO_SYSTEM_FILES"))
try:
    from modules.unified_llm_client import ask_llm
except:
    print(Fore.RED + "LLM Client not found" + Fore.RESET)
    exit(1)

def check_and_execute():
    if not os.path.exists(BRIDGE_FILE):
        return

    with open(BRIDGE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 未処理の緊急指令を探す
    if "**[CRITICAL INSTRUCTION]**" in content and "STATUS: EXECUTED" not in content.split("**[CRITICAL INSTRUCTION]**")[-1]:
        print(Fore.RED + "\n🚨 New Critical Instruction detected!" + Fore.RESET)
        
        # 最新の指令部分を抽出
        instruction = content.split("**[CRITICAL INSTRUCTION]**")[-1].split("---")[0].strip()
        print(Fore.YELLOW + f"Instruction: {instruction}" + Fore.RESET)

        # LLMに具体的な実行コマンドを生成させる
        prompt = f"""あなたはEGO OSのシステム管理者です。
以下の「緊急指令」を解決するためのWindows PowerShellまたはCMDのコマンドを1つだけ生成してください。

【緊急指令】
{instruction}

【制約】
- 出力は実行コマンドのみにしてください。
- ファイルパスは必要に応じて絶対パスを使用してください。
- 例: start RUN_ALL_INTELLIGENCE.bat

コマンド:"""

        print(Fore.CYAN + "🤖 Generating fix strategy..." + Fore.RESET)
        
        # 指令の内容によって処理を分ける
        if "修復" in instruction or "FIX" in instruction or "直して" in instruction:
            # --- 自己修復モード (Self-Healing) ---
            prompt = f"""あなたはEGO OSの自己修復システムです。以下の指令と対象ファイルを読み、修正後の【コード全文】のみを出力してください。
文章での説明は一切不要です。

【緊急指令】
{instruction}

出力形式:
コード全文（バッククォートなどの装飾なし）
"""
            # ファイルパスを推定（指令の中から抽出）
            import re
            file_match = re.search(r'[a-zA-Z0-9_\-\./]+\.(py|html|js|json)', instruction)
            if file_match:
                target_file_path = os.path.join(ROOT_DIR, file_match.group())
                if os.path.exists(target_file_path):
                    with open(target_file_path, "r", encoding="utf-8") as f:
                        current_code = f.read()
                    
                    full_prompt = f"{prompt}\n\n【対象ファイル: {target_file_path}】\n{current_code}"
                    print(Fore.YELLOW + f"🛠️ Attempting Self-Healing on: {target_file_path}" + Fore.RESET)
                    
                    fixed_code = ask_llm(full_prompt)
                    if fixed_code:
                        # クリーンアップ
                        if "```" in fixed_code:
                            fixed_code = fixed_code.split("```")[1]
                            if fixed_code.startswith("python") or fixed_code.startswith("html"):
                                fixed_code = "\n".join(fixed_code.split("\n")[1:])
                        
                        with open(target_file_path, "w", encoding="utf-8") as f:
                            f.write(fixed_code.strip())
                        
                        fix_command = f"Rewrote {target_file_path}"
                    else:
                        fix_command = None
                else:
                    fix_command = None
            else:
                fix_command = None
        else:
            # --- 通常のコマンド実行モード ---
            prompt = f"""あなたはEGO OSのシステム管理者です。以下の「緊急指令」を解決するためのWindowsコマンド（PowerShell/CMD）を1つだけ生成してください。
EGOシステムを更新・再起動する場合は 'RUN_ALL_INTELLIGENCE.bat' を実行するよう提案してください。
【緊急指令】: {instruction}
出力: 実行コマンドのみ"""
            fix_command = ask_llm(prompt)
            if fix_command:
                fix_command = fix_command.strip().replace("`", "").split("\n")[0]
                
                # --- EGO Specific Fixes ---
                if any(k in fix_command.lower() for k in ["reboot", "restart", "shutdown", "systemctl"]):
                    fix_command = "RUN_ALL_INTELLIGENCE.bat"
                    print(Fore.CYAN + "🔄 Redirecting to EGO restart script." + Fore.RESET)

                # --- SAFETY GUARD (DANGER CHECK) ---
                dangerous_keywords = ["shutdown /", "restart-computer", "format ", "rd /s", "rmdir /s", "del /s", "rm -rf"]
                is_dangerous = any(keyword in fix_command.lower() for keyword in dangerous_keywords)
                
                if is_dangerous:
                    print(Fore.RED + f"🚫 SAFETY BLOCK: Command '{fix_command}' was blocked because it is dangerous." + Fore.RESET)
                    with open(BRIDGE_FILE, "a", encoding="utf-8") as f:
                        f.write(f"\n> **STATUS: BLOCKED** (Dangerous Command: `{fix_command}`)\n")
                else:
                    if fix_command.endswith(".bat"):
                        subprocess.Popen(f"start cmd /c {fix_command}", shell=True, cwd=ROOT_DIR)
                    else:
                        subprocess.Popen(fix_command, shell=True, cwd=ROOT_DIR)

        if fix_command:
            # ブリッジに完了報告を追記
            with open(BRIDGE_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n> **STATUS: EXECUTED** at {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"> Result: `{fix_command}`\n")
            print(Fore.GREEN + f"✅ Success: {fix_command}" + Fore.RESET)

if __name__ == "__main__":
    print(Fore.CYAN + "🛠️ EGO Auto-Fixer Daemon started." + Fore.RESET)
    while True:
        try:
            check_and_execute()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in fixer loop: {e}")
        
        time.sleep(30) # 30秒ごとに指令書を確認
