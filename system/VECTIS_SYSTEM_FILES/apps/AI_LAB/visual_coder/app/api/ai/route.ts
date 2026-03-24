
import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: Request) {
    try {
        const { prompt } = await request.json();

        if (!prompt) {
            return NextResponse.json({ error: 'Prompt is required' }, { status: 400 });
        }

        const scriptPath = path.join(process.cwd(), 'ask_ai.py');

        // Spawn python process
        const pythonProcess = spawn('python', [scriptPath, prompt]);

        let result = '';
        let error = '';

        for await (const chunk of pythonProcess.stdout) {
            result += chunk.toString();
        }

        for await (const chunk of pythonProcess.stderr) {
            error += chunk.toString();
        }

        // Checking exit code not strictly necessary if we got stdout, but good practice
        // However, we just return what we got.

        if (!result && error) {
            return NextResponse.json({ code: `# Error generating code: ${error}` });
        }

        return NextResponse.json({ code: result || '# No response from AI' });

    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
