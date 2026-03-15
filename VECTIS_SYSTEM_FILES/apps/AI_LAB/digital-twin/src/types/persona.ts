export interface PersonaData {
    profile: {
        name: string;
        university: string;
        department: string;
        location: string;
        photoUrl?: string; // For the "copy" visualization
    };
    attributes: {
        strengths: string[];
        weaknesses: string[];
        values: string[]; // Job hunting axis (就活の軸)
        skills: string[];
    };
    episodes: Episode[];
    gaps: string[]; // Detected missing information
}

export interface Episode {
    id: string;
    title: string;
    description: string;
    tags: string[]; // e.g., "Leadership", "Failure", "Research"
    impact: number; // 1-10 scale of importance
}

export const analyzePersona = (data: PersonaData): { score: number; missing: string[] } => {
    let score = 0;
    const missing: string[] = [];

    // Basic Profile Check
    if (data.profile.name) score += 10;
    if (data.profile.university) score += 10;

    // Attributes Check
    if (data.attributes.strengths.length >= 3) score += 15;
    else missing.push("強みが3つ未満です");

    if (data.attributes.values.length >= 1) score += 15;
    else missing.push("就活の軸が未定義です");

    // Episodes Check
    if (data.episodes.length >= 3) score += 30;
    else missing.push("エピソードが不足しています (目標: 3つ)");

    const hasFailureStory = data.episodes.some(e => e.tags.includes("Failure") || e.tags.includes("挫折"));
    if (hasFailureStory) score += 20;
    else missing.push("挫折経験のエピソードがありません");

    return { score: Math.min(100, score), missing };
};
