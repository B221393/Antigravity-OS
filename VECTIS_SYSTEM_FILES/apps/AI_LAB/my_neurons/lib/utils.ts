export function generateFilename(title?: string): string {
    const today = new Date().toISOString().split('T')[0];
    if (!title || title.trim() === '') {
        return `${today}-random-thought.md`;
    }
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    return `${today}-${slug}.md`;
}
