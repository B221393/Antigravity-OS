import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/decompile
 * Decompile Python code to Visual Nodes using AI
 */
export async function POST(req: NextRequest) {
    try {
        const { code } = await req.json();

        if (!code || typeof code !== 'string') {
            return NextResponse.json(
                { error: 'Code is required' },
                { status: 400 }
            );
        }

        // AI Prompt for decompilation
        const prompt = `
あなたはPythonコードをビジュアルプログラミングのノードに変換するエキスパートです。

以下のPythonコードを解析し、ビジュアルノードとエッジのJSON配列を生成してください。

【Pythonコード】
${code}

【出力フォーマット】
{
    "nodes": [
        {
            "id": "unique-id",
            "type": "default",
            "position": { "x": number, "y": number },
            "data": {
                "label": "表示ラベル",
                "realType": "print|var|import|function|if|for|python",
                "value": "値（printやvarの場合）",
                "variable": "変数名（varの場合）",
                "code": "生のコード（pythonブロックの場合）",
                "condition": "条件式（ifの場合）"
            }
        }
    ],
    "edges": [
        {
            "id": "edge-id",
            "source": "source-node-id",
            "target": "target-node-id"
        }
    ]
}

重要:
- 最初のノードは必ずStartノード（type: "start"）にする
- ノードは上から下に100pxずつ配置（y: 50, 150, 250...）
- エッジは前のノードから次のノードへ繋げる
- 有効なJSONのみを返す
`;

        // Use Gemini API or fallback
        const apiKey = process.env.GEMINI_API_KEY;

        if (!apiKey) {
            // Fallback to client-side parser response format
            return NextResponse.json({
                error: 'No API key configured. Using client-side parsing.',
                fallback: true
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
                        temperature: 0.2,
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

        // Extract JSON from response
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            throw new Error('Failed to parse AI response');
        }

        const result = JSON.parse(jsonMatch[0]);
        return NextResponse.json(result);

    } catch (error: any) {
        console.error('Decompile error:', error);
        return NextResponse.json(
            { error: error.message || 'Decompilation failed', fallback: true },
            { status: 500 }
        );
    }
}
