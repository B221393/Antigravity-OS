'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

interface GalleryItem {
    title: string;
    desc: string;
    color: string;
}

const imageData: GalleryItem[] = [
    { title: "Project Alpha", desc: "Digital Experience", color: "linear-gradient(45deg, #FF6B6B, #556270)" },
    { title: "Neon Dreams", desc: "Cyberpunk Art", color: "linear-gradient(45deg, #12c2e9, #c471ed, #f64f59)" },
    { title: "Zen Garden", desc: "Minimalist Design", color: "linear-gradient(45deg, #11998e, #38ef7d)" },
    { title: "Deep Ocean", desc: "Abstract Concept", color: "linear-gradient(45deg, #2193b0, #6dd5ed)" },
    { title: "Solar flare", desc: "Energy Visualization", color: "linear-gradient(45deg, #f12711, #f5af19)" },
    { title: "Night Walk", desc: "Urban Photography", color: "linear-gradient(45deg, #000046, #1CB5E0)" },
    { title: "Abstract Core", desc: "Generative Art", color: "linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045)" }
];

export default function CoverFlow() {
    const [currentIndex, setCurrentIndex] = useState(3);
    const [touchStartX, setTouchStartX] = useState(0);

    const moveGallery = (direction: number) => {
        let newIndex = currentIndex + direction;
        if (newIndex < 0) newIndex = 0;
        if (newIndex >= imageData.length) newIndex = imageData.length - 1;
        setCurrentIndex(newIndex);
    };

    // Keyboard support
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'ArrowLeft') moveGallery(-1);
            if (e.key === 'ArrowRight') moveGallery(1);
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentIndex]);

    // Touch support
    const handleTouchStart = (e: React.TouchEvent) => {
        setTouchStartX(e.changedTouches[0].screenX);
    };

    const handleTouchEnd = (e: React.TouchEvent) => {
        const diff = touchStartX - e.changedTouches[0].screenX;
        if (Math.abs(diff) > 50) {
            moveGallery(diff > 0 ? 1 : -1);
        }
    };

    return (
        <div className="relative w-full h-screen overflow-hidden bg-[#050505] text-white font-sans flex flex-col items-center justify-center">
            {/* Background Ambient Light */}
            <div className="absolute inset-0 z-0 pointer-events-none" style={{ background: 'radial-gradient(circle at 50% 50%, #1a1a2e 0%, #050505 80%)' }} />

            <header className="absolute top-8 z-10 text-center animate-fade-in-down opacity-0" style={{ animation: 'fadeInDown 1s ease-out forwards 0.5s' }}>
                <h1 className="font-light tracking-[0.2em] text-2xl uppercase m-0 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    COVER FLOW GALLERY
                </h1>
                <p className="text-xs text-gray-500 mt-1 uppercase tracking-wider">VECTIS PREMIUM EDIT</p>
                <Link href="/" className="text-[10px] text-blue-400 hover:text-blue-300 mt-2 block transition-colors">← Back to Visual Coder</Link>
            </header>

            {/* Stage */}
            <div className="relative w-full h-[60vh] flex items-center justify-center perspective-[1200px]" onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
                <div className="relative w-[300px] h-[400px] preserve-3d transition-transform duration-500 ease-out-cubic">
                    {imageData.map((item, index) => {
                        const offset = index - currentIndex;
                        const absOffset = Math.abs(offset);

                        // Transform Logic
                        let transform = '';
                        let zIndex = 100 - absOffset;
                        let opacity = 1;
                        let isActive = offset === 0;

                        if (isActive) {
                            transform = `translateX(0) translateZ(200px) rotateY(0deg)`;
                        } else {
                            const xShift = offset * 220;
                            const zShift = -200 + (absOffset * -100);
                            const rotate = offset > 0 ? -60 : 60;
                            transform = `translateX(${xShift}px) translateZ(${zShift}px) rotateY(${rotate}deg)`;
                            opacity = 0.6;
                        }

                        return (
                            <div
                                key={index}
                                className={`absolute w-full h-full rounded-2xl border border-white/10 backdrop-blur-md flex flex-col justify-end p-5 transition-all duration-500 ease-out cursor-pointer shadow-2xl overflow-hidden
                                    ${isActive ? 'active' : ''}`}
                                style={{
                                    transform,
                                    zIndex,
                                    opacity,
                                    background: 'rgba(255, 255, 255, 0.05)',
                                    WebkitBoxReflect: 'below 2px linear-gradient(transparent, transparent, rgba(0, 0, 0, 0.3))'
                                }}
                                onClick={() => setCurrentIndex(index)}
                            >
                                {/* Image Placeholder */}
                                <div
                                    className="absolute inset-0 w-full h-full z-[-1] opacity-60 transition-opacity duration-500 group-hover:opacity-80"
                                    style={{ background: item.color }}
                                />

                                <div className={`relative z-10 transition-all duration-300 transform ${isActive ? 'translate-y-0 opacity-100' : 'translate-y-5 opacity-0'}`}>
                                    <h2 className="text-xl font-semibold m-0">{item.title}</h2>
                                    <p className="text-sm text-gray-400 mt-1">{item.desc}</p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Nav Buttons */}
            <button
                onClick={() => moveGallery(-1)}
                className="absolute left-[5%] top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/10 hover:bg-white/30 text-white flex items-center justify-center backdrop-blur-sm transition-colors z-50 border-none cursor-pointer"
            >
                &#10094;
            </button>
            <button
                onClick={() => moveGallery(1)}
                className="absolute right-[5%] top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/10 hover:bg-white/30 text-white flex items-center justify-center backdrop-blur-sm transition-colors z-50 border-none cursor-pointer"
            >
                &#10095;
            </button>

            {/* CTA */}
            <div className="absolute bottom-12 z-50 animate-fade-in-up opacity-0" style={{ animation: 'fadeInUp 1s ease-out forwards 1s' }}>
                <a
                    href="https://kawaidesign.studio.site/contact"
                    target="_blank"
                    className="no-underline text-white border border-white/30 px-8 py-3 rounded-full text-sm tracking-wider bg-black/30 backdrop-blur-sm transition-all duration-300 hover:bg-white hover:text-black hover:shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                >
                    GET IN TOUCH
                </a>
            </div>

            <style jsx>{`
                @keyframes fadeInDown {
                    from { opacity: 0; transform: translateY(-20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .preserve-3d { transform-style: preserve-3d; }
                .perspective-{1200px} { perspective: 1200px; }
                .ease-out-cubic { transition-timing-function: cubic-bezier(0.2, 0.8, 0.2, 1); }
            `}</style>
        </div>
    );
}
