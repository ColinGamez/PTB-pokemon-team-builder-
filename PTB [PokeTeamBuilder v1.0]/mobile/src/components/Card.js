/**
 * Card Component
 * Reusable card container with elevation and styling
 */

import React from 'react';
import {View, StyleSheet, TouchableOpacity} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';

const Card = ({
  children,
  onPress,
  style = {},
  variant = 'default', // 'default', 'elevated', 'outlined', 'filled', 'gradient'
  size = 'medium', // 'small', 'medium', 'large'
  disabled = false,
  gradient = null, // Array of colors for gradient variant
  ...props
}) => {
  const getVariantStyles = () => {
    const variants = {
      default: {
        backgroundColor: '#FFFFFF',
        borderWidth: 0,
        shadowColor: '#000',
        shadowOffset: {width: 0, height: 2},
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      },
      elevated: {
        backgroundColor: '#FFFFFF',
        borderWidth: 0,
        shadowColor: '#000',
        shadowOffset: {width: 0, height: 4},
        shadowOpacity: 0.15,
        shadowRadius: 8,
        elevation: 6,
      },
      outlined: {
        backgroundColor: '#FFFFFF',
        borderWidth: 1,
        borderColor: '#E5E7EB',
        shadowColor: '#000',
        shadowOffset: {width: 0, height: 1},
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 1,
      },
      filled: {
        backgroundColor: '#F9FAFB',
        borderWidth: 0,
        shadowOpacity: 0,
        elevation: 0,
      },
      gradient: {
        borderWidth: 0,
        shadowColor: '#000',
        shadowOffset: {width: 0, height: 2},
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      },
    };

    return variants[variant] || variants.default;
  };

  const getSizeStyles = () => {
    const sizes = {
      small: {
        padding: 12,
        borderRadius: 8,
      },
      medium: {
        padding: 16,
        borderRadius: 12,
      },
      large: {
        padding: 20,
        borderRadius: 16,
      },
    };

    return sizes[size] || sizes.medium;
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  const cardStyle = [
    styles.card,
    variantStyles,
    sizeStyles,
    disabled && styles.disabled,
    style,
  ];

  const cardContent = (
    <View style={styles.content}>
      {children}
    </View>
  );

  if (variant === 'gradient' && gradient && gradient.length > 0) {
    const CardComponent = onPress ? TouchableOpacity : View;
    
    return (
      <CardComponent
        style={[cardStyle, {backgroundColor: 'transparent'}]}
        onPress={disabled ? undefined : onPress}
        disabled={disabled}
        activeOpacity={onPress ? 0.8 : 1}
        {...props}>
        <LinearGradient
          colors={gradient}
          style={[styles.gradientContainer, {borderRadius: sizeStyles.borderRadius}]}
          start={{x: 0, y: 0}}
          end={{x: 1, y: 1}}>
          {cardContent}
        </LinearGradient>
      </CardComponent>
    );
  }

  if (onPress && !disabled) {
    return (
      <TouchableOpacity
        style={cardStyle}
        onPress={onPress}
        activeOpacity={0.8}
        {...props}>
        {cardContent}
      </TouchableOpacity>
    );
  }

  return (
    <View style={cardStyle} {...props}>
      {cardContent}
    </View>
  );
};

// Specialized card components
export const InfoCard = ({
  title,
  subtitle,
  value,
  icon,
  color = '#3B82F6',
  ...props
}) => {
  const Icon = require('react-native-vector-icons/MaterialIcons').default;
  
  return (
    <Card variant="elevated" {...props}>
      <View style={styles.infoCardContent}>
        {icon && (
          <View style={[styles.infoIcon, {backgroundColor: `${color}20`}]}>
            <Icon name={icon} size={24} color={color} />
          </View>
        )}
        
        <View style={styles.infoText}>
          {title && (
            <Text style={styles.infoTitle}>{title}</Text>
          )}
          {subtitle && (
            <Text style={styles.infoSubtitle}>{subtitle}</Text>
          )}
          {value && (
            <Text style={[styles.infoValue, {color}]}>{value}</Text>
          )}
        </View>
      </View>
    </Card>
  );
};

export const StatCard = ({
  label,
  value,
  change,
  changeType = 'neutral', // 'positive', 'negative', 'neutral'
  icon,
  ...props
}) => {
  const Icon = require('react-native-vector-icons/MaterialIcons').default;
  const Text = require('react-native').Text;
  
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return '#10B981';
      case 'negative':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  return (
    <Card variant="outlined" size="small" {...props}>
      <View style={styles.statCardContent}>
        <View style={styles.statCardHeader}>
          {icon && <Icon name={icon} size={16} color="#6B7280" />}
          <Text style={styles.statLabel}>{label}</Text>
        </View>
        
        <Text style={styles.statValue}>{value}</Text>
        
        {change && (
          <View style={styles.statChange}>
            <Icon
              name={changeType === 'positive' ? 'trending-up' : changeType === 'negative' ? 'trending-down' : 'trending-flat'}
              size={14}
              color={getChangeColor()}
            />
            <Text style={[styles.changeText, {color: getChangeColor()}]}>
              {change}
            </Text>
          </View>
        )}
      </View>
    </Card>
  );
};

export const ActionCard = ({
  title,
  description,
  icon,
  actionText = 'Action',
  onActionPress,
  color = '#3B82F6',
  ...props
}) => {
  const Icon = require('react-native-vector-icons/MaterialIcons').default;
  const Text = require('react-native').Text;
  const CustomButton = require('./CustomButton').default;
  
  return (
    <Card variant="elevated" {...props}>
      <View style={styles.actionCardContent}>
        {icon && (
          <View style={[styles.actionIcon, {backgroundColor: `${color}20`}]}>
            <Icon name={icon} size={32} color={color} />
          </View>
        )}
        
        <View style={styles.actionText}>
          <Text style={styles.actionTitle}>{title}</Text>
          {description && (
            <Text style={styles.actionDescription}>{description}</Text>
          )}
        </View>
        
        {onActionPress && (
          <CustomButton
            title={actionText}
            onPress={onActionPress}
            variant="primary"
            size="small"
            style={styles.actionButton}
          />
        )}
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    marginBottom: 8,
  },
  disabled: {
    opacity: 0.6,
  },
  content: {
    flex: 1,
  },
  gradientContainer: {
    flex: 1,
    padding: 16,
  },
  infoCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  infoIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  infoText: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  infoSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  statCardContent: {
    alignItems: 'flex-start',
  },
  statCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
    marginLeft: 4,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  statChange: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  changeText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 2,
  },
  actionCardContent: {
    alignItems: 'center',
    textAlign: 'center',
  },
  actionIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  actionText: {
    alignItems: 'center',
    marginBottom: 16,
  },
  actionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  actionDescription: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  actionButton: {
    minWidth: 120,
  },
});

export default Card;