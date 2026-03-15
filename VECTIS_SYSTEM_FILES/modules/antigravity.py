import json
import os
from .unified_llm import create_llm_client


class AntigravityArchitect:
    def __init__(self):
        # Default to Gemini 1.5 Flash for Antigravity (needs large context)
        # UnifiedLLM will fallback to Ollama if Gemini is unavailable
        from .unified_llm import UnifiedLLM
        self.llm = UnifiedLLM(provider="gemini", model_name="gemini-1.5-flash")
        # Load Constitution
        try:
            doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/ANTIGRAVITY_CONSTITUTION.md")
            with open(doc_path, "r", encoding="utf-8") as f:
                self.constitution = f.read()
        except:
            self.constitution = "Rule: Focus on deep logic and structural connections."

    def generate_universe_node(self, transcript, video_title, existing_nodes):
        """
        Analyzes transcript and existing nodes to generate a new Universe Node.
        Uses UnifiedLLM to support both Gemini and Ollama.
        """
        
        # Language Detection: Skip if content is primarily English
        import re
        # Count Japanese characters (Hiragana, Katakana, Kanji)
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', transcript))
        # Count ASCII letters
        english_chars = len(re.findall(r'[a-zA-Z]', transcript))
        
        # If more than 60% English, skip this content
        total_chars = japanese_chars + english_chars
        if total_chars > 0 and (english_chars / total_chars) > 0.6:
            return {"error": "Content is primarily in English. Skipping to maintain Japanese knowledge base."}
        
        # 1. Context Preparation
        universe_context = "\n".join([f"- [{n['id']}] {n['title']}" for n in existing_nodes])
        
        # 2. Architect Prompt (WIKIPEDIA ENCYCLOPEDIC MODE)
        product_prompt = f"""
        あなたは「Antigravity Architect」（VECTIS一元知識宇宙の主任司書）です。
        
        【憲法（絶対的ルール）】
        {self.constitution}

        【任務】
        提供されたコンテンツを吸収し、**「Wikipediaスタイルの百科事典記事」**を統合・生成してください。
        
        【重要指示（ユーザー命令）】
        1. **目標ボリューム**: **10,000文字級**の出力を目指してください。
           - **最重要**: 入力テキストが短い、または詳細に欠ける場合、**あなたの内部知識ベースを活用して**概念、歴史、技術的詳細、文脈を大幅に拡張してください。短い要約は禁止です。
        2. **密度戦略（"圧縮と肥大化"）**:
           - **圧縮**: 会話的な繋ぎ言葉、主観的な冗長表現、繰り返しを無慈悲に削除してください。
           - **肥大化**: すべての核となる概念について、深い定義、歴史的起源、理論的背景、将来的意味合いを提供してください。内容は**「極めて分厚く」**（構造的に密に）してください。
        3. **スタイル**: Wikipedia構文。学術的、百科事典的、客観的。
        4. **言語**: 日本語。
        
        【既存の宇宙（文脈）】
        {universe_context}
        
        【ターゲットコンテンツ】
        タイトル: {video_title}
        内容:
        {transcript[:50000]} 
        
        【出力フォーマット（厳格なJSON）】
        {{
          "node_metadata": {{
            "title": "Wikipedia記事タイトル（日本語）",
            "summary": "ここに記事全文を書く（Markdown）。改行には \\n を使用。ダブルクォートは \\" のようにエスケープすること。\n\n## 概要\n(Overview...)\n\n## 定義と語源\n(Definition...)\n\n## 歴史的背景\n(History... 一般知識を用いて大幅に拡張)\n\n## 構造とメカニズム\n(Detailed technical breakdown...)\n\n## 現代における意義\n(Significance...)\n\n## 関連項目\n(See also...)",
            "group": "Human Education (人育)",
            "importance_score": 10
          }},
          "gravity_links": [
            {{
              "target_id": "Existing Node ID",
              "strength": 5,
              "reason": "Connection logic"
            }}
          ],
          "suggested_tags": ["Keyword1", "Keyword2"],
          "shukatsu_task": {{
             "detected": true,
             "task_name": "Event Name or null",
             "date": "YYYY-MM-DD or null",
             "priority": 10
          }}
        }}

        重要:
        - 有効なJSONのみを返してください。
        - 文字列内のダブルクォートはすべてエスケープしてください。
        - 改行には \\n を使用してください。
        - 'summary' は**巨大**でなければなりません（10,000文字相当を目指す）。
        - **空白を埋めるために内部知識を使用してください。**
        """

        # 3. Execution
        try:
            # Use UnifiedLLM
            response_text = self.llm.generate(product_prompt)
            
            # Auto-repair JSON: Find first '{' and last '}'
            import re
            match = re.search(r"(\{.*\})", response_text.replace('\n', ' '), re.DOTALL)
            if match:
                clean_text = match.group(1)
            else:
                # Fallback: naive strip
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                result = json.loads(clean_text)
            except json.JSONDecodeError as jde:
                return {"error": f"JSON Decode Error: {jde}. Raw Text prefix: {clean_text[:50]}..."}
            
            # Validate summary length
            summary = result.get("node_metadata", {}).get("summary", "")
            if len(summary) < 300:
                return {"error": f"Summary too short ({len(summary)} chars). Need 800-1200 chars."}
            
            return result
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test Run
    architect = AntigravityArchitect()
    
    # Mock Data
    existing = [
        {"id": "V001", "title": "Python Programming Basics"},
        {"id": "V002", "title": "The Philosophy of Science"}
    ]
    
    new_title = "Advanced Python Connects to Logic"
    new_transcript = "In this video we explore how Python's logical structures mirror philosophical reasoning..."
    
    print("Testing Architect...")
    result = architect.generate_universe_node(new_transcript, new_title, existing)
    print(json.dumps(result, indent=2, ensure_ascii=False))
