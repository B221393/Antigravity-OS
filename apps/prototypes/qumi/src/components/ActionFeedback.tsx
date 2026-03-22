import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withSequence,
  withSpring,
  withDelay,
  Easing,
  cancelAnimation,
  runOnJS,
  FadeIn,
  FadeOut,
  SlideInDown,
  SlideOutDown,
} from 'react-native-reanimated';

/**
 * ActionFeedback - アクション実行中の視覚フィードバック
 * 
 * 1. PulseGlow: スロットアイコンの鼓動パルス発光
 * 2. NotificationBadge: 完了通知バッジの飛び出しエフェクト
 * 3. ProcessingOverlay: 実行中のオーバーレイ表示
 */

// ─── 1. パルス発光コンポーネント ─────────────────
interface PulseGlowProps {
  isActive: boolean;
  color: string;
  size?: number;
  children: React.ReactNode;
}

export const PulseGlow: React.FC<PulseGlowProps> = ({
  isActive,
  color,
  size = 75,
  children,
}) => {
  const pulseScale = useSharedValue(1);
  const pulseOpacity = useSharedValue(0);
  const glowRadius = useSharedValue(0);

  useEffect(() => {
    if (isActive) {
      // 鼓動スケールアニメーション
      pulseScale.value = withRepeat(
        withSequence(
          withTiming(1.08, { duration: 600, easing: Easing.inOut(Easing.ease) }),
          withTiming(1.0, { duration: 600, easing: Easing.inOut(Easing.ease) })
        ),
        -1, // 無限ループ
        true
      );

      // 発光オパシティ
      pulseOpacity.value = withRepeat(
        withSequence(
          withTiming(0.8, { duration: 600, easing: Easing.inOut(Easing.ease) }),
          withTiming(0.2, { duration: 600, easing: Easing.inOut(Easing.ease) })
        ),
        -1,
        true
      );

      // グロー半径
      glowRadius.value = withRepeat(
        withSequence(
          withTiming(20, { duration: 600, easing: Easing.inOut(Easing.ease) }),
          withTiming(8, { duration: 600, easing: Easing.inOut(Easing.ease) })
        ),
        -1,
        true
      );
    } else {
      cancelAnimation(pulseScale);
      cancelAnimation(pulseOpacity);
      cancelAnimation(glowRadius);
      pulseScale.value = withTiming(1, { duration: 200 });
      pulseOpacity.value = withTiming(0, { duration: 200 });
      glowRadius.value = withTiming(0, { duration: 200 });
    }
  }, [isActive]);

  const animatedContainerStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulseScale.value }],
  }));

  const animatedGlowStyle = useAnimatedStyle(() => ({
    position: 'absolute' as const,
    top: -8,
    left: -8,
    right: -8,
    bottom: -8,
    borderRadius: 32,
    backgroundColor: color,
    opacity: pulseOpacity.value * 0.3,
    shadowColor: color,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: pulseOpacity.value,
    shadowRadius: glowRadius.value,
    elevation: 15,
  }));

  return (
    <Animated.View style={[{ position: 'relative' }, animatedContainerStyle]}>
      {isActive && <Animated.View style={animatedGlowStyle} />}
      {children}
    </Animated.View>
  );
};

// ─── 2. 通知バッジコンポーネント ─────────────────
interface NotificationBadgeProps {
  visible: boolean;
  color: string;
  label?: string;
}

export const NotificationBadge: React.FC<NotificationBadgeProps> = ({
  visible,
  color,
  label = '✓',
}) => {
  const badgeScale = useSharedValue(0);
  const badgeY = useSharedValue(10);

  useEffect(() => {
    if (visible) {
      // 飛び出しアニメーション
      badgeScale.value = withSpring(1, {
        damping: 8,
        stiffness: 200,
        mass: 0.5,
      });
      badgeY.value = withSpring(-8, {
        damping: 10,
        stiffness: 180,
      });

      // 3秒後に消えるように
      const timeout = setTimeout(() => {
        badgeScale.value = withTiming(0, { duration: 300 });
        badgeY.value = withTiming(10, { duration: 300 });
      }, 3000);

      return () => clearTimeout(timeout);
    } else {
      badgeScale.value = withTiming(0, { duration: 200 });
      badgeY.value = withTiming(10, { duration: 200 });
    }
  }, [visible]);

  const badgeStyle = useAnimatedStyle(() => ({
    transform: [{ scale: badgeScale.value }, { translateY: badgeY.value }],
  }));

  if (!visible) return null;

  return (
    <Animated.View style={[localStyles.badge, { backgroundColor: color }, badgeStyle]}>
      <Text style={localStyles.badgeText}>{label}</Text>
    </Animated.View>
  );
};

// ─── 3. 実行中オーバーレイ ───────────────────────
interface ProcessingOverlayProps {
  visible: boolean;
  slotLabel: string;
  color: string;
}

export const ProcessingOverlay: React.FC<ProcessingOverlayProps> = ({
  visible,
  slotLabel,
  color,
}) => {
  const dotOpacity1 = useSharedValue(0.3);
  const dotOpacity2 = useSharedValue(0.3);
  const dotOpacity3 = useSharedValue(0.3);

  useEffect(() => {
    if (visible) {
      dotOpacity1.value = withRepeat(
        withSequence(
          withTiming(1, { duration: 400 }),
          withTiming(0.3, { duration: 400 })
        ),
        -1,
        true
      );
      dotOpacity2.value = withDelay(
        200,
        withRepeat(
          withSequence(
            withTiming(1, { duration: 400 }),
            withTiming(0.3, { duration: 400 })
          ),
          -1,
          true
        )
      );
      dotOpacity3.value = withDelay(
        400,
        withRepeat(
          withSequence(
            withTiming(1, { duration: 400 }),
            withTiming(0.3, { duration: 400 })
          ),
          -1,
          true
        )
      );
    } else {
      cancelAnimation(dotOpacity1);
      cancelAnimation(dotOpacity2);
      cancelAnimation(dotOpacity3);
    }
  }, [visible]);

  const dot1Style = useAnimatedStyle(() => ({ opacity: dotOpacity1.value }));
  const dot2Style = useAnimatedStyle(() => ({ opacity: dotOpacity2.value }));
  const dot3Style = useAnimatedStyle(() => ({ opacity: dotOpacity3.value }));

  if (!visible) return null;

  return (
    <Animated.View
      entering={SlideInDown.springify().damping(15)}
      exiting={SlideOutDown.duration(200)}
      style={localStyles.processingBar}
    >
      <View style={[localStyles.processingDot, { backgroundColor: color }]}>
        <Animated.View style={[localStyles.processingDotInner, { backgroundColor: color }, dot1Style]} />
      </View>
      <View style={[localStyles.processingDot, { backgroundColor: color }]}>
        <Animated.View style={[localStyles.processingDotInner, { backgroundColor: color }, dot2Style]} />
      </View>
      <View style={[localStyles.processingDot, { backgroundColor: color }]}>
        <Animated.View style={[localStyles.processingDotInner, { backgroundColor: color }, dot3Style]} />
      </View>
      <Text style={[localStyles.processingText, { color }]}>
        {slotLabel} 処理中...
      </Text>
    </Animated.View>
  );
};

// ─── 4. チャットメッセージ・アニメーション ─────────
interface ChatBubbleAnimatedProps {
  children: React.ReactNode;
  index: number;
}

export const ChatBubbleAnimated: React.FC<ChatBubbleAnimatedProps> = ({
  children,
  index,
}) => {
  return (
    <Animated.View
      entering={FadeIn.delay(index * 50).duration(300).springify()}
    >
      {children}
    </Animated.View>
  );
};

// ─── ローカルスタイル ─────────────────────────────
const localStyles = StyleSheet.create({
  badge: {
    position: 'absolute',
    top: -6,
    right: -6,
    width: 22,
    height: 22,
    borderRadius: 11,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#000',
    zIndex: 10,
  },
  badgeText: {
    color: '#000',
    fontSize: 10,
    fontWeight: '900',
  },
  processingBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    gap: 6,
  },
  processingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    opacity: 0.2,
  },
  processingDotInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  processingText: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1,
    marginLeft: 8,
  },
});
