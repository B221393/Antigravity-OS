import { processMarkdown, buildLinkMap, getRelatedNotes } from '@/lib/markdown-engine';
import { generateFilename } from '@/lib/utils';
import path from 'path';
import fs from 'fs';

const FIXTURES_DIR = path.join(process.cwd(), '__tests__/fixtures');

describe('My Neurons Core Engine', () => {
    let linkMap: any;

    beforeAll(async () => {
        // Ensure fixtures exist (they are created by the subagent step)
        if (!fs.existsSync(FIXTURES_DIR)) {
            throw new Error("Fixtures dir not found");
        }
        linkMap = await buildLinkMap(FIXTURES_DIR);
    });

    test('Feature 1: Dynamic Auto-Linking', async () => {
        const wittgensteinPath = path.join(FIXTURES_DIR, 'wittgenstein.md');
        // processMarkdown returns { content, data }
        // content should be HTML string with links
        const { content } = await processMarkdown(wittgensteinPath, linkMap);

        // Expect "Language Game" to be linked
        // We expect the parser to convert "Language Game" text into a link to its slug
        // Slug for "Language Game" -> "language-game"

        // The link format should be standard HTML <a> or markdown link, but processed to HTML usually
        expect(content).toContain('href="/notes/language-game"');

        // Check for Context link (English alias matching Japanese Title or vice versa)
        // "コンテキスト" should link to "context.md" (slug: context)
        expect(content).toMatch(/href="\/notes\/context".*?コンテキスト/);
    });

    test('Feature 2: The Vibe Hop', async () => {
        // We pass the SLUG of the current note
        const related = await getRelatedNotes('wittgenstein', FIXTURES_DIR);
        // Wittgenstein tags: #Philosophy
        // Language Game tags: #Philosophy, #Linguistics
        // Otani Emiri: #Idol

        // Should suggest Language Game due to shared tag
        const titles = related.map(r => r.title);
        expect(titles).toContain('Language Game');
        expect(titles).not.toContain('大谷映美里'); // Unrelated
    });

    test('Feature 3: Quick Capture (Logic)', () => {
        // Logic only: auto filename generation
        const filename = generateFilename('My new thought');

        const today = new Date().toISOString().split('T')[0];
        expect(filename).toBe(`${today}-my-new-thought.md`);

        const random = generateFilename('');
        expect(random).toMatch(new RegExp(`${today}-random-thought`));
        // User requested: 2026-01-19-random-thought.md
    });
});
