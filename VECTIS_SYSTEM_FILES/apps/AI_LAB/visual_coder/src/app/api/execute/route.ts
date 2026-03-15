import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { writeFileSync, unlinkSync, mkdirSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { randomUUID } from 'crypto';

const TIMEOUT_MS = 10000; // 10 second timeout
const MAX_OUTPUT_LENGTH = 50000; // 50KB max output

export async function POST(req: NextRequest) {
    try {
        const { code } = await req.json();

        if (!code || typeof code !== 'string') {
            return NextResponse.json({ error: 'No code provided' }, { status: 400 });
        }

        // Create temp file
        const tempDir = join(tmpdir(), 'visual_coder');
        mkdirSync(tempDir, { recursive: true });
        const tempFile = join(tempDir, `run_${randomUUID()}.py`);
        writeFileSync(tempFile, code, 'utf-8');

        const result = await new Promise<{ stdout: string; stderr: string; exitCode: number | null; timedOut: boolean }>((resolve) => {
            let stdout = '';
            let stderr = '';
            let timedOut = false;

            const proc = spawn('python', [tempFile], {
                timeout: TIMEOUT_MS,
                env: { ...process.env },
                cwd: tempDir,
            });

            proc.stdout.on('data', (data) => {
                stdout += data.toString();
                if (stdout.length > MAX_OUTPUT_LENGTH) {
                    stdout = stdout.slice(0, MAX_OUTPUT_LENGTH) + '\n... [output truncated]';
                    proc.kill();
                }
            });

            proc.stderr.on('data', (data) => {
                stderr += data.toString();
                if (stderr.length > MAX_OUTPUT_LENGTH) {
                    stderr = stderr.slice(0, MAX_OUTPUT_LENGTH) + '\n... [output truncated]';
                    proc.kill();
                }
            });

            proc.on('error', (err) => {
                stderr += `Process error: ${err.message}`;
                resolve({ stdout, stderr, exitCode: 1, timedOut: false });
            });

            proc.on('close', (exitCode) => {
                resolve({ stdout, stderr, exitCode, timedOut });
            });

            // Manual timeout handling
            setTimeout(() => {
                timedOut = true;
                proc.kill('SIGTERM');
                setTimeout(() => proc.kill('SIGKILL'), 1000);
            }, TIMEOUT_MS);
        });

        // Cleanup temp file
        try { unlinkSync(tempFile); } catch { /* ignore */ }

        return NextResponse.json({
            stdout: result.stdout,
            stderr: result.stderr,
            exitCode: result.exitCode,
            timedOut: result.timedOut,
            timestamp: new Date().toISOString(),
        });

    } catch (error: any) {
        return NextResponse.json({
            error: error.message || 'Execution failed',
        }, { status: 500 });
    }
}
