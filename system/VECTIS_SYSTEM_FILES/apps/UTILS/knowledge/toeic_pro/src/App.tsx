import React, { useState, useEffect } from 'react';
import {
    LayoutDashboard,
    Lightbulb,
    PlayCircle,
    History,
    Settings,
    ChevronRight,
    Headphones,
    BookOpen,
    Target,
    Trophy,
    ArrowRight,
    RotateCcw
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { PersistenceService } from './services/PersistenceService';
import { CURATED_YOUTUBE_RESOURCES } from './services/CuratorService';
import type { TOEICPart, TOEICQuestion, UserStats } from './types/toeic';

// Components
import PracticeView from './components/PracticeView';
import DashboardView from './components/DashboardView';
import CuratorView from './components/CuratorView';
import ReviewView from './components/ReviewView';

const NAVIGATION = [
    { id: 'dashboard', label: 'Performance', icon: LayoutDashboard },
    { id: 'strategy', label: 'Strategy Hub', icon: Lightbulb },
    { id: 'practice', label: 'Daily Practice', icon: PlayCircle },
    { id: 'review', label: 'Review Center', icon: History }
];

export default function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [stats, setStats] = useState<UserStats>(PersistenceService.getStats());

    const refreshStats = () => {
        setStats(PersistenceService.getStats());
    };

    return (
        <>
            <div className="bg-mesh" />
            <div className="app-container">
                {/* Sidebar */}
                <aside className="sidebar">
                    <div className="logo-container" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ background: 'var(--accent-primary)', width: '36px', height: '36px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Target size={22} color="#000" />
                        </div>
                        <div>
                            <div style={{ fontSize: '1.2em', fontWeight: 700, fontFamily: 'var(--font-display)' }}>TOEIC PRO</div>
                            <div style={{ fontSize: '0.6em', color: 'var(--accent-primary)', fontWeight: 700, letterSpacing: '0.1em' }}>VECTIS ELITE</div>
                        </div>
                    </div>

                    <nav style={{ flex: 1 }}>
                        <div style={{ fontSize: '0.7em', color: 'rgba(255,255,255,0.3)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '16px', paddingLeft: '16px' }}>Terminal Navigation</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            {NAVIGATION.map(item => (
                                <div
                                    key={item.id}
                                    className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                                    onClick={() => setActiveTab(item.id)}
                                >
                                    <item.icon size={20} />
                                    <span>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </nav>

                    <div className="glass-card" style={{ padding: '20px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                            <span style={{ fontSize: '0.8em', color: 'var(--text-secondary)' }}>Weekly Target</span>
                            <span style={{ fontSize: '0.8em', color: 'var(--accent-primary)' }}>{Math.round((stats.correctQuestions / stats.weeklyGoal) * 100)}%</span>
                        </div>
                        <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${Math.min(100, (stats.correctQuestions / stats.weeklyGoal) * 100)}%` }}
                                style={{ height: '100%', background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))' }}
                            />
                        </div>
                        <div style={{ marginTop: '12px', fontSize: '0.75em', color: 'var(--text-secondary)' }}>
                            {stats.correctQuestions} / {stats.weeklyGoal} items remaining
                        </div>
                    </div>
                </aside>

                {/* Main View */}
                <main className="main-view">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                        >
                            {activeTab === 'dashboard' && <DashboardView stats={stats} />}
                            {activeTab === 'strategy' && <CuratorView />}
                            {activeTab === 'practice' && <PracticeView onUpdate={refreshStats} />}
                            {activeTab === 'review' && <ReviewView stats={stats} />}
                        </motion.div>
                    </AnimatePresence>
                </main>
            </div>
        </>
    );
}
