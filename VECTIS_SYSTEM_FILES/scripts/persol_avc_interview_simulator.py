import time
import os

EXPECTED_INTERVIEW_MINUTES = 40
EXPECTED_INTERVIEW_SECONDS = EXPECTED_INTERVIEW_MINUTES * 60
MIN_RESPONSE_LENGTH = 30
MIN_RESPONSE_TIME_SECONDS = 10
MAX_RESPONSE_LENGTH = 200
MAX_RESPONSE_TIME_SECONDS = 60
LONG_INTERVIEW_THRESHOLD = 0.8
SHORT_INTERVIEW_THRESHOLD = 0.3

def interview_simulator():
    print("-----------------------------------------------------")
    print("  パーソルAVCテクノロジー株式会社 面接シミュレーション  ")
    print("-----------------------------------------------------")
    print("面接官: 本日はよろしくお願いいたします。")
    print("       それでは、面接を始めさせていただきます。")
    print("-----------------------------------------------------")

    responses = {}
    questions = [
        ("自己紹介をお願いします。大学での専攻や、これまでの経験を含めて教えてください。", "introduction"),
        ("パーソルAVCテクノロジーを志望された理由を教えてください。", "motivation"),
        ("なぜメーカーへの直接就職ではなく、技術派遣という働き方を選ばれたのですか？", "why_dispatch"),
        ("学生時代に最も力を入れたことは何ですか？その中でどのような困難があり、どう乗り越えましたか？", "gakuchika"),
        ("ものづくりや技術開発に対する興味・関心について教えてください。特にどのような技術分野に関心がありますか？", "tech_interest"),
        ("チームで仕事をする上で、あなたが大切にしていることは何ですか？具体的なエピソードがあれば教えてください。", "teamwork"),
        ("あなたの強みと弱みを教えてください。弱みについてはどのように克服しようとしていますか？", "strengths_weaknesses"),
        ("5年後、10年後のキャリアプランについて教えてください。パーソルAVCテクノロジーでどのように成長していきたいですか？", "career_plan"),
        ("パーソルグループの『はたらいて、笑おう。』というビジョンについて、どのように感じますか？", "vision"),
        ("ストレスを感じた時、どのように対処していますか？", "stress_management"),
        ("最後に、何か質問はありますか？（逆質問）", "reverse_question")
    ]

    for i, (question, key) in enumerate(questions):
        print(f"\n面接官: {question}")
        start_time = time.time()

        user_response = input("あなた: ")

        end_time = time.time()
        response_time = round(end_time - start_time)

        responses[key] = {"question": question, "answer": user_response, "time": response_time}

        # Feedback based on response quality indicators
        if len(user_response) < MIN_RESPONSE_LENGTH and response_time < MIN_RESPONSE_TIME_SECONDS and i > 0:
            print("フィードバック: もう少し具体的に、掘り下げて回答できると良いでしょう。STAR法（状況→課題→行動→結果）を意識してみてください。")
        elif len(user_response) > MAX_RESPONSE_LENGTH and response_time > MAX_RESPONSE_TIME_SECONDS:
            print("フィードバック: 回答が長すぎると、要点が伝わりにくくなることがあります。結論→理由→具体例の順で簡潔にまとめましょう。")
        else:
            print("フィードバック: 回答を承りました。")

        if i == len(questions) - 1:
            print("\n面接官: 本日はありがとうございました。以上で面接を終了します。")
            print("-----------------------------------------------------")
        else:
            print("-----------------------------------------------------")
            time.sleep(1)

    # Final summary
    print("\n--- 面接終了後の総合フィードバック ---")
    print("以下は、あなたの回答の記録です。\n")

    total_response_time = 0
    for key, data in responses.items():
        print(f"質問: {data['question']}")
        print(f"あなたの回答: {data['answer']}")
        print(f"回答時間: {data['time']}秒")
        total_response_time += data['time']
        print("-" * 20)

    print(f"\n合計回答時間: {total_response_time}秒")
    if total_response_time > EXPECTED_INTERVIEW_SECONDS * LONG_INTERVIEW_THRESHOLD:
        print("総合評価: 全体的に回答時間が長くなる傾向があるようです。時間配分を意識し、より簡潔に要点を伝える練習をしましょう。")
    elif total_response_time < EXPECTED_INTERVIEW_SECONDS * SHORT_INTERVIEW_THRESHOLD:
        print("総合評価: 回答時間が短い傾向にあるようです。質問に対して、より具体例や深掘りした内容を盛り込むことを意識しましょう。")
    else:
        print("総合評価: 時間配分は概ね良好です。さらに回答の質を高めることに注力しましょう。")

    print("\n--- パーソルAVCテクノロジー面接のポイント ---")
    print("パーソルAVCテクノロジーが求める人物像を意識し、以下の点を一貫してアピールできるよう準備しましょう。")
    print("1. **ものづくりへの情熱**: 家電・AV機器・車載機器の設計開発に携わりたいという具体的な意欲。")
    print("2. **技術への学習意欲**: 組込みソフト、電気電子設計、機械設計等への関心と、主体的に学び続ける姿勢。")
    print("3. **チームワーク**: 派遣先のチームに溶け込み、協力して成果を出すコミュニケーション力。")
    print("4. **キャリアビジョン**: エンジニアとして長期的にどう成長したいかの明確なビジョン。")
    print("5. **パーソルグループへの理解**: 『はたらいて、笑おう。』のビジョンへの共感と、グループの強みの理解。")
    print("\nこれらの要素が、あなたの経験談や考え方と結びつくように準備してください。")
    print("特に、「なぜ技術派遣か？」「なぜパーソルAVCテクノロジーか？」は必ず聞かれます。")
    print("パーソルクロステクノロジーとの違い（パナソニック系に特化した専門性）も説明できるようにしましょう。")


if __name__ == "__main__":
    interview_simulator()
