import os
import sys
import json
import datetime
import traceback

class ErrorRelay:
    """
    VECTIS Error Relay System
    =========================
    エラーを「勝手に」記録し、AI（LAST_ERROR.md）とCLI（標準出力）に
    投げつけるためのクラス。
    """
    def __init__(self, app_name):
        self.app_name = app_name
        # ベースディレクトリの特定 (このファイルは modules/ にあると仮定)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.log_dir = os.path.join(self.base_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, "error_stream.jsonl")
        self.last_error_file = os.path.join(self.log_dir, "LAST_ERROR.md")

    def report(self, error: Exception, context: str = "", fatal: bool = False):
        """エラーを報告する"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb = traceback.format_exc()
        
        error_msg = str(error)
        error_type = type(error).__name__

        # 1. コンソールへの出力 (CLIへの通知)
        print(f"\n{'='*40}")
        print(f"🚨 [System Error Relay] {timestamp}")
        print(f"   App: {self.app_name}")
        print(f"   Msg: {error_type}: {error_msg}")
        if context:
            print(f"   Ctx: {context}")
        print(f"   -> Logged to LAST_ERROR.md")
        print(f"{'='*40}\n")
        
        # 2. ストリームログへの追記 (履歴用)
        log_entry = {
            "timestamp": timestamp,
            "app": self.app_name,
            "error_type": error_type,
            "message": error_msg,
            "context": context,
            "fatal": fatal
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except: pass

        # 3. AIへの通知 (LAST_ERROR.md の更新)
        # これを作成しておけば、ユーザーは「エラー見て」と言うだけでAIがここを参照できる
        try:
            with open(self.last_error_file, "w", encoding="utf-8") as f:
                f.write(f"# 🚨 VECTIS System Error Report\n\n")
                f.write(f"**Application**: `{self.app_name}`\n")
                f.write(f"**Timestamp**: `{timestamp}`\n")
                f.write(f"**Error Type**: `{error_type}`\n")
                f.write(f"**Message**: `{error_msg}`\n")
                f.write(f"**Context**: {context}\n")
                if fatal:
                    f.write(f"**Status**: 💀 FATAL CRASH\n")
                
                f.write(f"\n## Stack Trace\n```python\n{tb}\n```")
        except: pass

