import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/refactor
 * AI-powered code refactoring
 */
export async function POST(req: NextRequest) {
    try {
        const { code, instruction } = await req.json();

        if (!code || typeof code !== 'string') {
            return NextResponse.json(
                { error: 'Code is required' },
                { status: 400 }
            );
        }

        const refactorInstruction = instruction || 'コードを整理し、可読性を向上させてください';

        const prompt = `
あなたは優秀なPythonプログラマーです。以下のコードをリファクタリングしてください。

【指示】
${refactorInstruction}

【元のコード】
${code}

【出力フォーマット】
{
    "refactoredCode": "リファクタリング後のコード",
    "explanation": "何を変更したかの説明（日本語）",
    "improvements": ["改善点1", "改善点2"]
}

重要:
- Pythonの規約（PEP8）に従う
- 変数名を意味のあるものにする
- 不要なコードを削除
- コメントを適切に追加
- 有効なJSONのみを返す
`;

        const apiKey = process.env.GEMINI_API_KEY;

        if (!apiKey) {
            return NextResponse.json({
                refactoredCode: code,
                explanation: 'APIキーが設定されていないため、リファクタリングをスキップしました',
                improvements: []
            });
        }

        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: prompt }] }],
                    generationConfig: {
                        temperature: 0.3,
                        maxOutputTokens: 8192
                    }
                })
            }
        );

        if (!response.ok) {
            throw new Error(`Gemini API error: ${response.status}`);
        }

        const data = await response.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '';

        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            throw new Error('Failed to parse AI response');
        }

        const result = JSON.parse(jsonMatch[0]);
        return NextResponse.json(result);

    } catch (error: any) {
        console.error('Refactor error:', error);
        return NextResponse.json(
            { error: error.message || 'Refactoring failed' },
            { status: 500 }
        );
    }
}
