import { useState, useEffect, useCallback, useRef } from 'react';

export const useVoiceInput = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'ja-JP';

            recognitionRef.current.onresult = (event: any) => {
                let currentTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    currentTranscript += event.results[i][0].transcript;
                }
                setTranscript(currentTranscript);
            };

            recognitionRef.current.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);
                setIsRecording(false);
            };

            recognitionRef.current.onend = () => {
                // If it ends but we think we are still recording, restart
                // This can happen if there's a long silence
                if (isRecording) {
                    recognitionRef.current.start();
                }
            };
        }
    }, [isRecording]);

    const startRecording = useCallback(() => {
        if (recognitionRef.current && !isRecording) {
            setIsRecording(true);
            setTranscript('');
            recognitionRef.current.start();
        }
    }, [isRecording]);

    const stopRecording = useCallback(() => {
        if (recognitionRef.current && isRecording) {
            setIsRecording(false);
            recognitionRef.current.stop();
        }
    }, [isRecording]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Enter' && !isRecording && !e.repeat) {
                // Check if we are in an input field to avoid conflicts if necessary
                // But the user specifically asked for "Enter" hold
                startRecording();
            }
        };

        const handleKeyUp = (e: KeyboardEvent) => {
            if (e.key === 'Enter') {
                stopRecording();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [startRecording, stopRecording, isRecording]);

    return { isRecording, transcript };
};
