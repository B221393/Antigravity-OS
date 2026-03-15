// --- DOM Elements ---
const characterAvatar = document.getElementById('character-avatar');
const questionDisplay = document.getElementById('question-display');
const feedbackDisplay = document.getElementById('feedback-display');
const userResponseInput = document.getElementById('user-response-input');
const submitResponseBtn = document.getElementById('submit-response-btn');
const voiceInputBtn = document.getElementById('voice-input-btn');
const recognitionStatus = document.getElementById('recognition-status');

// --- Interview Data ---
const questions = [
    { text: "自己紹介をお願いします。", key: "introduction" },
    { text: "株式会社メイテックを志望された理由を教えてください。", key: "motivation" },
    { text: "あなたの研究内容について、メイテックの事業と関連付けて教えてください。", key: "research_and_meitec" },
    { text: "「生涯プロエンジニア®」という働き方について、どのように考えますか？", key: "lifelong_engineer" },
    { text: "チームで困難を乗り越えた経験があれば教えてください。", key: "team_challenge" },
    { text: "メイテックでどのようなキャリアを築きたいですか？", key: "career_plan" },
    { text: "あなたの強みと弱みを教えてください。また、弱みをどのように克服しようとしていますか？", key: "strengths_weaknesses" },
    { text: "成功体験と失敗体験をそれぞれ教えてください。そこから何を学びましたか？", key: "success_failure" },
    { text: "ストレスを感じた時、どのように対処していますか？", key: "stress_management" },
    { text: "入社後、具体的にどのようにメイテックに貢献したいですか？", key: "contribution" },
    { text: "最後に、何か質問はありますか？（逆質問）", key: "reverse_question" }
];
let currentQuestionIndex = 0;
let userResponses = [];

// --- Speech Synthesis (Text-to-Speech) ---
let speechSynth = window.speechSynthesis;
let utterance = new SpeechSynthesisUtterance();
utterance.lang = 'ja-JP';
utterance.rate = 1.0;
utterance.pitch = 1.0;

function speak(text, callback = null) {
    // Cancel any previous speech
    if (speechSynth.speaking) {
        speechSynth.cancel();
    }
    utterance.text = text;
    utterance.onstart = () => characterAvatar.classList.add('speaking');
    utterance.onend = () => {
        characterAvatar.classList.remove('speaking');
        if (callback && typeof callback === 'function') {
            callback();
        }
    };
    speechSynth.speak(utterance);
}

// --- Speech Recognition (Speech-to-Text) ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'ja-JP';
    recognition.interimResults = false; // We only want final results

    recognition.onstart = () => {
        recognitionStatus.textContent = "音声認識中... マイクに向かって話してください。";
        voiceInputBtn.disabled = true;
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userResponseInput.value = transcript;
        recognitionStatus.textContent = "音声の入力を受け付けました。内容を確認・修正して送信してください。";
    };

    recognition.onend = () => {
        voiceInputBtn.disabled = false;
        recognitionStatus.textContent = ""; // Clear status on end
    };

    recognition.onerror = (event) => {
        recognitionStatus.textContent = `音声認識エラー: ${event.error}`;
        voiceInputBtn.disabled = false;
    };
} else {
    voiceInputBtn.style.display = 'none'; // Hide button if not supported
    recognitionStatus.textContent = "お使いのブラウザは音声認識に対応していません。";
}


// --- Interview Logic ---
function displayQuestion(questionText) {
    questionDisplay.innerHTML = `<p>${questionText}</p>`;
    feedbackDisplay.innerHTML = '';
    userResponseInput.value = '';
    submitResponseBtn.disabled = false;
    voiceInputBtn.disabled = false;
    userResponseInput.focus();
    speak(questionText);
}

function provideFeedback(userAnswer, questionKey, callback) {
    let feedbackText = "回答を承りました。";
    if (userAnswer.length < 30 && questionKey !== "introduction") {
        feedbackText = "フィードバック: もう少し具体的に、掘り下げて回答できると良いでしょう。";
    } else if (userAnswer.length > 200) {
        feedbackText = "フィードバック: 回答が長すぎると、要点が伝わりにくくなることがあります。簡潔さも意識しましょう。";
    }
    feedbackDisplay.innerHTML = `<p>${feedbackText}</p>`;
    speak(feedbackText, callback);
}

function processResponse() {
    const userAnswer = userResponseInput.value.trim();
    if (!userAnswer) {
        alert("回答を入力してください。");
        return;
    }

    submitResponseBtn.disabled = true;
    voiceInputBtn.disabled = true;
    if (recognition && recognition.running) {
        recognition.stop();
    }

    const currentQuestion = questions[currentQuestionIndex];
    userResponses.push({ question: currentQuestion.text, answer: userAnswer });

    // Provide feedback then move to next question/finish
    // Callback ensures next step only happens after speak is done
    provideFeedback(userAnswer, currentQuestion.key, () => {
        setTimeout(() => {
            currentQuestionIndex++;
            if (currentQuestionIndex < questions.length) {
                displayQuestion(questions[currentQuestionIndex].text);
            } else {
                finishInterview();
            }
        }, 1500); // Wait 1.5 seconds after feedback speech ends
    });
}

function finishInterview() {
    const endMessage = "本日はありがとうございました。以上で面接を終了します。";
    questionDisplay.innerHTML = `<p>${endMessage}</p>`;
    feedbackDisplay.innerHTML = "";
    userResponseInput.style.display = 'none';
    submitResponseBtn.style.display = 'none';
    voiceInputBtn.style.display = 'none';
    recognitionStatus.style.display = 'none';
    
    speak(endMessage, () => setTimeout(displayOverallFeedback, 2000));
}

function displayOverallFeedback() {
    let finalFeedbackHtml = "<h3>--- 面接終了後の総合フィードバック ---</h3><p>あなたの回答の記録です。</p>";
    userResponses.forEach(res => {
        finalFeedbackHtml += `<p><strong>質問:</strong> ${res.question}</p>`;
        finalFeedbackHtml += `<p><strong>あなたの回答:</strong> ${res.answer}</p><hr>`;
    });
    finalFeedbackHtml += "<h4>--- 性格診断対策のヒント ---</h4><ul>" +
        "<li><strong>学習意欲と成長志向</strong>: 新しい技術や知識を主体的に学び続ける姿勢。</li>" +
        "<li><strong>主体性と課題解決能力</strong>: 指示待ちではなく、自ら課題を見つけて解決しようとする行動力。</li>" +
        "<li><strong>協調性とコミュニケーション能力</strong>: チームや顧客と円滑に連携し、貢献する力。</li>" +
        "<li><strong>挑戦心と粘り強さ</strong>: 困難な状況でも諦めずに目標達成に向けて努力する姿勢。</li></ul>";
    questionDisplay.innerHTML = finalFeedbackHtml;
}

// --- Event Listeners ---
voiceInputBtn.addEventListener('click', () => {
    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            recognitionStatus.textContent = 'エラー: 音声認識を再度開始できません。少し待ってからお試しください。';
        }
    }
});
submitResponseBtn.addEventListener('click', processResponse);
userResponseInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!submitResponseBtn.disabled) processResponse();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const startMessage = "本日はよろしくお願いいたします。それでは、自己紹介をお願いします。";
    if ('speechSynthesis' in window && SpeechRecognition) {
        speechSynth.onvoiceschanged = () => displayQuestion(startMessage);
        // Fallback for browsers that don't fire onvoiceschanged
        setTimeout(() => displayQuestion(startMessage), 250);
    } else {
        displayQuestion(startMessage);
    }
});
