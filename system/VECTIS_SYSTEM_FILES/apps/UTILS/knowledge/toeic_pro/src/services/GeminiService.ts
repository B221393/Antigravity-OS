import { GoogleGenerativeAI } from "@google/generative-ai";
import type { TOEICPart, TOEICQuestion, TOEICScene } from "../types/toeic";

// Static key for local VECTIS usage
// Use environment variable for API key
// Use environment variable for API key
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY || "AIzaSyCE0PPHxz9KhY0GJIytS1j6aBTpRPT0Tuo";

const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-exp" });

export class GeminiService {
    static async generateScene(part: TOEICPart): Promise<TOEICScene> {
        const prompt = `
        You are a creative director for a global business English test (TOEIC).
        Generate a vivid, realistic scene description for a Part ${part} question.
        Context: Global business, office, airport, store, or street scene.
        Return ONLY JSON: { "scene_description": "...", "image_prompt": "Keywords for image search..." }
        `;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        let text = response.text();
        text = text.replace(/```json|```/g, "").trim();
        const scene = JSON.parse(text) as TOEICScene;

        if (part === "P1") {
            // Use Pollinations.ai for real-time generative images based on the prompt
            // "Copyright is not an issue" -> We prioritize relevance and quality over generic stock
            const safePrompt = encodeURIComponent(`${scene.image_prompt}, photorealistic, 8k, highly detailed, professional photography, business scene`);
            scene.image_url = `https://image.pollinations.ai/prompt/${safePrompt}?width=1024&height=576&nologo=true&seed=${Math.floor(Math.random() * 1000)}`;
        }

        return scene;
    }

    static async generateQuestion(part: TOEICPart, scene: TOEICScene, intensive: boolean = false): Promise<TOEICQuestion> {
        const jpInst = "IMPORTANT: The 'explanation' and 'translation' fields MUST be in JAPANESE.";
        const intensiveInst = intensive ? "INTENSIVE: Focus on HIGH-FREQUENCY patterns and COMMON PITFALLS." : "";
        const sceneDesc = scene.scene_description;

        const basePrompts: Record<string, string> = {
            P1: `Based on: '${sceneDesc}'. Generate 1 Part 1 question. Provide 4 options (A-D). ${jpInst} JSON: {"script": "M: Look at the picture marked Number 1 in your test book. (A) ... (B) ... (C) ... (D) ...", "script_translation": "スクリプトの和訳...", "question": "Look at the picture...", "options": ["(A) ...", "(B) ...", "(C) ...", "(D) ..."], "correctAnswer": 0, "explanation": "...", "translation": "..."}`,
            P2: `Generate 1 Part 2 question. Context: ${sceneDesc}. ${jpInst} JSON: {"script": "M: [Question text]? W: (A) [Response A] (B) [Response B] (C) [Response C]", "script_translation": "スクリプトの和訳...", "question": "(Listen to the question)", "options": ["(A)", "(B)", "(C)"], "correctAnswer": 0, "explanation": "...", "translation": "..."}`,
            P3: `Generate Part 3 (Conversation). Context: ${sceneDesc}. ${jpInst} JSON: {"script": "M: ... W: ... M: ...", "script_translation": "スクリプトの和訳...", "questions": [{"id": "1", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 0, "explanation": "...", "translation": "..."}, {"id": "2", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 1, "explanation": "...", "translation": "..."}, {"id": "3", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 2, "explanation": "...", "translation": "..."}]}`,
            P4: `Generate Part 4 (Short Talk). Context: ${sceneDesc}. One speaker (M or W). 3 Questions. ${jpInst} JSON: {"script": "M: ... (talk content) ...", "script_translation": "スクリプトの和訳...", "questions": [{"id": "1", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 0, "explanation": "...", "translation": "..."}, {"id": "2", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 1, "explanation": "...", "translation": "..."}, {"id": "3", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 2, "explanation": "...", "translation": "..."}]}`,
            P5: `Generate 1 Part 5 (Incomplete Sentence) question. Context: ${sceneDesc}. Level: 800+. Focus: Business Grammar/Vocab. ${jpInst} JSON: {"question": "Sentence with a _____ (blank).", "options": ["(A) ...", "(B) ...", "(C) ...", "(D) ..."], "correctAnswer": 0, "explanation": "...", "translation": "文の和訳..."}`,
            P6: `Generate Part 6 (Text Completion). Context: ${sceneDesc}. Create a short business text (email/memo/letter) with 4 blanks marked [1] to [4]. 4 Questions. ${jpInst} JSON: {"passage": "Dear Team, \n\nPlease note that the [1] will be...", "questions": [{"id": "1", "question": "Select the best answer for [1]", "options": ["A","B","C","D"], "correctAnswer": 0, "explanation": "...", "translation": "..."}, {"id": "2", "question": "Select the best answer for [2]", "options": ["A","B","C","D"], "correctAnswer": 1, "explanation": "...", "translation": "..."}, {"id": "3", "question": "Select the best answer for [3]", "options": ["A","B","C","D"], "correctAnswer": 2, "explanation": "...", "translation": "..."}, {"id": "4", "question": "Select the best answer for [4]", "options": ["A","B","C","D"], "correctAnswer": 3, "explanation": "...", "translation": "..."}]}`,
            P7: `Generate Part 7 (Reading Comprehension). Context: ${sceneDesc}. Create a realistic single passage (Email, Article, Text Chain, or Notice) approx 150-200 words. 3 Questions. ${jpInst} JSON: {"passage": "TITLE\n\nBody text logic...", "questions": [{"id": "1", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 0, "explanation": "...", "translation": "..."}, {"id": "2", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 1, "explanation": "...", "translation": "..."}, {"id": "3", "question": "...", "options": ["A","B","C","D"], "correctAnswer": 2, "explanation": "...", "translation": "..."}]}`
        };

        const prompt = basePrompts[part] || basePrompts.P5;
        // Logic for generating multi or single question...
        const result = await model.generateContent(prompt);
        const response = await result.response;
        let text = response.text();
        text = text.replace(/```json|```/g, "").trim();

        const qData = JSON.parse(text);
        return {
            id: Math.random().toString(36).substr(2, 9),
            part,
            ...qData,
            imageUrl: scene.image_url,
            isIntensive: intensive,
            timestamp: Date.now()
        };
    }
}
