import React from 'react';
import { StyleSheet, Text, View, Dimensions } from 'react-native';
import { BlurView } from 'expo-blur';
import { Mic } from 'lucide-react-native';
import Animated, { FadeInUp, withRepeat, withTiming, useSharedValue, useAnimatedStyle, Easing, withSequence } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

const AudioBar = ({ delay }: { delay: number }) => {
  const heightAnim = useSharedValue(20);
  React.useEffect(() => {
    setTimeout(() => {
      heightAnim.value = withRepeat(
        withSequence(
          withTiming(80 + Math.random() * 60, { duration: 400 + Math.random() * 400, easing: Easing.inOut(Easing.ease) }),
          withTiming(20, { duration: 400 + Math.random() * 400, easing: Easing.inOut(Easing.ease) })
        ), -1, true
      );
    }, delay);
  }, []);

  const style = useAnimatedStyle(() => ({ height: heightAnim.value }));
  return <Animated.View style={[styles.audioBar, style]} />;
};

export default function SoundScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <View style={styles.inner}>
        <Animated.View entering={FadeInUp.springify()} style={styles.waveContainer}>
          {[...Array(15)].map((_, i) => (
            <AudioBar key={i} delay={i * 100} />
          ))}
        </Animated.View>

        <Animated.View entering={FadeInUp.delay(500).springify()} style={styles.recordContainer}>
          <View style={styles.recordButton}>
            <Mic color="#FFF" size={40} />
          </View>
          <Text style={styles.recordingText}>LISTENING TO SOUL VECTORS...</Text>
        </Animated.View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow: { position: 'absolute', bottom: 100, left: 100, width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#00D4FF', opacity: 0.2, filter: 'blur(90px)' as any },
  inner: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  waveContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', height: 200, marginBottom: 80 },
  audioBar: { width: 8, backgroundColor: '#00D4FF', borderRadius: 4, marginHorizontal: 4, shadowColor: '#00D4FF', shadowOpacity: 0.8, shadowRadius: 8 },
  recordContainer: { alignItems: 'center' },
  recordButton: { width: 100, height: 100, borderRadius: 50, backgroundColor: 'rgba(0, 212, 255, 0.2)', borderWidth: 2, borderColor: '#00D4FF', justifyContent: 'center', alignItems: 'center', shadowColor: '#00D4FF', shadowOpacity: 0.8, shadowRadius: 20 },
  recordingText: { color: '#00D4FF', marginTop: 24, fontSize: 13, fontFamily: 'Outfit_700Bold', letterSpacing: 2 }
});
