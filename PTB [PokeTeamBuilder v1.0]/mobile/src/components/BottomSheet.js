/**
 * BottomSheet Component
 * Sliding bottom sheet modal with gestures
 */

import React, {useRef, useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  PanGestureHandler,
  TouchableOpacity,
  Dimensions,
  Modal,
  TouchableWithoutFeedback,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const {height: screenHeight} = Dimensions.get('window');

const BottomSheet = ({
  visible = false,
  onClose,
  title,
  children,
  height = screenHeight * 0.6,
  showHandle = true,
  showCloseButton = true,
  closable = true,
  style = {},
  headerStyle = {},
  contentStyle = {},
  backdropOpacity = 0.5,
  snapPoints = [],
  initialSnapIndex = 0,
}) => {
  const translateY = useRef(new Animated.Value(height)).current;
  const backdropOpacity = useRef(new Animated.Value(0)).current;
  const [currentSnapIndex, setCurrentSnapIndex] = useState(initialSnapIndex);

  useEffect(() => {
    if (visible) {
      openSheet();
    } else {
      closeSheet();
    }
  }, [visible]);

  const openSheet = () => {
    const targetHeight = snapPoints.length > 0 ? snapPoints[currentSnapIndex] : 0;
    
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: targetHeight,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(backdropOpacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const closeSheet = () => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: height,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(backdropOpacity, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => {
      if (onClose) onClose();
    });
  };

  const handleGesture = (event) => {
    const {translationY, velocityY} = event.nativeEvent;
    
    if (snapPoints.length > 0) {
      // Handle snapping
      let targetIndex = currentSnapIndex;
      
      if (velocityY > 500 && currentSnapIndex < snapPoints.length - 1) {
        targetIndex = currentSnapIndex + 1;
      } else if (velocityY < -500 && currentSnapIndex > 0) {
        targetIndex = currentSnapIndex - 1;
      } else {
        // Find closest snap point
        const currentPosition = snapPoints[currentSnapIndex] + translationY;
        let closestIndex = 0;
        let closestDistance = Math.abs(currentPosition - snapPoints[0]);
        
        snapPoints.forEach((snapPoint, index) => {
          const distance = Math.abs(currentPosition - snapPoint);
          if (distance < closestDistance) {
            closestDistance = distance;
            closestIndex = index;
          }
        });
        
        targetIndex = closestIndex;
      }
      
      if (targetIndex === snapPoints.length - 1 && closable) {
        closeSheet();
      } else {
        setCurrentSnapIndex(targetIndex);
        Animated.spring(translateY, {
          toValue: snapPoints[targetIndex],
          useNativeDriver: true,
        }).start();
      }
    } else {
      // Simple close on drag down
      if (translationY > 100 || velocityY > 500) {
        if (closable) closeSheet();
      } else {
        Animated.spring(translateY, {
          toValue: 0,
          useNativeDriver: true,
        }).start();
      }
    }
  };

  const handleBackdropPress = () => {
    if (closable) closeSheet();
  };

  if (!visible) return null;

  return (
    <Modal
      transparent
      visible={visible}
      animationType="none"
      onRequestClose={closable ? closeSheet : undefined}>
      
      {/* Backdrop */}
      <TouchableWithoutFeedback onPress={handleBackdropPress}>
        <Animated.View
          style={[
            styles.backdrop,
            {
              opacity: backdropOpacity,
              backgroundColor: `rgba(0,0,0,${backdropOpacity})`,
            },
          ]}
        />
      </TouchableWithoutFeedback>

      {/* Bottom Sheet */}
      <Animated.View
        style={[
          styles.container,
          {
            height,
            transform: [{translateY}],
          },
          style,
        ]}>
        
        <PanGestureHandler onGestureEvent={handleGesture}>
          <View style={styles.gestureArea}>
            {/* Handle */}
            {showHandle && (
              <View style={styles.handleContainer}>
                <View style={styles.handle} />
              </View>
            )}

            {/* Header */}
            {(title || showCloseButton) && (
              <View style={[styles.header, headerStyle]}>
                <View style={styles.headerLeft}>
                  {title && (
                    <Text style={styles.title}>{title}</Text>
                  )}
                </View>
                
                {showCloseButton && closable && (
                  <TouchableOpacity
                    style={styles.closeButton}
                    onPress={closeSheet}>
                    <Icon name="close" size={24} color="#6B7280" />
                  </TouchableOpacity>
                )}
              </View>
            )}

            {/* Content */}
            <View style={[styles.content, contentStyle]}>
              {children}
            </View>
          </View>
        </PanGestureHandler>
      </Animated.View>
    </Modal>
  );
};

// Quick action bottom sheet
export const ActionSheet = ({
  visible = false,
  onClose,
  title,
  actions = [],
  cancelText = 'Cancel',
  destructiveIndex = -1,
}) => {
  return (
    <BottomSheet
      visible={visible}
      onClose={onClose}
      title={title}
      height={Math.min(actions.length * 60 + 150, screenHeight * 0.8)}>
      
      <View style={styles.actionContainer}>
        {actions.map((action, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.actionButton,
              index === destructiveIndex && styles.destructiveAction,
            ]}
            onPress={() => {
              action.onPress?.();
              onClose?.();
            }}>
            
            {action.icon && (
              <Icon
                name={action.icon}
                size={20}
                color={index === destructiveIndex ? '#EF4444' : '#374151'}
                style={styles.actionIcon}
              />
            )}
            
            <Text
              style={[
                styles.actionText,
                index === destructiveIndex && styles.destructiveText,
              ]}>
              {action.title}
            </Text>
          </TouchableOpacity>
        ))}

        {/* Cancel Button */}
        <TouchableOpacity
          style={[styles.actionButton, styles.cancelButton]}
          onPress={onClose}>
          <Text style={styles.cancelText}>{cancelText}</Text>
        </TouchableOpacity>
      </View>
    </BottomSheet>
  );
};

const styles = StyleSheet.create({
  backdrop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: -2},
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 10,
  },
  gestureArea: {
    flex: 1,
  },
  handleContainer: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  handle: {
    width: 40,
    height: 4,
    backgroundColor: '#D1D5DB',
    borderRadius: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  headerLeft: {
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  closeButton: {
    padding: 4,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  actionContainer: {
    padding: 20,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 8,
    backgroundColor: '#F9FAFB',
  },
  destructiveAction: {
    backgroundColor: '#FEF2F2',
  },
  cancelButton: {
    backgroundColor: '#F3F4F6',
    marginTop: 8,
  },
  actionIcon: {
    marginRight: 12,
  },
  actionText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
  },
  destructiveText: {
    color: '#EF4444',
  },
  cancelText: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '600',
    textAlign: 'center',
    flex: 1,
  },
});

export default BottomSheet;