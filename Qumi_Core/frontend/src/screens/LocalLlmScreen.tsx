import React from 'react';
import { StyleSheet, Text, View, Dimensions } from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { MessageSquare } from 'lucide-react-native';
import Animated, { FadeInUp, FadeInDown } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

export default function LocalLlmScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.bgGlow1} />
      <BlurView intensity={100} tint="dark" style={StyleSheet.absoluteFillObject} />
      
      <View style={styles.inner}>
        <Animated.View entering={FadeInDown.springify()} style={styles.header}>
          <LinearGradient colors={['#FCEE09', '#FF8C00']} style={styles.iconCircle}>
            <MessageSquare color="#FFF" size={32} />
          </LinearGradient>
          <Text style={styles.title}>LOCAL LLM</Text>
          <Text style={styles.subtitle}>オフライン自律推論エンジンを起動中...</Text>
        </Animated.View>

        <Animated.View entering={FadeInUp.delay(200).springify()} style={styles.terminalWindow}>
          <BlurView intensity={60} tint="dark" style={styles.termBlur}>
            <Text style={styles.codeText}>[SYSTEM] Loading LLaMA 3.2 8B Int4...</Text>
            <Text style={styles.codeText}>[SYSTEM] Model loaded. RAM usage: 4.8GB</Text>
            <Text style={styles.codeText}>[READY] You are completely offline. Local vectors synchronized.</Text>
            <Text style={styles.blinkingCursor}>_</Text>
          </BlurView>
        </Animated.View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow1: { position: 'absolute', top: 100, left: 100, width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#FCEE09', opacity: 0.2, filter: 'blur(80px)' as any },
  inner: { flex: 1, paddingTop: 100, paddingHorizontal: 20 },
  header: { alignItems: 'center', marginBottom: 40 },
  iconCircle: { width: 80, height: 80, borderRadius: 40, justifyContent: 'center', alignItems: 'center', shadowColor: '#FCEE09', shadowOpacity: 0.8, shadowRadius: 20 },
  title: { color: '#FFF', fontSize: 28, fontWeight: '900', fontFamily: 'Outfit_900Black', marginTop: 24, letterSpacing: 2 },
  subtitle: { color: '#FCEE09', fontSize: 13, fontFamily: 'Outfit_700Bold', marginTop: 6, letterSpacing: 1 },
  terminalWindow: { flex: 1, marginBottom: 80, borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(252, 238, 9, 0.3)' },
  termBlur: { flex: 1, padding: 24 },
  codeText: { color: '#00FF99', fontFamily: 'monospace', fontSize: 14, marginBottom: 12 },
  blinkingCursor: { color: '#00FF99', fontFamily: 'monospace', fontSize: 16 }
});
