import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic } from 'lucide-react';

interface VoiceOverlayProps {
    isRecording: boolean;
}

export const VoiceOverlay: React.FC<VoiceOverlayProps> = ({ isRecording }) => {
    return (
        <AnimatePresence>
            {isRecording && (
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    style={{
                        position: 'fixed',
                        top: '20px',
                        left: '20px',
                        zIndex: 1000,
                        background: 'rgba(255, 51, 102, 0.9)',
                        color: 'white',
                        padding: '12px 20px',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        boxShadow: '0 8px 32px rgba(255, 51, 102, 0.3)',
                        backdropFilter: 'blur(8px)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        fontWeight: 'bold',
                        pointerEvents: 'none'
                    }}
                >
                    <motion.div
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1, repeat: Infinity }}
                        style={{
                            width: '12px',
                            height: '12px',
                            background: '#fff',
                            borderRadius: '50%'
                        }}
                    />
                    <Mic size={18} />
                    <span>音声入力中... (Enterを離して完了)</span>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
