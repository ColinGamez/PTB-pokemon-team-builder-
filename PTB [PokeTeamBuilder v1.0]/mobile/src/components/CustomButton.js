/**
 * CustomButton Component
 * Polished button component with multiple variants and states
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

const CustomButton = ({
  title,
  onPress,
  variant = 'primary', // 'primary', 'secondary', 'outline', 'ghost', 'danger', 'success'
  size = 'medium', // 'small', 'medium', 'large'
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left', // 'left', 'right', 'only'
  fullWidth = false,
  style = {},
  textStyle = {},
  gradient = false,
  ...props
}) => {
  const getVariantStyles = () => {
    const variants = {
      primary: {
        backgroundColor: '#3B82F6',
        borderColor: '#3B82F6',
        textColor: '#FFFFFF',
        gradientColors: ['#3B82F6', '#2563EB'],
      },
      secondary: {
        backgroundColor: '#6B7280',
        borderColor: '#6B7280',
        textColor: '#FFFFFF',
        gradientColors: ['#6B7280', '#4B5563'],
      },
      outline: {
        backgroundColor: 'transparent',
        borderColor: '#3B82F6',
        textColor: '#3B82F6',
        gradientColors: ['transparent', 'transparent'],
      },
      ghost: {
        backgroundColor: 'transparent',
        borderColor: 'transparent',
        textColor: '#3B82F6',
        gradientColors: ['transparent', 'transparent'],
      },
      danger: {
        backgroundColor: '#EF4444',
        borderColor: '#EF4444',
        textColor: '#FFFFFF',
        gradientColors: ['#EF4444', '#DC2626'],
      },
      success: {
        backgroundColor: '#10B981',
        borderColor: '#10B981',
        textColor: '#FFFFFF',
        gradientColors: ['#10B981', '#059669'],
      },
    };

    return variants[variant] || variants.primary;
  };

  const getSizeStyles = () => {
    const sizes = {
      small: {
        paddingVertical: 8,
        paddingHorizontal: 16,
        fontSize: 14,
        iconSize: 16,
      },
      medium: {
        paddingVertical: 12,
        paddingHorizontal: 24,
        fontSize: 16,
        iconSize: 20,
      },
      large: {
        paddingVertical: 16,
        paddingHorizontal: 32,
        fontSize: 18,
        iconSize: 24,
      },
    };

    return sizes[size] || sizes.medium;
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  const buttonStyle = [
    styles.button,
    {
      paddingVertical: sizeStyles.paddingVertical,
      paddingHorizontal: sizeStyles.paddingHorizontal,
      backgroundColor: disabled ? '#D1D5DB' : variantStyles.backgroundColor,
      borderColor: disabled ? '#D1D5DB' : variantStyles.borderColor,
      opacity: disabled ? 0.6 : 1,
    },
    fullWidth && styles.fullWidth,
    style,
  ];

  const textStyles = [
    styles.text,
    {
      fontSize: sizeStyles.fontSize,
      color: disabled ? '#9CA3AF' : variantStyles.textColor,
    },
    textStyle,
  ];

  const renderContent = () => {
    if (loading) {
      return (
        <View style={styles.contentContainer}>
          <ActivityIndicator
            size="small"
            color={disabled ? '#9CA3AF' : variantStyles.textColor}
          />
          {title && iconPosition !== 'only' && (
            <Text style={[textStyles, {marginLeft: 8}]}>
              {typeof title === 'string' ? title : 'Loading...'}
            </Text>
          )}
        </View>
      );
    }

    if (iconPosition === 'only' && icon) {
      return (
        <Icon
          name={icon}
          size={sizeStyles.iconSize}
          color={disabled ? '#9CA3AF' : variantStyles.textColor}
        />
      );
    }

    return (
      <View style={styles.contentContainer}>
        {icon && iconPosition === 'left' && (
          <Icon
            name={icon}
            size={sizeStyles.iconSize}
            color={disabled ? '#9CA3AF' : variantStyles.textColor}
            style={styles.iconLeft}
          />
        )}
        
        {title && (
          <Text style={textStyles} numberOfLines={1}>
            {title}
          </Text>
        )}
        
        {icon && iconPosition === 'right' && (
          <Icon
            name={icon}
            size={sizeStyles.iconSize}
            color={disabled ? '#9CA3AF' : variantStyles.textColor}
            style={styles.iconRight}
          />
        )}
      </View>
    );
  };

  const ButtonComponent = gradient && !disabled ? LinearGradient : View;
  const gradientProps = gradient && !disabled ? {
    colors: variantStyles.gradientColors,
    start: {x: 0, y: 0},
    end: {x: 1, y: 0},
  } : {};

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
      {...props}>
      <ButtonComponent
        style={[
          gradient && !disabled ? styles.gradient : null,
          !gradient ? {backgroundColor: buttonStyle[1].backgroundColor} : null,
        ]}
        {...gradientProps}>
        {renderContent()}
      </ButtonComponent>
    </TouchableOpacity>
  );
};

// Floating Action Button Component
export const FloatingActionButton = ({
  onPress,
  icon = 'add',
  backgroundColor = '#3B82F6',
  size = 56,
  style = {},
  disabled = false,
}) => {
  return (
    <TouchableOpacity
      style={[
        styles.fab,
        {
          width: size,
          height: size,
          backgroundColor: disabled ? '#D1D5DB' : backgroundColor,
          opacity: disabled ? 0.6 : 1,
        },
        style,
      ]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.8}>
      <Icon
        name={icon}
        size={size * 0.4}
        color={disabled ? '#9CA3AF' : '#FFFFFF'}
      />
    </TouchableOpacity>
  );
};

// Button Group Component
export const ButtonGroup = ({
  buttons = [],
  selectedIndex = 0,
  onPress,
  style = {},
}) => {
  return (
    <View style={[styles.buttonGroup, style]}>
      {buttons.map((button, index) => (
        <CustomButton
          key={index}
          title={button.title}
          variant={selectedIndex === index ? 'primary' : 'outline'}
          onPress={() => onPress(index)}
          style={[
            styles.groupButton,
            index === 0 && styles.groupButtonFirst,
            index === buttons.length - 1 && styles.groupButtonLast,
          ]}
          size="small"
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  fullWidth: {
    width: '100%',
  },
  gradient: {
    flex: 1,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  contentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
  fab: {
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
    position: 'absolute',
    bottom: 20,
    right: 20,
  },
  buttonGroup: {
    flexDirection: 'row',
    borderRadius: 8,
    overflow: 'hidden',
  },
  groupButton: {
    flex: 1,
    borderRadius: 0,
    borderRightWidth: 0,
    shadowOpacity: 0,
    elevation: 0,
  },
  groupButtonFirst: {
    borderTopLeftRadius: 8,
    borderBottomLeftRadius: 8,
  },
  groupButtonLast: {
    borderTopRightRadius: 8,
    borderBottomRightRadius: 8,
    borderRightWidth: 1,
  },
});

export default CustomButton;