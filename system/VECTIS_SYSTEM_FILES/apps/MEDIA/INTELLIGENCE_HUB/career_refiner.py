"""
EGO Career Refiner
=====================
Entry Sheet (ES) の下書きを、最新の就活インテリジェンスと照らし合わせ、
自動的に修正・洗練（Refine）するプログラム。

1. CAREERディレクトリ内の下書き（Markdown）を読み込み
2. 関連する企業の最新情報を data/shukatsu/ から取得
3. LLMで「現在の業界動向」に即した改善案を提案
"""

import os
import sys
import json
import glob
from datetime import datetime
from dotenv import load_dotenv

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../../..", ".env"))

CAREER_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../..", "CAREER"))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))
SHUKATSU_DATA_DIR = os.path.join(DATA_DIR, "shukatsu")
REFINED_DIR = os.path.join(CAREER_DIR, "REFINED_OUTPUTS")
os.makedirs(REFINED_DIR, exist_ok=True)

# Add modules path
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))

# Import LLM
try:
    from modules.unified_llm_client import ask_llm
except ImportError:
    print("[ERROR] unified_llm_client not found.")
    sys.exit(1)

def load_latest_intelligence(company_name):
    """当該企業の最新インテリジェンス（パトロール結果）を取得"""
    intel_files = glob.glob(os.path.join(SHUKATSU_DATA_DIR, "SHUKATSU_*.json"))
    relevant_data = []
    
    for f in intel_files:
        try:
            with open(f, 'r', encoding='utf-8') as j:
                data = json.load(j)
                # 企業名が一致、またはタイトルに含まれる場合
                if company_name.lower() in str(data.get('title', '')).lower() or \
                   company_name.lower() in str(data.get('ai_analysis', {}).get('company', '')).lower():
                    relevant_data.append(data)
        except:
            continue
            
    # 新しい順にソートして最新3件程度を返す
    relevant_data.sort(key=lambda x: x.get('collected_at', ''), reverse=True)
    return relevant_data[:3]

def refine_es(file_path):
    """ESファイルを読み込んで洗練させる"""
    print(f"🔍 Refining: {os.path.basename(file_path)}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
        
    # 下書きから企業名を抽出（簡易的なマッチング）
    # ファイル名や内容から推定
    targets = ["KDDI", "トヨタ", "ソニー", "電通", "博報堂", "講談社", "集英社", "P&G"]
    target_company = None
    for t in targets:
        if t in original_content or t in file_path:
            target_company = t
            break
            
    intel_context = ""
    if target_company:
        print(f"   🏢 Detected Target: {target_company}")
        intel_list = load_latest_intelligence(target_company)
        if intel_list:
            intel_context = "\n### 関連する最新インテリジェンス:\n"
            for intel in intel_list:
                analysis = intel.get('ai_analysis', {})
                intel_context += f"- **{intel.get('title')}**\n"
                intel_context += f"  - 分析: {analysis.get('summary')}\n"
                if analysis.get('strategic_analysis', {}).get('action_plan'):
                    intel_context += f"  - 推奨アクション: {analysis['strategic_analysis']['action_plan']}\n"
    else:
        print("   ⚠️ Target company not detected. Performing general refinement.")

    prompt = f"""
あなたは伝説的なキャリアアドバイザー兼、戦略的就活ハッカーです。
以下のES下書きを、最新のインテリジェンス（あれば）を考慮して洗練（Refine）してください。

【ユーザーの核心的強み・世界観（不変）】
- **AIネイティブ時代の指揮官（Director）**: 単なる実装者ではなく、未完成なAIを統率するマネジメント能力。
- **重力への反逆（AntiGravity）**: 既存の非効率や「重い」システム、予定調和な回答を嫌い、本質的な価値（ What/Why ）にコミットする姿勢。
- **馬術SA級という直感**: 言葉が通じない「カオス」と対話し、信頼関係という「秩序」を導き出す観察眼。馬を「新人エンジニア」や「予測不能なエージェント」として捉える比喩。

【ユーザーの独自の語り口 (Voice Patterns)】
- ゲームやシステム設計の比喩を用いる（βテスト、バグ、ログインボーナス、パズル力、実装者vs意思決定者）。
- 「〜と考えています」といった弱気な結びを避け、「〜と確信しています」「〜にフルコミットします」「〜を先取りします」といった指揮官らしい断定を用いる。
- AI用語（コンテキスト、フォールバック）を、自身の哲学の一部として自然に織り交ぜる。

【変換例（Before/After）】
- **Before (AI-ish)**: 「貴社の技術力に惹かれ、自分の強みを活かして貢献したいと考えています。」
- **After (User-like)**: 「汎用化する技術を『ログインボーナス』として享受するのではなく、それを操る『指揮官』としての価値を貴社で証明したいと確信しています。」
- **Before (AI-ish)**: 「馬術部での経験を通じて、粘り強さを身につけました。」
- **After (User-like)**: 「言葉の通じない馬という『予測不能なエージェント』との対話を通じて、混沌から秩序を導き出す観察眼（SA級）を研ぎ澄ませてきました。」

【現在のES下書き】
---
{original_content}
---

{intel_context}

【指示】
1. **徹底した脱・AI構文**: 「〜に惹かれました」「〜に魅力を感じました」「〜に貢献したい」といったテンプレート表現は禁止です。代わりに、ユーザーのManifestoにあるような「指揮官」「重力への反逆」「未完成な技術へのコミット」という文脈で語ってください。
2. **指揮官の視点**: 技術を単なる「手段」ではなく、マネジメント対象として捉えるディレクターの立場から記述してください。
3. **具体的なインテリジェンスの「刺し】**: パトロール結果にある特定キーワード（例：KDDIの『未来のコンビニ』など）を、自身の「AI指揮能力」や「環境設計」の文脈で再解釈して組み込んでください。
4. **文字数遵守**: 400文字前後（設問に応じて）を厳守。

出力形式：
# Refined (Authentic User Voice): [元のファイル名]
## 修正後のドラフト
...
## Voice Logic (なぜこの「自分らしい」表現にしたか)
...
"""

    try:
        refined_content = ask_llm(prompt)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"REFINED_{timestamp}_{os.path.basename(file_path)}"
        output_path = os.path.join(REFINED_DIR, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(refined_content)
            
        print(f"   ✅ Saved to: {output_filename}")
        return output_path
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("🚀 EGO Career Refiner Initializing...")
    
    # スキャン対象（CAREERディレクトリ内の Markdown ファイル、ただし REFINED_OUTPUTS は除外）
    es_files = glob.glob(os.path.join(CAREER_DIR, "*.md"))
    # GAKUCHIKA テンプレなどは除外
    exclude = ["ES_COMPLETE_TEMPLATES.md", "ES_WRITING_GUIDE.md", "GAKUCHIKA_EQUESTRIAN_SA.md"]
    
    process_list = [f for f in es_files if os.path.basename(f) not in exclude]
    
    if not process_list:
        print("ℹ️ No ES drafts found to refine.")
        return

    for es_file in process_list:
        refine_es(es_file)

if __name__ == "__main__":
    main()
