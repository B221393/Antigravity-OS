import time
import os

def interview_simulator():
    print("-----------------------------------------------------")
    print("      株式会社メイテック 面接シミュレーション      ")
    print("-----------------------------------------------------")
    print("面接官: 本日はよろしくお願いいたします。")
    print("       それでは、自己紹介をお願いします。")
    print("-----------------------------------------------------")

    responses = {}
    questions = [
        ("自己紹介をお願いします。", "introduction"),
        ("株式会社メイテックを志望された理由を教えてください。", "motivation"),
        ("あなたの研究内容について、メイテックの事業と関連付けて教えてください。", "research_and_meitec"),
        ("「生涯プロエンジニア®」という働き方について、どのように考えますか？", "lifelong_engineer"),
        ("チームで困難を乗り越えた経験があれば教えてください。", "team_challenge"),
        ("メイテックでどのようなキャリアを築きたいですか？", "career_plan"),
        ("あなたの強みと弱みを教えてください。また、弱みをどのように克服しようとしていますか？", "strengths_weaknesses"),
        ("成功体験と失敗体験をそれぞれ教えてください。そこから何を学びましたか？", "success_failure"),
        ("ストレスを感じた時、どのように対処していますか？", "stress_management"),
        ("入社後、具体的にどのようにメイテックに貢献したいですか？", "contribution"),
        ("最後に、何か質問はありますか？（逆質問）", "reverse_question")
    ]

    for i, (question, key) in enumerate(questions):
        print(f"
面接官: {question}")
        start_time = time.time()
        
        user_response = input("あなた: ")
        
        end_time = time.time()
        response_time = round(end_time - start_time)
        
        responses[key] = {"question": question, "answer": user_response, "time": response_time}
        
        # Simple feedback based on general expectations
        if len(user_response) < 30 and response_time < 10 and i > 0: # Exclude self-intro for this specific feedback
            print("フィードバック: もう少し具体的に、掘り下げて回答できると良いでしょう。")
        elif len(user_response) > 200 and response_time > 60:
            print("フィードバック: 回答が長すぎると、要点が伝わりにくくなることがあります。簡潔さも意識しましょう。")
        else:
            print("フィードバック: 回答を承りました。")

        # Basic time management for 40 mins overall - rough estimate per question
        # For a 40 min interview with 6 questions, roughly 6-7 mins per question, including follow-ups.
        # This is a very rough simulation.
        if i == len(questions) - 1:
            print("
面接官: 本日はありがとうございました。以上で面接を終了します。")
            print("-----------------------------------------------------")
        else:
            print("-----------------------------------------------------")
            time.sleep(1) # Simulate thinking time

    # Final summary of responses and overall feedback after the interview
    print("
--- 面接終了後の総合フィードバック ---")
    print("以下は、あなたの回答の記録です。
")
    
    total_response_time = 0
    for key, data in responses.items():
        print(f"質問: {data['question']}")
        print(f"あなたの回答: {data['answer']}")
        print(f"回答時間: {data['time']}秒")
        total_response_time += data['time']
        print("-" * 20)
    
    print(f"
合計回答時間: {total_response_time}秒")
    if total_response_time > 40 * 60 * 0.8: # Roughly 80% of 40 mins
        print("総合評価: 全体的に回答時間が長くなる傾向があるようです。時間配分を意識し、より簡潔に要点を伝える練習をしましょう。")
    elif total_response_time < 40 * 60 * 0.3: # Roughly 30% of 40 mins
        print("総合評価: 回答時間が短い傾向にあるようです。質問に対して、より具体例や深掘りした内容を盛り込むことを意識しましょう。")
    else:
        print("総合評価: 時間配分は概ね良好です。さらに回答の質を高めることに注力しましょう。")

    print("
--- 性格診断対策のヒント ---")
    print("メイテックが求める「生涯プロエンジニア®」像を意識し、以下の点を一貫してアピールできるよう自己分析を深めましょう。")
    print("1. **学習意欲と成長志向**: 新しい技術や知識を主体的に学び続ける姿勢。")
    print("2. **主体性と課題解決能力**: 指示待ちではなく、自ら課題を見つけて解決しようとする行動力。")
    print("3. **協調性とコミュニケーション能力**: チームや顧客と円滑に連携し、貢献する力。")
    print("4. **挑戦心と粘り強さ**: 困難な状況でも諦めずに目標達成に向けて努力する姿勢。")
    print("これらの要素が、あなたの経験談や考え方と結びつくように準備してください。")


if __name__ == "__main__":
    interview_simulator()
