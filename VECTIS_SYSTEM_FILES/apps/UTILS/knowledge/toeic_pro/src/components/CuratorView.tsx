import React from 'react';
import { ExternalLink, Youtube, CheckCircle2 } from 'lucide-react';
import { CURATED_YOUTUBE_RESOURCES } from '../services/CuratorService';

export default function CuratorView() {
    return (
        <div style={{ maxWidth: '1200px' }}>
            <header style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2.5em', marginBottom: '8px' }}>Intelligence Hub</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Curated high-impact strategies from global TOEIC experts.</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
                {CURATED_YOUTUBE_RESOURCES.map(res => (
                    <div key={res.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div className="stats-badge">{res.part}</div>
                            <a href={res.url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-primary)' }}>
                                <ExternalLink size={18} />
                            </a>
                        </div>

                        <div>
                            <h3 style={{ marginBottom: '4px', fontSize: '1.2em' }}>{res.title}</h3>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '0.85em' }}>
                                <Youtube size={14} /> {res.channel}
                            </div>
                        </div>

                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9em', lineHeight: 1.5 }}>
                            {res.description}
                        </p>

                        <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '12px', padding: '16px' }}>
                            <div style={{ fontSize: '0.75em', fontWeight: 700, textTransform: 'uppercase', marginBottom: '12px', color: 'rgba(255,255,255,0.4)' }}>Critical Insights</div>
                            {res.keyTakeaways.map((task, idx) => (
                                <div key={idx} style={{ display: 'flex', gap: '10px', marginBottom: '10px', fontSize: '0.85em', color: 'var(--text-primary)' }}>
                                    <CheckCircle2 size={14} color="var(--accent-success)" style={{ marginTop: '2px' }} />
                                    <span>{task}</span>
                                </div>
                            ))}
                        </div>

                        <button className="btn-outline" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }} onClick={() => window.open(res.url, '_blank')}>
                            Initialize Training <Youtube size={16} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
