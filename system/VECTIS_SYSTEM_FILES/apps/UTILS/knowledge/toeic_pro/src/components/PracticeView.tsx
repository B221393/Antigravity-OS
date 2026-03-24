import React, { useState, useEffect } from 'react';
import {
    Headphones,
    Sparkles,
    CheckCircle,
    XCircle,
    Target
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GeminiService } from '../services/GeminiService';
import { PersistenceService } from '../services/PersistenceService';
import type { TOEICPart, TOEICQuestion, SubQuestion } from '../types/toeic';

const PART_LABELS: Record<TOEICPart, string> = {
    P1: 'Photographs',
    P2: 'Question-Response',
    P3: 'Conversations',
    P4: 'Short Talks',
    P5: 'Incomplete Sentences',
    P6: 'Text Completion',
    P7: 'Reading Comprehension'
};

export default function PracticeView({ onUpdate }: { onUpdate: () => void }) {
    const [part, setPart] = useState<TOEICPart>('P1');
    const [loading, setLoading] = useState(false);
    const [question, setQuestion] = useState<TOEICQuestion | null>(null);
    const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
    const [isCorrects, setIsCorrects] = useState<Record<string, boolean>>({});
    const [isIntensive, setIsIntensive] = useState(false);

    const speak = (text: string) => {
        window.speechSynthesis.cancel();
        const segments = text.split(/(?=[MW]:)/);
        const voices = window.speechSynthesis.getVoices();
        const maleVoice = voices.find(v => v.lang.startsWith('en') && (v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('guy') || v.name.toLowerCase().includes('google us english'))) || voices.find(v => v.lang.startsWith('en'));
        const femaleVoice = voices.find(v => v.lang.startsWith('en') && (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('samantha') || v.name.toLowerCase().includes('google uk english female'))) || voices.find(v => v.lang.startsWith('en'));

        let delay = 0;
        segments.forEach(segment => {
            setTimeout(() => {
                const utterance = new SpeechSynthesisUtterance(segment.replace(/^[MW]:\s*/, ''));
                utterance.lang = 'en-US';
                utterance.rate = 0.9;

                if (segment.startsWith('M:')) utterance.voice = maleVoice || null;
                else if (segment.startsWith('W:')) utterance.voice = femaleVoice || null;
                else utterance.voice = femaleVoice || null;

                window.speechSynthesis.speak(utterance);
            }, delay);
            delay += segment.length * 60; // Heuristic
        });
    };

    const handleGenerate = async () => {
        setLoading(true);
        setQuestion(null);
        setSelectedAnswers({});
        setIsCorrects({});
        try {
            const scene = await GeminiService.generateScene(part);
            const q = await GeminiService.generateQuestion(part, scene, isIntensive);
            setQuestion(q);
            if ((['P1', 'P2', 'P3', 'P4'].includes(part)) && q.script) {
                setTimeout(() => speak(q.script!), 1000);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const onOptionSelect = (qIdx: string | number, optIdx: number, correctIdx: number) => {
        if (selectedAnswers[qIdx] !== undefined) return;

        const isCorrect = optIdx === correctIdx;
        const newSelected = { ...selectedAnswers, [qIdx]: optIdx };
        const newCorrects = { ...isCorrects, [qIdx]: isCorrect };

        setSelectedAnswers(newSelected);
        setIsCorrects(newCorrects);

        // If it's a single question or the last in a set, persist
        const totalSub = question?.questions?.length || 1;
        if (Object.keys(newSelected).length === totalSub) {
            const updatedQ = {
                ...question!,
                userAnswer: newSelected,
                isCorrect: totalSub === 1 ? isCorrect : newCorrects
            };
            PersistenceService.saveQuestion(updatedQ);
            onUpdate();
        }
    };

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h1 style={{ fontSize: '2.5em', marginBottom: '8px' }}>Active Training</h1>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        {(Object.keys(PART_LABELS) as TOEICPart[]).map(p => (
                            <button
                                key={p}
                                className={`stats-badge ${part === p ? 'active' : ''}`}
                                style={{ cursor: 'pointer', border: 'none', opacity: part === p ? 1 : 0.4, transition: '0.2s' }}
                                onClick={() => setPart(p)}
                            >
                                {p}
                            </button>
                        ))}
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <label style={{ fontSize: '0.8em', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                        <input type="checkbox" checked={isIntensive} onChange={e => setIsIntensive(e.target.checked)} />
                        Intensive Study
                    </label>
                    <button className="btn-primary" onClick={handleGenerate} disabled={loading}>
                        {loading ? 'GENERATING...' : 'NEW SESSION'}
                    </button>
                </div>
            </header>

            <AnimatePresence mode="wait">
                {loading ? (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="glass-card" style={{ textAlign: 'center', padding: '100px 0' }}>
                        <Sparkles size={48} className="spin" color="var(--accent-primary)" style={{ marginBottom: '24px' }} />
                        <h2 style={{ fontFamily: 'var(--font-display)' }}>Drafting Professional Scenario...</h2>
                        <p style={{ color: 'var(--text-secondary)' }}>Gemini AI is constructing a relevant business context.</p>
                    </motion.div>
                ) : question ? (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card">
                        {/* Visual Content */}
                        {question.imageUrl && (
                            <div style={{ marginBottom: '30px', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}>
                                <img src={question.imageUrl} alt="Scenario" style={{ width: '100%', height: 'auto', display: 'block' }} />
                            </div>
                        )}

                        {/* Script / Passage Toggle */}
                        {question.passage && <div style={{ background: 'rgba(255,255,255,0.03)', padding: '24px', borderRadius: '16px', marginBottom: '30px', fontSize: '1.1em', lineHeight: 1.6, color: '#DDD' }}>{question.passage}</div>}

                        {question.script && (
                            <div style={{ marginBottom: '30px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '16px', background: 'rgba(0, 242, 254, 0.05)', borderRadius: '12px', marginBottom: '16px' }}>
                                    <button
                                        onClick={() => speak(question.script!)}
                                        className="btn-primary"
                                        style={{ width: '40px', height: '40px', padding: 0, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                    >
                                        <Headphones size={20} color="#000" />
                                    </button>
                                    <div style={{ fontSize: '0.85em', fontWeight: 600 }}>Audio Source Available</div>
                                    <div style={{ flex: 1, height: '2px', background: 'rgba(255,255,255,0.05)', borderRadius: '1px' }}></div>
                                </div>
                                <AnimatePresence>
                                    {(Object.keys(selectedAnswers).length === (question.questions?.length || 1)) && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            style={{ background: 'rgba(0,0,0,0.2)', borderRadius: '12px', padding: '20px', border: '1px solid var(--border-glass)' }}
                                        >
                                            <div style={{ fontSize: '0.8em', color: 'var(--accent-primary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 700 }}>Transcript Log</div>
                                            <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: '#eee', marginBottom: '16px', fontSize: '0.95em' }}>{question.script}</p>

                                            {question.script_translation && (
                                                <>
                                                    <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)', margin: '12px 0' }}></div>
                                                    <div style={{ fontSize: '0.8em', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 700 }}>Translation</div>
                                                    <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: '#ccc', fontSize: '0.9em' }}>{question.script_translation}</p>
                                                </>
                                            )}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        )}

                        {/* Questions Rendering */}
                        {(question.questions || [{ ...question, id: 'main' }]).map((q: any, idx) => {
                            const qId = q.id || idx;
                            const isAnswered = selectedAnswers[qId] !== undefined;

                            return (
                                <div key={qId} style={{ marginBottom: '40px' }}>
                                    <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
                                        <div className="stats-badge" style={{ height: 'fit-content' }}>Q{idx + 1}</div>
                                        <h2 style={{ fontSize: '1.3em', flex: 1 }}>
                                            {(['P1', 'P2'].includes(part) && !isAnswered) ? '(Please listen to the audio)' : q.question}
                                        </h2>
                                    </div>

                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                        {q.options.map((opt: string, optIdx: number) => {
                                            const isSelected = selectedAnswers[qId] === optIdx;
                                            const isCorrect = optIdx === q.correctAnswer;
                                            const state = isAnswered ? (isCorrect ? 'correct' : (isSelected ? 'wrong' : '')) : '';

                                            return (
                                                <button
                                                    key={optIdx}
                                                    onClick={() => onOptionSelect(qId, optIdx, q.correctAnswer)}
                                                    className="btn-outline"
                                                    style={{
                                                        textAlign: 'left',
                                                        padding: '16px 20px',
                                                        borderColor: state === 'correct' ? 'var(--accent-success)' : (state === 'wrong' ? 'var(--accent-error)' : 'var(--border-glass)'),
                                                        background: state === 'correct' ? 'rgba(0, 255, 163, 0.05)' : (state === 'wrong' ? 'rgba(255, 51, 102, 0.05)' : ''),
                                                        color: state ? '#FFF' : 'var(--text-secondary)'
                                                    }}
                                                >
                                                    <span style={{ fontWeight: 700, marginRight: '10px', color: state === 'correct' ? 'var(--accent-success)' : (state === 'wrong' ? 'var(--accent-error)' : 'var(--accent-primary)') }}>
                                                        ({String.fromCharCode(65 + optIdx)})
                                                    </span>
                                                    {(['P1', 'P2'].includes(part) && !isAnswered) ? '' : opt.replace(/^\([A-D]\)\s*/, '')}
                                                </button>
                                            );
                                        })}
                                    </div>

                                    <AnimatePresence>
                                        {isAnswered && (
                                            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} style={{ marginTop: '24px', padding: '20px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', borderLeft: `3px solid ${isCorrects[qId] ? 'var(--accent-success)' : 'var(--accent-error)'}` }}>
                                                <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', color: isCorrects[qId] ? 'var(--accent-success)' : 'var(--accent-error)', fontSize: '0.9em', fontWeight: 700 }}>
                                                    {isCorrects[qId] ? <CheckCircle size={16} /> : <XCircle size={16} />}
                                                    {isCorrects[qId] ? 'PROFICIENT' : 'IMPROVEMENT NECESSARY'}
                                                </div>
                                                <p style={{ lineHeight: 1.6, marginBottom: '16px' }}>{q.explanation}</p>
                                                <div style={{ fontSize: '0.85em', color: 'var(--text-secondary)', fontStyle: 'italic', paddingLeft: '12px', borderLeft: '1px solid rgba(255,255,255,0.1)' }}>{q.translation}</div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            );
                        })}
                    </motion.div>
                ) : (
                    <div className="glass-card" style={{ textAlign: 'center', padding: '80px 0' }}>
                        <div style={{ color: 'rgba(255,255,255,0.1)', marginBottom: '24px' }}><Target size={64} /></div>
                        <h2 style={{ color: 'var(--text-secondary)' }}>Ready for Departure</h2>
                        <p>Select a module and initialize your training session.</p>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
