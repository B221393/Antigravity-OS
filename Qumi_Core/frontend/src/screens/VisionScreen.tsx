import React from 'react';
import { StyleSheet, Text, View, Dimensions } from 'react-native';
import { BlurView } from 'expo-blur';
import { Camera } from 'lucide-react-native';
import Animated, { FadeInUp, withRepeat, withTiming, useSharedValue, useAnimatedStyle, Easing } from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

export default function VisionScreen() {
  const scanY = useSharedValue(0);

  React.useEffect(() => {
    scanY.value = withRepeat(withTiming(height * 0.5, { duration: 2500, easing: Easing.linear }), -1, true);
  }, []);

  const scanStyle = useAnimatedStyle(() => ({ transform: [{ translateY: scanY.value }] }));

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={30} tint="dark" style={StyleSheet.absoluteFillObject} />

      <View style={styles.viewfinder}>
        {/* スキャンバーのアニメーション */}
        <Animated.View style={[styles.scanLine, scanStyle]} />

        {/* 四隅のカメラフレーム */}
        <View style={[styles.corner, styles.topLeft]} />
        <View style={[styles.corner, styles.topRight]} />
        <View style={[styles.corner, styles.bottomLeft]} />
        <View style={[styles.corner, styles.bottomRight]} />

        <Animated.View entering={FadeInUp.delay(300).springify()} style={styles.centerTarget}>
          <Camera color="#00FF66" size={40} />
          <Text style={styles.targetText}>EVALUATING ENVIRONMENT VECTORS...</Text>
        </Animated.View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505', justifyContent: 'center', alignItems: 'center' },
  bgGlow: { position: 'absolute', width: width, height: height, backgroundColor: '#00FF66', opacity: 0.1, filter: 'blur(100px)' as any },
  viewfinder: { width: '80%', height: '60%', position: 'relative', justifyContent: 'center', alignItems: 'center' },
  scanLine: { position: 'absolute', top: 0, left: 0, right: 0, height: 2, backgroundColor: '#00FF66', shadowColor: '#00FF66', shadowOpacity: 1, shadowRadius: 10, zIndex: 10 },
  corner: { position: 'absolute', width: 40, height: 40, borderColor: '#00FF66', borderWidth: 0 },
  topLeft: { top: 0, left: 0, borderTopWidth: 4, borderLeftWidth: 4 },
  topRight: { top: 0, right: 0, borderTopWidth: 4, borderRightWidth: 4 },
  bottomLeft: { bottom: 0, left: 0, borderBottomWidth: 4, borderLeftWidth: 4 },
  bottomRight: { bottom: 0, right: 0, borderBottomWidth: 4, borderRightWidth: 4 },
  centerTarget: { alignItems: 'center' },
  targetText: { color: '#00FF66', fontFamily: 'Outfit_700Bold', fontSize: 12, marginTop: 16, letterSpacing: 2 }
});
