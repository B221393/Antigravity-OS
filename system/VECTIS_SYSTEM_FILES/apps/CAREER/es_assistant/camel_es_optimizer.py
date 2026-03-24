from modules.unified_llm import UnifiedLLM
import json
import os

class CamelESOptimizer:
    def __init__(self):
        self.model = UnifiedLLM(provider="ollama", model_name="phi4")
        
    def load_examples(self):
        path = os.path.join(os.path.dirname(__file__), "data/WINNING_ES_EXAMPLES.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def run_optimization(self, industry, topic, current_draft, user_identity):
        examples_data = self.load_examples()
        target_data = examples_data.get(industry, {})
        example_text = target_data.get("winning_example", "特になし")
        keywords = ", ".join(target_data.get("keywords", []))
        evaluation_criteria = target_data.get("evaluation_criteria", "特になし")

        # --- Round 1: Coach Critique ---
        coach_prompt = f"""
        あなたは{industry}業界の採用担当者であり、厳しいES添削コーチです。
        ユーザーが書いた以下のESドラフトを、業界の「内定基準」に照らし合わせて厳しく評価してください。
        
        【業界の評価基準】
        重視するキーワード: {keywords}
        評価ポイント: {evaluation_criteria}
        
        【内定者の模範解答（参考）】
        {example_text}
        
        【ユーザーのドラフト】
        {current_draft}
        
        ---
        【指示】
        このドラフトの良い点と、内定レベルに達するために足りない点（具体性、キーワードの盛り込み不足など）を指摘し、
        具体的な改善アドバイスを提示してください。
        """
        coach_feedback = self.model.generate_content(coach_prompt).text

        # --- Round 2: User Agent Rewrite ---
        user_agent_prompt = f"""
        あなたは就職活動中の学生（ユーザー本人）です。
        以下の「コーチからのフィードバック」と「あなたのコア・アイデンティティ」を元に、ESドラフトをリライトしてください。
        
        【あなたのIdentity Core】
        {user_identity}
        
        【コーチからのフィードバック】
        {coach_feedback}
        
        ---
        【指示】
        コーチのアドバイスを受け入れつつも、あなたの個性（Identity Core）が消えないように、
        より{industry}業界に刺さる、完成度の高いESに書き直してください。
        出力は書き直した「ES本文のみ」にしてください。
        """
        improved_draft = self.model.generate_content(user_agent_prompt).text
        
        return {
            "coach_feedback": coach_feedback,
            "improved_draft": improved_draft
        }
