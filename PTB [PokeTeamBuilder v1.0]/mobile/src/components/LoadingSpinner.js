/**
 * LoadingSpinner Component
 * Elegant loading indicator with Pokemon theme
 */

import React, {useRef, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Easing,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

const LoadingSpinner = ({
  size = 'medium',
  message = 'Loading...',
  showMessage = true,
  color = '#3B82F6',
  variant = 'default', // 'default', 'pokeball', 'pulse', 'dots'
  style = {},
}) => {
  const spinValue = useRef(new Animated.Value(0)).current;
  const scaleValue = useRef(new Animated.Value(1)).current;
  const fadeValue = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    // Spinning animation
    const spinAnimation = Animated.loop(
      Animated.timing(spinValue, {
        toValue: 1,
        duration: variant === 'pokeball' ? 2000 : 1000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );

    // Pulse animation
    const pulseAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(scaleValue, {
          toValue: 1.1,
          duration: 800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(scaleValue, {
          toValue: 1,
          duration: 800,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );

    // Fade animation
    const fadeAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(fadeValue, {
          toValue: 1,
          duration: 1200,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(fadeValue, {
          toValue: 0.3,
          duration: 1200,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );

    spinAnimation.start();
    if (variant === 'pulse') pulseAnimation.start();
    if (variant === 'dots') fadeAnimation.start();

    return () => {
      spinAnimation.stop();
      pulseAnimation.stop();
      fadeAnimation.stop();
    };
  }, [variant]);

  const getSize = () => {
    switch (size) {
      case 'small':
        return 24;
      case 'large':
        return 48;
      default:
        return 32;
    }
  };

  const spin = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const renderSpinner = () => {
    const iconSize = getSize();

    switch (variant) {
      case 'pokeball':
        return (
          <Animated.View
            style={[
              styles.pokeballContainer,
              {transform: [{rotate: spin}, {scale: scaleValue}]},
            ]}>
            <LinearGradient
              colors={['#EF4444', '#DC2626', '#B91C1C']}
              style={[styles.pokeball, {width: iconSize, height: iconSize}]}>
              <View style={[styles.pokeballTop, {borderBottomWidth: iconSize * 0.05}]} />
              <View style={[styles.pokeballCenter, {width: iconSize * 0.3, height: iconSize * 0.3}]} />
              <View style={[styles.pokeballBottom, {borderTopWidth: iconSize * 0.05}]} />
            </LinearGradient>
          </Animated.View>
        );

      case 'pulse':
        return (
          <Animated.View style={{transform: [{scale: scaleValue}]}}>
            <Icon name="catching-pokemon" size={iconSize} color={color} />
          </Animated.View>
        );

      case 'dots':
        return (
          <View style={styles.dotsContainer}>
            {[0, 1, 2].map((index) => (
              <Animated.View
                key={index}
                style={[
                  styles.dot,
                  {
                    backgroundColor: color,
                    opacity: fadeValue,
                    transform: [
                      {
                        scale: fadeValue.interpolate({
                          inputRange: [0.3, 1],
                          outputRange: [0.8, 1.2],
                        }),
                      },
                    ],
                  },
                ]}
              />
            ))}
          </View>
        );

      default:
        return (
          <Animated.View style={{transform: [{rotate: spin}]}}>
            <ActivityIndicator size={size} color={color} />
          </Animated.View>
        );
    }
  };

  return (
    <View style={[styles.container, style]}>
      <View style={styles.spinnerContainer}>
        {renderSpinner()}
      </View>
      
      {showMessage && message && (
        <Text style={[styles.message, {color}]}>
          {message}
        </Text>
      )}
    </View>
  );
};

// Overlay Loading Component
export const LoadingOverlay = ({
  visible = false,
  message = 'Loading...',
  variant = 'pokeball',
  backgroundColor = 'rgba(0,0,0,0.7)',
}) => {
  if (!visible) return null;

  return (
    <View style={[styles.overlay, {backgroundColor}]}>
      <View style={styles.overlayContent}>
        <LoadingSpinner
          variant={variant}
          message={message}
          size="large"
          color="#FFFFFF"
        />
      </View>
    </View>
  );
};

// Inline Loading Component
export const InlineLoading = ({
  message = 'Loading...',
  size = 'small',
  color = '#6B7280',
}) => {
  return (
    <View style={styles.inlineContainer}>
      <LoadingSpinner
        variant="default"
        message={message}
        size={size}
        color={color}
        style={styles.inline}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  spinnerContainer: {
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    fontWeight: '500',
    textAlign: 'center',
  },
  pokeballContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  pokeball: {
    borderRadius: 100,
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  pokeballTop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '50%',
    backgroundColor: 'transparent',
    borderBottomColor: '#1F2937',
  },
  pokeballCenter: {
    backgroundColor: '#F3F4F6',
    borderRadius: 100,
    borderWidth: 2,
    borderColor: '#1F2937',
    zIndex: 1,
  },
  pokeballBottom: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '50%',
    backgroundColor: 'transparent',
    borderTopColor: '#1F2937',
  },
  dotsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  overlayContent: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    backdropFilter: 'blur(10px)',
  },
  inlineContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
  },
  inline: {
    padding: 0,
  },
});

export default LoadingSpinner;