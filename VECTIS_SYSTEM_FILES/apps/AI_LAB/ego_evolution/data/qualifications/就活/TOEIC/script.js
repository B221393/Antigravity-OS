const quizData = [
    {
        question: "The man _______ the newspaper is my father.",
        answers: [
            { text: "reading", correct: true },
            { text: "reads", correct: false },
            { text: "is reading", correct: false },
            { text: "read", correct: false }
        ]
    },
    {
        question: "I am looking forward _______ you again.",
        answers: [
            { text: "to seeing", correct: true },
            { text: "to see", correct: false },
            { text: "seeing", correct: false },
            { text: "see", correct: false }
        ]
    },
    {
        question: "She has been working here _______ 2010.",
        answers: [
            { text: "since", correct: true },
            { text: "for", correct: false },
            { text: "in", correct: false },
            { text: "on", correct: false }
        ]
    },
    {
        question: "This is the _______ interesting book I have ever read.",
        answers: [
            { text: "most", correct: true },
            { text: "more", correct: false },
            { text: "much", correct: false },
            { text: "many", correct: false }
        ]
    },
    {
        question: "If I _______ you, I would not do that.",
        answers: [
            { text: "were", correct: true },
            { text: "am", correct: false },
            { text: "was", correct: false },
            { text: "be", correct: false }
        ]
    },
    {
        question: "He is used to _______ up early.",
        answers: [
            { text: "getting", correct: true },
            { text: "get", correct: false },
            { text: "got", correct: false },
            { text: "have gotten", correct: false }
        ]
    },
    {
        question: "The meeting was put _______ until next week.",
        answers: [
            { text: "off", correct: true },
            { text: "on", correct: false },
            { text: "in", correct: false },
            { text: "out", correct: false }
        ]
    },
    {
        question: "I _______ my homework when she called me.",
        answers: [
            { text: "was doing", correct: true },
            { text: "did", correct: false },
            { text: "am doing", correct: false },
            { text: "do", correct: false }
        ]
    },
    {
        question: "This book is _______ than that one.",
        answers: [
            { text: "better", correct: true },
            { text: "good", correct: false },
            { text: "best", correct: false },
            { text: "more good", correct: false }
        ]
    },
    {
        question: "You had better _______ to the doctor.",
        answers: [
            { text: "go", correct: true },
            { text: "to go", correct: false },
            { text: "going", correct: false },
            { text: "went", correct: false }
        ]
    }
];

const questionContainer = document.getElementById("question-container");
const questionText = document.getElementById("question-text");
const answersContainer = document.getElementById("answers-container");
const submitBtn = document.getElementById("submit-btn");
const feedbackContainer = document.getElementById("feedback-container");

let currentQuestionIndex = 0;
let selectedAnswer = null;

function showQuestion() {
    const currentQuestion = quizData[currentQuestionIndex];
    questionText.innerText = currentQuestion.question;
    answersContainer.innerHTML = "";
    currentQuestion.answers.forEach(answer => {
        const button = document.createElement("button");
        button.innerText = answer.text;
        button.classList.add("answer-btn");
        button.addEventListener("click", () => {
            selectedAnswer = answer;
            Array.from(answersContainer.children).forEach(btn => {
                btn.style.backgroundColor = "";
            });
            button.style.backgroundColor = "#e0e0e0";
        });
        answersContainer.appendChild(button);
    });
}

function showFeedback() {
    if (selectedAnswer) {
        if (selectedAnswer.correct) {
            feedbackContainer.innerText = "Correct!";
            feedbackContainer.style.color = "green";
        } else {
            feedbackContainer.innerText = "Incorrect.";
            feedbackContainer.style.color = "red";
        }
        submitBtn.innerText = "Next";
        submitBtn.removeEventListener("click", showFeedback);
        submitBtn.addEventListener("click", nextQuestion);
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < quizData.length) {
        selectedAnswer = null;
        feedbackContainer.innerText = "";
        submitBtn.innerText = "Answer";
        showQuestion();
        submitBtn.removeEventListener("click", nextQuestion);
        submitBtn.addEventListener("click", showFeedback);
    } else {
        questionText.innerText = "Quiz finished!";
        answersContainer.innerHTML = "";
        submitBtn.style.display = "none";
        feedbackContainer.innerText = "";
    }
}

submitBtn.addEventListener("click", showFeedback);

showQuestion();