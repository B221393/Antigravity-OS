
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Restrict access to VECTIS_SYSTEM_FILES for safety
const BASE_DIR = path.resolve(process.cwd(), '../../../');

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const relPath = searchParams.get('path') || '';
    const operation = searchParams.get('op') || 'list';

    const fullPath = path.join(BASE_DIR, relPath);

    // Security check: ensure we don't go above BASE_DIR
    if (!fullPath.startsWith(BASE_DIR)) {
        return NextResponse.json({ error: 'Access denied' }, { status: 403 });
    }

    try {
        if (operation === 'read') {
            if (fs.statSync(fullPath).isFile()) {
                const content = fs.readFileSync(fullPath, 'utf-8');
                return NextResponse.json({ content });
            } else {
                return NextResponse.json({ error: 'Not a file' }, { status: 400 });
            }
        }
        else {
            // LIST
            const items = fs.readdirSync(fullPath);
            const fileList = items.map(name => {
                try {
                    const itemPath = path.join(fullPath, name);
                    const stats = fs.statSync(itemPath);
                    return {
                        name,
                        isDirectory: stats.isDirectory(),
                        path: path.relative(BASE_DIR, itemPath).replace(/\\/g, '/')
                    };
                } catch {
                    return null;
                }
            }).filter(Boolean);

            return NextResponse.json({ files: fileList });
        }
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
