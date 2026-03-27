import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity,
  Platform, ActivityIndicator
} from 'react-native';
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import Animated, { 
  useAnimatedStyle, 
  withSpring, 
  withRepeat, 
  withTiming,
  interpolate,
  useSharedValue,
  FadeIn,
  FadeOut,
  Layout
} from 'react-native-reanimated';
import { BlurView } from 'expo-blur';

const BACKEND_URL = 'http://localhost:8000';

export default function ThoughtCapture({ onResult }: { onResult: (res: any) => void }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState('');
  
  const pulse = useSharedValue(0);
  const mediaRecorder = useRef<any>(null);
  const audioChunks = useRef<Blob[]>([]);

  useEffect(() => {
    if (isRecording) {
      pulse.value = withRepeat(withTiming(1, { duration: 1000 }), -1, true);
    } else {
      pulse.value = withSpring(0);
    }
  }, [isRecording]);

  const animatedPulseStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: interpolate(pulse.value, [0, 1], [1, 1.4]) }],
      opacity: interpolate(pulse.value, [0, 1], [0.8, 0.2]),
    };
  });

  const startRecording = async () => {
    try {
      if (Platform.OS !== 'web') {
        alert('Voice capture is currently optimized for Web Thought OS.');
        return;
      }
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event: any) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        await uploadAudio(audioBlob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setStatus('LISTENING TO YOUR SOUL...');
    } catch (err) {
      console.error('Failed to start recording:', err);
      alert('Microphone access denied.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      setStatus('ANALYZING FREQUENCIES...');
    }
  };

  const uploadAudio = async (blob: Blob) => {
    setIsProcessing(true);
    setStatus('WHISPERING TO GEMMA...');
    
    const formData = new FormData();
    formData.append('file', blob, 'thought.wav');

    try {
      const response = await fetch(`${BACKEND_URL}/voice`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.structured_result) {
        onResult(data);
      }
    } catch (err) {
      console.error('Upload failed:', err);
      setStatus('ERROR: CONNECTION LOST');
    } finally {
      setIsProcessing(false);
      setStatus('');
    }
  };

  return (
    <View style={styles.container}>
      <BlurView intensity={30} tint="dark" style={styles.glassContainer}>
        {isRecording && (
          <Animated.View style={[styles.pulseCircle, animatedPulseStyle]} />
        )}
        
        <TouchableOpacity
          activeOpacity={0.8}
          onPressIn={startRecording}
          onPressOut={stopRecording}
          style={[
            styles.micButton,
            isRecording && styles.micButtonActive,
            isProcessing && styles.micButtonDisabled
          ]}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="#3b82f6" />
          ) : (
            <Ionicons 
              name={isRecording ? "stop" : "mic"} 
              size={32} 
              color={isRecording ? "#ef4444" : "#3b82f6"} 
            />
          )}
        </TouchableOpacity>

        {status ? (
          <Animated.Text entering={FadeIn} exiting={FadeOut} style={styles.statusText}>
            {status}
          </Animated.Text>
        ) : (
          <Text style={styles.hintText}>HOLD TO CAPTURE THOUGHT</Text>
        )}
      </BlurView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 24,
    width: '100%',
    alignItems: 'center',
  },
  glassContainer: {
    width: '100%',
    padding: 32,
    borderRadius: 32,
    borderWidth: 1,
    borderColor: 'rgba(59, 130, 246, 0.2)',
    alignItems: 'center',
    overflow: 'hidden',
    backgroundColor: 'rgba(15, 23, 42, 0.5)',
  },
  pulseCircle: {
    position: 'absolute',
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#3b82f6',
    top: 32,
  },
  micButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#1e293b',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#3b82f6',
    zIndex: 2,
  },
  micButtonActive: {
    borderColor: '#ef4444',
    backgroundColor: '#2d0a0a',
  },
  micButtonDisabled: {
    opacity: 0.5,
  },
  statusText: {
    color: '#3b82f6',
    marginTop: 20,
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 2,
  },
  hintText: {
    color: '#475569',
    marginTop: 20,
    fontSize: 10,
    fontWeight: 'bold',
    letterSpacing: 1,
  }
});
