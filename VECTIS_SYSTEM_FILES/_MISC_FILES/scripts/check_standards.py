import os
import re
import ast

def check_file_standards(file_path: str) -> tuple[list[str], list[str]]:
    """
    【INVARIANT】
    - INPUT: 有効なPythonファイルパス
    - OUTPUT: (警告リスト, エラーリスト) のタプル
    
    【REASONING】
    なぜast（抽象構文木）を使うのか？
    → 単なる文字列検索よりも、関数定義やdocstringを正確に特定できるため。
    → コメントアウトされたコードを無視できるため。
    """
    warnings = []
    errors = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errors.append(f"READ_ERROR: {e}")
        return warnings, errors
        
    # 旧Gemini SDKのチェック
    # REASONING: このスクリプト自体が 'import google.generativeai' という文字列を含むため、
    # インポート文そのものをチェックするように正規表現を使用する。
    if re.search(r'^\s*(import google\.generativeai|from google import generativeai)', content, re.MULTILINE):
        errors.append("DEPRECATED_SDK: Old Gemini SDK import found. Use 'modules.gemini_client' instead.")

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        errors.append(f"SYNTAX_ERROR: {e}")
        return warnings, errors

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            name = node.name
            
            # 小さなプライベート関数や__init__は除外
            if name.startswith("_") or name == "main":
                continue

            if not docstring:
                warnings.append(f"MISSING_DOCSTRING: '{name}' has no docstring.")
                continue

            # First-Class Reasoning セクションのチェック
            required_sections = ["【INVARIANT】", "【REASONING】"]
            for section in required_sections:
                if section not in docstring:
                    warnings.append(f"MISSING_SECTION: '{name}' docstring is missing {section}")

    return warnings, errors

def main():
    """
    【INVARIANT】
    - プロジェクトの主要ディレクトリをスキャンし、規約違反を標準出力に報告する。
    
    【REASONING】
    なぜ target_dirs を限定しているのか？
    → node_modules や .venv などの外部ライブラリをスキャン対象から外すため。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dirs = ["apps", "modules", "scripts"]
    
    print(f"🔍 Scanning VECTIS Project Standards in {base_dir}...")
    print("-" * 60)
    
    total_files = 0
    total_warnings = 0
    total_errors = 0

    for target in target_dirs:
        dir_path = os.path.join(base_dir, target)
        if not os.path.exists(dir_path): continue
        
        for root, _, files in os.walk(dir_path):
            # Skip node_modules and .venv
            if "node_modules" in root or ".venv" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    total_files += 1
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, base_dir)
                    
                    warnings, errors = check_file_standards(full_path)
                    
                    if warnings or errors:
                        print(f"📄 {rel_path}")
                        for e in errors:
                            print(f"  ❌ {e}")
                            total_errors += 1
                        for w in warnings:
                            print(f"  ⚠️ {w}")
                            total_warnings += 1
                            
    print("-" * 60)
    print(f"✅ Scan Complete. Files: {total_files}, Errors: {total_errors}, Warnings: {total_warnings}")

if __name__ == "__main__":
    main()
