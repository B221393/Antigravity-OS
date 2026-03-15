import React from 'react';
import { History, XCircle, CheckCircle, ArrowRight } from 'lucide-react';
import type { UserStats } from '../types/toeic';

export default function ReviewView({ stats }: { stats: UserStats }) {
    const incorrectQuestions = stats.history.filter(q => {
        if (typeof q.isCorrect === 'boolean') return !q.isCorrect;
        if (typeof q.isCorrect === 'object') return Object.values(q.isCorrect).some(v => !v);
        return false;
    });

    return (
        <div style={{ maxWidth: '1000px' }}>
            <header style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2.5em', marginBottom: '8px' }}>Review Center</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Focus on past discrepancies to solidify your knowledge base.</p>
            </header>

            {incorrectQuestions.length === 0 ? (
                <div className="glass-card" style={{ textAlign: 'center', padding: '60px' }}>
                    <CheckCircle size={48} color="var(--accent-success)" style={{ marginBottom: '20px' }} />
                    <h3>Optimization Complete</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>No incorrect items found in your recent history.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {incorrectQuestions.map(q => (
                        <div key={q.id} className="glass-card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', alignItems: 'center' }}>
                                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                                    <div className="stats-badge" style={{ background: 'rgba(255, 51, 102, 0.1)', color: 'var(--accent-error)' }}>{q.part}</div>
                                    <span style={{ fontSize: '0.8em', color: 'var(--text-secondary)' }}>{new Date(q.timestamp).toLocaleDateString()}</span>
                                </div>
                                <div style={{ fontSize: '0.75em', color: 'rgba(255,255,255,0.2)' }}>ID: {q.id}</div>
                            </div>

                            {/* Context: Image, Script, or Passage */}
                            <div style={{ marginBottom: '24px', paddingBottom: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                {q.imageUrl && (
                                    <div style={{ marginBottom: '16px', borderRadius: '8px', overflow: 'hidden', maxWidth: '300px' }}>
                                        <img src={q.imageUrl} alt="Context" style={{ width: '100%', height: 'auto', display: 'block' }} />
                                    </div>
                                )}
                                {q.passage && (
                                    <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '8px', marginBottom: '16px', fontSize: '0.9em', lineHeight: 1.6, color: '#DDD', maxHeight: '200px', overflowY: 'auto' }}>
                                        {q.passage}
                                    </div>
                                )}
                                {q.script && (
                                    <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', fontSize: '0.9em' }}>
                                        <div style={{ fontSize: '0.75em', color: 'var(--accent-primary)', marginBottom: '4px', textTransform: 'uppercase' }}>Transcript</div>
                                        <div style={{ whiteSpace: 'pre-wrap', color: '#EEE', lineHeight: 1.5 }}>{q.script}</div>
                                        {q.script_translation && (
                                            <>
                                                <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)', margin: '8px 0' }}></div>
                                                <div style={{ fontSize: '0.8em', color: '#CCC' }}>{q.script_translation}</div>
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* Questions Logic */}
                            {q.questions ? (
                                // Multi-question handling (P3, P4, P6, P7)
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                                    {q.questions.map((subQ, sIdx) => {
                                        const isSubCorrect = typeof q.isCorrect === 'object' ? q.isCorrect[subQ.id] : false;
                                        if (isSubCorrect) return null; // Optionally hide correct sub-questions or show them differently

                                        return (
                                            <div key={sIdx}>
                                                <h4 style={{ fontSize: '1em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <XCircle size={16} color="var(--accent-error)" />
                                                    {subQ.question}
                                                </h4>
                                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginBottom: '12px' }}>
                                                    {subQ.options.map((opt, oIdx) => (
                                                        <div key={oIdx} style={{
                                                            padding: '8px 12px', borderRadius: '6px', fontSize: '0.85em',
                                                            border: oIdx === subQ.correctAnswer ? '1px solid var(--accent-success)' : '1px solid rgba(255,255,255,0.05)',
                                                            background: oIdx === subQ.correctAnswer ? 'rgba(0, 255, 163, 0.05)' : 'transparent',
                                                            color: oIdx === subQ.correctAnswer ? 'var(--accent-success)' : 'var(--text-secondary)'
                                                        }}>
                                                            ({String.fromCharCode(65 + oIdx)}) {opt}
                                                        </div>
                                                    ))}
                                                </div>
                                                <div style={{ fontSize: '0.85em', color: '#BBB', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px' }}>
                                                    <div style={{ marginBottom: '4px' }}>{subQ.explanation}</div>
                                                    <div style={{ fontSize: '0.9em', color: 'rgba(255,255,255,0.4)', fontStyle: 'italic' }}>{subQ.translation}</div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                // Single question handling (P1, P2, P5)
                                <div>
                                    <h3 style={{ fontSize: '1.1em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <XCircle size={20} color="var(--accent-error)" />
                                        {q.question}
                                    </h3>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginBottom: '16px' }}>
                                        {q.options?.map((opt, idx) => (
                                            <div key={idx} style={{
                                                padding: '10px 16px', borderRadius: '8px', fontSize: '0.9em',
                                                border: idx === q.correctAnswer ? '1px solid var(--accent-success)' : '1px solid rgba(255,255,255,0.05)',
                                                background: idx === q.correctAnswer ? 'rgba(0, 255, 163, 0.05)' : 'transparent',
                                                color: idx === q.correctAnswer ? 'var(--accent-success)' : 'var(--text-secondary)'
                                            }}>
                                                ({String.fromCharCode(65 + idx)}) {opt}
                                            </div>
                                        )) || <div style={{ color: 'red' }}>Data Error: Options missing</div>}
                                    </div>
                                    <div style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', borderLeft: '3px solid var(--accent-primary)' }}>
                                        <p style={{ fontSize: '0.9em', lineHeight: 1.6, marginBottom: '10px' }}>{q.explanation}</p>
                                        <div style={{ fontSize: '0.8em', color: 'rgba(255,255,255,0.4)', fontStyle: 'italic' }}>{q.translation}</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
