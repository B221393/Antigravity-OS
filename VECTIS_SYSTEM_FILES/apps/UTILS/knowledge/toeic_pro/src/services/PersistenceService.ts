import type { TOEICQuestion, UserStats, TOEICPart } from '../types/toeic';

const STORAGE_KEY = 'VECTIS_TOEIC_PRO_DATA';

export class PersistenceService {
    static getStats(): UserStats {
        const data = localStorage.getItem(STORAGE_KEY);
        if (!data) {
            return {
                totalQuestions: 0,
                correctQuestions: 0,
                partStats: {
                    P1: { total: 0, correct: 0 },
                    P2: { total: 0, correct: 0 },
                    P3: { total: 0, correct: 0 },
                    P4: { total: 0, correct: 0 },
                    P5: { total: 0, correct: 0 },
                    P6: { total: 0, correct: 0 },
                    P7: { total: 0, correct: 0 }
                },
                history: [],
                weeklyGoal: 35
            };
        }
        return JSON.parse(data);
    }

    static saveQuestion(question: TOEICQuestion) {
        const stats = this.getStats();

        // Add to history (keep last 100 for storage limits)
        stats.history = [question, ...stats.history].slice(0, 100);

        // Update counters
        stats.totalQuestions += 1;
        const part = question.part as TOEICPart;
        stats.partStats[part].total += 1;

        if (question.isCorrect === true) {
            stats.correctQuestions += 1;
            stats.partStats[part].correct += 1;
        } else if (typeof question.isCorrect === 'object') {
            // Support multi-question sets
            const values = Object.values(question.isCorrect);
            const correctInSet = values.filter(v => v).length;
            stats.correctQuestions += correctInSet;
            stats.partStats[part].correct += correctInSet;

            // Adjust total for sets
            stats.totalQuestions += (values.length - 1);
            stats.partStats[part].total += (values.length - 1);
        }

        localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
    }

    static clearHistory() {
        const stats = this.getStats();
        stats.history = [];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
    }
}
