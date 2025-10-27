/**
 * AnimatedComponents
 * Collection of smooth animations and micro-interactions
 */

import React, {useRef, useEffect} from 'react';
import {
  Animated,
  PanGestureHandler,
  TapGestureHandler,
  State,
} from 'react-native';

// Fade In Animation
export const FadeInView = ({
  children,
  duration = 300,
  delay = 0,
  style = {},
}) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration,
        useNativeDriver: true,
      }).start();
    }, delay);

    return () => clearTimeout(timer);
  }, []);

  return (
    <Animated.View
      style={[
        style,
        {
          opacity: fadeAnim,
        },
      ]}>
      {children}
    </Animated.View>
  );
};

// Slide In Animation
export const SlideInView = ({
  children,
  direction = 'up', // 'up', 'down', 'left', 'right'
  duration = 300,
  delay = 0,
  distance = 50,
  style = {},
}) => {
  const slideAnim = useRef(new Animated.Value(distance)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: 0,
          duration,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration,
          useNativeDriver: true,
        }),
      ]).start();
    }, delay);

    return () => clearTimeout(timer);
  }, []);

  const getTransform = () => {
    switch (direction) {
      case 'up':
        return {translateY: slideAnim};
      case 'down':
        return {translateY: slideAnim.interpolate({
          inputRange: [0, distance],
          outputRange: [0, -distance],
        })};
      case 'left':
        return {translateX: slideAnim.interpolate({
          inputRange: [0, distance],
          outputRange: [0, -distance],
        })};
      case 'right':
        return {translateX: slideAnim};
      default:
        return {translateY: slideAnim};
    }
  };

  return (
    <Animated.View
      style={[
        style,
        {
          opacity: fadeAnim,
          transform: [getTransform()],
        },
      ]}>
      {children}
    </Animated.View>
  );
};

// Scale Animation
export const ScaleView = ({
  children,
  duration = 300,
  delay = 0,
  fromScale = 0.8,
  toScale = 1,
  style = {},
}) => {
  const scaleAnim = useRef(new Animated.Value(fromScale)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(scaleAnim, {
          toValue: toScale,
          duration,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration,
          useNativeDriver: true,
        }),
      ]).start();
    }, delay);

    return () => clearTimeout(timer);
  }, []);

  return (
    <Animated.View
      style={[
        style,
        {
          opacity: fadeAnim,
          transform: [{scale: scaleAnim}],
        },
      ]}>
      {children}
    </Animated.View>
  );
};

// Bounce Animation
export const BounceView = ({
  children,
  bounceValue = 0.1,
  duration = 100,
  style = {},
  onPress,
}) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const animateBounce = () => {
    Animated.sequence([
      Animated.timing(scaleAnim, {
        toValue: 1 - bounceValue,
        duration,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration,
        useNativeDriver: true,
      }),
    ]).start();

    if (onPress) {
      onPress();
    }
  };

  return (
    <TapGestureHandler onHandlerStateChange={({nativeEvent}) => {
      if (nativeEvent.state === State.BEGAN) {
        animateBounce();
      }
    }}>
      <Animated.View
        style={[
          style,
          {
            transform: [{scale: scaleAnim}],
          },
        ]}>
        {children}
      </Animated.View>
    </TapGestureHandler>
  );
};

// Pulse Animation
export const PulseView = ({
  children,
  pulseScale = 1.05,
  duration = 1000,
  repeat = true,
  style = {},
}) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const createPulse = () => {
      return Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: pulseScale,
          duration: duration / 2,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: duration / 2,
          useNativeDriver: true,
        }),
      ]);
    };

    if (repeat) {
      Animated.loop(createPulse()).start();
    } else {
      createPulse().start();
    }
  }, []);

  return (
    <Animated.View
      style={[
        style,
        {
          transform: [{scale: pulseAnim}],
        },
      ]}>
      {children}
    </Animated.View>
  );
};

// Shake Animation
export const ShakeView = ({
  children,
  shakeDistance = 10,
  duration = 100,
  repeat = 3,
  style = {},
  trigger = false,
}) => {
  const shakeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (trigger) {
      const shakeSequence = [];
      for (let i = 0; i < repeat; i++) {
        shakeSequence.push(
          Animated.timing(shakeAnim, {
            toValue: shakeDistance,
            duration,
            useNativeDriver: true,
          }),
          Animated.timing(shakeAnim, {
            toValue: -shakeDistance,
            duration,
            useNativeDriver: true,
          })
        );
      }
      shakeSequence.push(
        Animated.timing(shakeAnim, {
          toValue: 0,
          duration,
          useNativeDriver: true,
        })
      );

      Animated.sequence(shakeSequence).start();
    }
  }, [trigger]);

  return (
    <Animated.View
      style={[
        style,
        {
          transform: [{translateX: shakeAnim}],
        },
      ]}>
      {children}
    </Animated.View>
  );
};

// Swipeable Card
export const SwipeableCard = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  swipeThreshold = 100,
  style = {},
}) => {
  const translateX = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(1)).current;

  const onGestureEvent = Animated.event(
    [{nativeEvent: {translationX: translateX}}],
    {useNativeDriver: true}
  );

  const onHandlerStateChange = ({nativeEvent}) => {
    if (nativeEvent.state === State.END) {
      const {translationX, velocityX} = nativeEvent;
      
      if (translationX > swipeThreshold || velocityX > 500) {
        // Swipe right
        Animated.parallel([
          Animated.timing(translateX, {
            toValue: 500,
            duration: 200,
            useNativeDriver: true,
          }),
          Animated.timing(opacity, {
            toValue: 0,
            duration: 200,
            useNativeDriver: true,
          }),
        ]).start(() => {
          if (onSwipeRight) onSwipeRight();
        });
      } else if (translationX < -swipeThreshold || velocityX < -500) {
        // Swipe left
        Animated.parallel([
          Animated.timing(translateX, {
            toValue: -500,
            duration: 200,
            useNativeDriver: true,
          }),
          Animated.timing(opacity, {
            toValue: 0,
            duration: 200,
            useNativeDriver: true,
          }),
        ]).start(() => {
          if (onSwipeLeft) onSwipeLeft();
        });
      } else {
        // Snap back
        Animated.spring(translateX, {
          toValue: 0,
          useNativeDriver: true,
        }).start();
      }
    }
  };

  return (
    <PanGestureHandler
      onGestureEvent={onGestureEvent}
      onHandlerStateChange={onHandlerStateChange}>
      <Animated.View
        style={[
          style,
          {
            transform: [{translateX}],
            opacity,
          },
        ]}>
        {children}
      </Animated.View>
    </PanGestureHandler>
  );
};

// Staggered List Animation
export const StaggeredList = ({
  children,
  staggerDelay = 100,
  animationType = 'fadeIn', // 'fadeIn', 'slideIn', 'scale'
  style = {},
}) => {
  const childrenArray = React.Children.toArray(children);

  return (
    <Animated.View style={style}>
      {childrenArray.map((child, index) => {
        const delay = index * staggerDelay;
        
        switch (animationType) {
          case 'slideIn':
            return (
              <SlideInView key={index} delay={delay}>
                {child}
              </SlideInView>
            );
          case 'scale':
            return (
              <ScaleView key={index} delay={delay}>
                {child}
              </ScaleView>
            );
          default:
            return (
              <FadeInView key={index} delay={delay}>
                {child}
              </FadeInView>
            );
        }
      })}
    </Animated.View>
  );
};

// Typing Animation
export const TypingText = ({
  text = '',
  speed = 50,
  style = {},
  onComplete,
}) => {
  const [displayText, setDisplayText] = React.useState('');
  const [currentIndex, setCurrentIndex] = React.useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timer);
    } else if (onComplete) {
      onComplete();
    }
  }, [currentIndex, text, speed]);

  useEffect(() => {
    setDisplayText('');
    setCurrentIndex(0);
  }, [text]);

  const Text = require('react-native').Text;

  return <Text style={style}>{displayText}</Text>;
};

export default {
  FadeInView,
  SlideInView,
  ScaleView,
  BounceView,
  PulseView,
  ShakeView,
  SwipeableCard,
  StaggeredList,
  TypingText,
};