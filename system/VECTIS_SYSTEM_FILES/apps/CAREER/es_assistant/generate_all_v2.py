import os
import json
import sys

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to reach EGO_SYSTEM_FILES
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from modules.unified_llm import UnifiedLLM
except ImportError:
    # If module import fails, try adding one more level up just in case
    sys.path.append(os.path.abspath(os.path.join(root_dir, "..")))
    from modules.unified_llm import UnifiedLLM

def main():
    print("Initializing Generator...")
    
    # Load IDENTITY_CORE
    identity_path = os.path.join(current_dir, "IDENTITY_CORE.md")
    identity_content = "ユーザー情報なし"
    if os.path.exists(identity_path):
        with open(identity_path, "r", encoding="utf-8") as f:
            identity_content = f.read()

    # Load Examples
    examples_path = os.path.join(current_dir, "data/WINNING_ES_EXAMPLES.json")
    if not os.path.exists(examples_path):
        print("Error: Examples file not found.")
        return

    with open(examples_path, "r", encoding="utf-8") as f:
        examples_data = json.load(f)

    # Initialize LLM
    try:
        model = UnifiedLLM(provider="ollama", model_name="phi4")
    except Exception as e:
        print(f"LLM Init Failed: {e}")
        return

    # Output Directory
    output_dir = os.path.join(current_dir, "drafts_targeted")
    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 Starting Batch ES Generation for {len(examples_data)} Industries...")

    for industry, data in examples_data.items():
        print(f"  - Generating for: {industry}...")
        
        keywords = ", ".join(data.get("keywords", []))
        winning_example = data.get("winning_example", "")
        criteria = data.get("evaluation_criteria", "")
        
        prompt = f"""
        あなたは就職活動のプロフェッショナル・ライターです。
        ユーザーの「コア・アイデンティティ」をベースに、指定された「業界」に特化した自己PR（ESドラフト）を作成してください。
        
        【ターゲット業界】
        {industry}
        
        【業界で評価されるキーワード】
        {keywords}
        
        【内定者の勝ちパターン（参考）】
        {winning_example}
        
        【評価基準】
        {criteria}
        
        【ユーザーのIdentity Core】
        {identity_content}
        
        ---
        【指示】
        ユーザーの経験や価値観（Identity Core）を、この業界が好む文脈（勝ちパターン）に沿って再構成してください。
        嘘はつかず、しかし最大限に魅力的に表現してください。
        
        【出力形式】
        タイトル: [キャッチーなタイトル]
        本文: (400文字程度)
        解説: なぜこの構成にしたか、どのキーワードを意識したか
        """
        
        try:
            response_text = model.generate(prompt)
            
            # Save to file
            safe_name = industry.replace("/", "_").replace("・", "_").replace(" ", "_").replace("(", "").replace(")", "")
            filename = f"ES_Draft_{safe_name}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {industry} 向けESドラフト\n\n")
                f.write(response_text)
                
            print(f"    ✅ Saved to {filename}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")

    print("\n✨ All drafts generated successfully!")

if __name__ == "__main__":
    main()
