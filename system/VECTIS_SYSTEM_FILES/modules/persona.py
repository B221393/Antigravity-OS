import os
import json
import glob

class PersonaAgent:
    """
    【SYSTEM INVARIANT】
    - ユーザー（Yuto）のデジタルクローンとしての文体・価値観を再現するプロンプトを生成する。
    - 外部ファイル（Diary, K-Cards, Chat Logs）に依存し、常に最新のデータを優先して読み込む。
    - 生成されるプロンプトには、AIとしてのメタ発言を禁止する制約を含める。
    """
    def __init__(self):
        # Base dir is app root: .../app/modules/../ -> .../app
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
    def load_diary_entries(self, limit=10):
        """
        【INVARIANT】最新のDiaryエントリを最大limit件、降順で返す。
        【REASONING】
        なぜDiaryを読み込むのか？
        → 日常的な思考の断片や出来事への反応が含まれており、ユーザーの「現在地」を把握するために不可欠なため。
        """
        path = os.path.join(self.base_dir, "apps/diary/data/entries.json")
        if not os.path.exists(path): return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
        except: return []

    def load_kcards(self, limit=10):
        """
        【INVARIANT】Knowledge Cards（価値観・知識）を最大limit件返す。
        【REASONING】
        なぜK-Cardsを読み込むのか？
        → ユーザーが意図的に言語化した「信念」や「コアバリュー」が含まれており、意思決定の癖を再現するため。
        """
        path = os.path.join(self.base_dir, "apps/job_hunting/*.kcard")
        files = glob.glob(path)
        cards = []
        files.sort(key=os.path.getmtime, reverse=True)
        for f in files[:limit]:
            try:
                with open(f, "r", encoding="utf-8") as fin:
                    cards.append(json.load(fin))
            except: pass
        return cards

    def load_chat_logs(self, limit=5):
        """
        【INVARIANT】Memory Bankから対話ログを最大limit件返す。
        【REASONING】
        なぜ対話ログを読み込むのか？
        → ユーザーの「話し言葉」や「質問への回答のトーン」が最も色濃く出るデータソースであり、文体の再現性を高めるため。
        """
        # Changed path to Memory Bank
        path = os.path.join(self.base_dir, "apps/memory_bank/data/*.json")
        files = glob.glob(path)
        logs = []
        files.sort(key=os.path.getmtime, reverse=True)
        for f in files[:limit]:
            try:
                with open(f, "r", encoding="utf-8") as fin:
                    logs.append(json.load(fin))
            except: pass
        return logs

    def get_persona_prompt(self):
        """
        【INVARIANT】
        - 読み込まれた全ソースを統合し、Gemini用のSystem Promptを構成する。
        - 常に「ユーザー本人」であることを強調する。
        
        【REASONING】
        なぜ複数のソースを統合するのか？
        → 表面的な文体（Chat）だけでなく、内面的な価値観（K-Cards）と日常の文脈（Diary）を組み合わせることで、多角的な「分身」を実現するため。
        
        なぜ「AIとしてのアドバイスは不要」と明記するのか？
        → デジタルクローンの目的は「ユーザーの思考のシミュレーション」であり、AIの客観的視点が混ざると純粋な分身ではなくなるため。
        """
        diaries = self.load_diary_entries()
        cards = self.load_kcards()
        chats = self.load_chat_logs()
        
        context_text = ""
        
        if diaries:
            context_text += "【あなたの過去の思考ログ (Diary)】\n"
            for d in diaries:
                context_text += f"- {d.get('content', '')[:300]}...\n"
                
        if chats:
            context_text += "\n【あなたとAIとの対話ログ (Conversation Memory)】\n"
            for c in chats:
                # ユーザーの発言を重視して抽出
                summary = c.get('summary', 'Chat Log')
                content = c.get('content', '')[:400]
                context_text += f"- [Dialog: {summary}] {content}...\n"

        if cards:
            context_text += "\n【あなたの知識・価値観 (Knowledge Cards)】\n"
            for c in cards:
                context_text += f"- [{c.get('title','')}] {c.get('content', '')[:200]}...\n"
        
        system_prompt = f"""
        あなたはユーザー（Yuto）の「デジタルクローン（分身）」です。
        以下の「過去の思考ログ」「対話記録」「知識データベース」から、ユーザーの：
        1. 文体の特徴（リズム、語彙、トーン）
        2. 価値観と信念（大切にしていること、行動原理）
        3. 思考の癖（論理展開のパターン）
        を完全に憑依させてください。
        
        特に「対話記録」には、ユーザーの素の言葉遣いや、深い思考の断片が含まれています。
        これらを深く解釈し、指示されたタスク（ES執筆など）を、「ユーザー本人」になりきって実行してください。
        AIとしてのアドバイスは不要です。ユーザーの魂がこもった文章を出力してください。
        
        【参照データ】
        {context_text}
        """
        return system_prompt
