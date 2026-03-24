import React from 'react';
import { Target, TrendingUp, CheckCircle, Clock } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import type { UserStats } from '../types/toeic';

export default function DashboardView({ stats }: { stats: UserStats }) {
    const chartData = Object.entries(stats.partStats).map(([part, s]) => ({
        name: part,
        accuracy: s.total > 0 ? Math.round((s.correct / s.total) * 100) : 0,
        count: s.total
    }));

    const COLORS = ['#00f2fe', '#00f2fe', '#7000ff', '#7000ff', '#00ffa3', '#00ffa3', '#00ffa3'];

    return (
        <div style={{ maxWidth: '1200px' }}>
            <header style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2.5em', marginBottom: '8px' }}>Executive Performance</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Comprehensive analysis of your TOEIC proficiency levels.</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '40px' }}>
                <div className="glass-card">
                    <div style={{ color: 'var(--accent-primary)', marginBottom: '12px' }}><Target size={24} /></div>
                    <div style={{ fontSize: '2em', fontWeight: 700 }}>{stats.totalQuestions}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>Total Inquiries</div>
                </div>
                <div className="glass-card">
                    <div style={{ color: 'var(--accent-success)', marginBottom: '12px' }}><CheckCircle size={24} /></div>
                    <div style={{ fontSize: '2em', fontWeight: 700 }}>
                        {stats.totalQuestions > 0 ? Math.round((stats.correctQuestions / stats.totalQuestions) * 100) : 0}%
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>Average Accuracy</div>
                </div>
                <div className="glass-card">
                    <div style={{ color: 'var(--accent-secondary)', marginBottom: '12px' }}><TrendingUp size={24} /></div>
                    <div style={{ fontSize: '2em', fontWeight: 700 }}>{stats.history.length}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>Retained Scenarios</div>
                </div>
                <div className="glass-card">
                    <div style={{ color: 'var(--accent-warning)', marginBottom: '12px' }}><Clock size={24} /></div>
                    <div style={{ fontSize: '2em', fontWeight: 700 }}>{stats.weeklyGoal}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>Weekly Goal</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
                <div className="glass-card" style={{ height: '400px' }}>
                    <h3 style={{ marginBottom: '24px' }}>Accuracy by Module (Part 1-7)</h3>
                    <ResponsiveContainer width="100%" height="80%">
                        <BarChart data={chartData}>
                            <XAxis dataKey="name" stroke="#555" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#555" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                            <Tooltip
                                contentStyle={{ background: '#111', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px' }}
                                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                            />
                            <Bar dataKey="accuracy" radius={[6, 6, 0, 0]}>
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="glass-card">
                    <h3 style={{ marginBottom: '20px' }}>Recent Performance</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {stats.history.slice(0, 5).map((q, idx) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <div style={{
                                    width: '32px', height: '32px', borderRadius: '8px',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    background: q.isCorrect === true ? 'rgba(0, 255, 163, 0.1)' : 'rgba(255, 51, 102, 0.1)',
                                    color: q.isCorrect === true ? 'var(--accent-success)' : 'var(--accent-error)'
                                }}>
                                    {q.part}
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: '0.85em', fontWeight: 500 }}>Question {q.id.slice(0, 4)}</div>
                                    <div style={{ fontSize: '0.75em', color: 'var(--text-secondary)' }}>{new Date(q.timestamp).toLocaleTimeString()}</div>
                                </div>
                                <div className="stats-badge" style={{
                                    background: q.isCorrect === true ? 'rgba(0, 255, 163, 0.1)' : 'rgba(255, 51, 102, 0.1)',
                                    color: q.isCorrect === true ? 'var(--accent-success)' : 'var(--accent-error)'
                                }}>
                                    {q.isCorrect === true ? 'PASS' : 'FAIL'}
                                </div>
                            </div>
                        ))}
                        {stats.history.length === 0 && <p style={{ color: 'var(--text-secondary)', fontSize: '0.9em' }}>No practice history found.</p>}
                    </div>
                </div>
            </div>
        </div>
    );
}
