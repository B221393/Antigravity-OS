export interface SubQuestion {
    id: string;
    question: string;
    options: string[];
    correctAnswer: number;
    explanation: string;
    translation: string;
}

export interface TOEICQuestion {
    id: string;
    part: TOEICPart;
    question: string;
    options: string[];
    correctAnswer: number;
    explanation: string;
    translation: string;
    script?: string;
    script_translation?: string;
    passage?: string;
    imageUrl?: string;
    isIntensive?: boolean;
    questions?: SubQuestion[]; // For P3, P4, P6, P7
    timestamp: number;
    userAnswer?: number | Record<string, number>;
    isCorrect?: boolean | Record<string, boolean>;
}

export interface TOEICScene {
    scene_description: string;
    image_prompt: string;
    image_url?: string;
}

export type TOEICPart = 'P1' | 'P2' | 'P3' | 'P4' | 'P5' | 'P6' | 'P7';

export interface UserStats {
    totalQuestions: number;
    correctQuestions: number;
    partStats: Record<TOEICPart, { total: number; correct: number }>;
    history: TOEICQuestion[];
    weeklyGoal: number;
}

export interface CuratedResource {
    id: string;
    title: string;
    channel: string;
    url: string;
    part: TOEICPart | 'General';
    description: string;
    keyTakeaways: string[];
}
