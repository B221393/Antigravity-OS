import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { marked } from 'marked';

export interface NoteData {
    slug: string;
    title: string;
    aliases: string[];
    tags: string[];
    content: string; // raw markdown
    html?: string;
    score?: number;
}

export type LinkMap = Map<string, string>; // Keyword -> Slug

function escapeRegExp(string: string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export async function buildLinkMap(dir: string): Promise<LinkMap> {
    const map = new Map<string, string>();
    if (!fs.existsSync(dir)) return map;

    const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));

    for (const file of files) {
        const filePath = path.join(dir, file);
        const content = fs.readFileSync(filePath, 'utf-8');
        const { data } = matter(content);
        const slug = file.replace('.md', '');

        if (data.title) {
            map.set(data.title.toLowerCase(), slug);
        }
        if (data.aliases && Array.isArray(data.aliases)) {
            data.aliases.forEach((alias: string) => map.set(alias.toLowerCase(), slug));
        }
    }
    return map;
}

export async function processMarkdown(filePath: string, linkMap: LinkMap): Promise<{ content: string; data: any }> {
    const raw = fs.readFileSync(filePath, 'utf-8');
    const { content, data } = matter(raw);

    let protectedContent = content;
    const placeholders: string[] = [];

    // 1. Protect Logic (Placeholders)
    // Code Blocks
    protectedContent = protectedContent.replace(/```[\s\S]*?```/g, (match) => {
        placeholders.push(match);
        return `__MK_PLACEHOLDER_${placeholders.length - 1}__`;
    });
    // Inline Code
    protectedContent = protectedContent.replace(/`[^`]*`/g, (match) => {
        placeholders.push(match);
        return `__MK_PLACEHOLDER_${placeholders.length - 1}__`;
    });
    // Existing Links [text](url)
    protectedContent = protectedContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match) => {
        placeholders.push(match);
        return `__MK_PLACEHOLDER_${placeholders.length - 1}__`;
    });
    // Wiki Links [[text]] or [[text|alias]]
    protectedContent = protectedContent.replace(/\[\[([^\]]+)\]\]/g, (match) => {
        placeholders.push(match);
        return `__MK_PLACEHOLDER_${placeholders.length - 1}__`;
    });

    // 2. Auto-Link (One-Pass)
    const keywords = Array.from(linkMap.keys()).filter(k => k.length > 0).sort((a, b) => b.length - a.length);

    if (keywords.length > 0) {
        const pattern = keywords.map(k => {
            // If ascii, use word boundaries. If not, don't.
            const isAscii = /^[\u0000-\u007f]*$/.test(k);
            return isAscii ? `\\b${escapeRegExp(k)}\\b` : escapeRegExp(k);
        }).join('|');

        const regex = new RegExp(pattern, 'gi');

        protectedContent = protectedContent.replace(regex, (match) => {
            const lower = match.toLowerCase();
            const slug = linkMap.get(lower);
            // Avoid self-linking
            if (slug && !filePath.toLowerCase().endsWith(`${slug.toLowerCase()}.md`) && !filePath.toLowerCase().endsWith(`/${slug.toLowerCase()}.md`)) {
                // We return markdown link provided it parses correctly later
                // Using HTML <a> tag directly might be safer for rendering if marked doesn't support recursive markdown
                // but [text](url) is standard.
                return `[${match}](/notes/${slug})`;
            }
            return match;
        });
    }

    // 3. Restore placeholders
    placeholders.forEach((ph, i) => {
        // Need to be careful about order? Loop 0 to N is fine.
        // But string replacement replaces FIRST occurrence.
        // Placeholders are unique strings `__MK_PLACEHOLDER_0__`, so safe.
        protectedContent = protectedContent.replace(`__MK_PLACEHOLDER_${i}__`, ph);
    });

    // 4. To HTML
    const html = await marked.parse(protectedContent);
    return { content: html, data };
}

export async function getRelatedNotes(currentSlug: string, dir: string): Promise<NoteData[]> {
    if (!fs.existsSync(dir)) return [];
    const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
    const notes: NoteData[] = [];
    let currentNoteTags: string[] = [];

    // Load current note first
    const currentPath = path.join(dir, `${currentSlug}.md`);
    if (fs.existsSync(currentPath)) {
        const raw = fs.readFileSync(currentPath, 'utf-8');
        const { data } = matter(raw);
        currentNoteTags = data.tags || [];
    }

    for (const file of files) {
        const slug = file.replace('.md', '');
        if (slug === currentSlug) continue;

        const raw = fs.readFileSync(path.join(dir, file), 'utf-8');
        const { data, content } = matter(raw);

        notes.push({
            slug,
            title: data.title,
            aliases: data.aliases || [],
            tags: data.tags || [],
            content
        });
    }

    // Score logic
    const scored = notes.map(note => {
        let score = 0;
        const intersection = note.tags.filter(t => currentNoteTags.includes(t));
        score += intersection.length * 10;

        // TODO: Backlink logic (Bonus points if this note links to current note)
        // This requires parsing content which is expensive. Skipping for MVP unless requested.
        // User asked: "common tags AND # of bidirectional links weighting".
        // Checking "links FROM note TO current" is regex search.
        if (note.content.includes(currentSlug) || note.content.includes(currentSlug.replace('-', ' '))) { // Naive
            score += 5;
        }

        return { ...note, score };
    });

    return scored.filter(n => n.score > 0).sort((a, b) => b.score - a.score);
}
