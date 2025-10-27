/**
 * TypeBadge Component
 * Pokemon type display with proper colors and styling
 */

import React from 'react';
import {View, Text, StyleSheet} from 'react-native';

const TypeBadge = ({
  type,
  size = 'medium', // 'small', 'medium', 'large'
  variant = 'filled', // 'filled', 'outlined', 'subtle'
  style = {},
  textStyle = {},
}) => {
  if (!type) return null;

  // Pokemon type colors
  const typeColors = {
    normal: '#A8A878',
    fire: '#F08030',
    water: '#6890F0',
    electric: '#F8D030',
    grass: '#78C850',
    ice: '#98D8D8',
    fighting: '#C03028',
    poison: '#A040A0',
    ground: '#E0C068',
    flying: '#A890F0',
    psychic: '#F85888',
    bug: '#A8B820',
    rock: '#B8A038',
    ghost: '#705898',
    dragon: '#7038F8',
    dark: '#705848',
    steel: '#B8B8D0',
    fairy: '#EE99AC',
  };

  const getTypeColor = (typeName) => {
    return typeColors[typeName?.toLowerCase()] || '#68A090';
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          paddingHorizontal: 6,
          paddingVertical: 2,
          fontSize: 10,
          borderRadius: 8,
        };
      case 'large':
        return {
          paddingHorizontal: 16,
          paddingVertical: 6,
          fontSize: 16,
          borderRadius: 16,
        };
      default:
        return {
          paddingHorizontal: 12,
          paddingVertical: 4,
          fontSize: 12,
          borderRadius: 12,
        };
    }
  };

  const getVariantStyles = (color) => {
    switch (variant) {
      case 'outlined':
        return {
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderColor: color,
          textColor: color,
        };
      case 'subtle':
        return {
          backgroundColor: `${color}20`, // 20% opacity
          borderWidth: 0,
          textColor: color,
        };
      default: // filled
        return {
          backgroundColor: color,
          borderWidth: 0,
          textColor: '#FFFFFF',
        };
    }
  };

  const sizeStyles = getSizeStyles();
  const baseColor = getTypeColor(type);
  const variantStyles = getVariantStyles(baseColor);

  // Determine text color based on background for better contrast
  const getTextColor = () => {
    if (variant === 'outlined' || variant === 'subtle') {
      return variantStyles.textColor;
    }
    
    // For filled variant, use white text for better contrast
    return '#FFFFFF';
  };

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: variantStyles.backgroundColor,
          borderWidth: variantStyles.borderWidth,
          borderColor: variantStyles.borderColor,
          paddingHorizontal: sizeStyles.paddingHorizontal,
          paddingVertical: sizeStyles.paddingVertical,
          borderRadius: sizeStyles.borderRadius,
        },
        style,
      ]}>
      <Text
        style={[
          styles.text,
          {
            fontSize: sizeStyles.fontSize,
            color: getTextColor(),
          },
          textStyle,
        ]}>
        {type.toUpperCase()}
      </Text>
    </View>
  );
};

// Multi-type display component
export const TypeBadgeGroup = ({
  types = [],
  size = 'medium',
  variant = 'filled',
  maxTypes = 2,
  horizontal = true,
  style = {},
}) => {
  if (!types || types.length === 0) return null;

  const displayTypes = types.slice(0, maxTypes);

  return (
    <View
      style={[
        styles.group,
        horizontal ? styles.horizontal : styles.vertical,
        style,
      ]}>
      {displayTypes.map((type, index) => (
        <TypeBadge
          key={index}
          type={type}
          size={size}
          variant={variant}
          style={horizontal ? styles.horizontalSpacing : styles.verticalSpacing}
        />
      ))}
    </View>
  );
};

// Type effectiveness indicator
export const TypeEffectiveness = ({
  attackingType,
  defendingTypes = [],
  size = 'small',
  style = {},
}) => {
  // Simplified type effectiveness (you can expand this)
  const typeChart = {
    fire: {
      strong: ['grass', 'ice', 'bug', 'steel'],
      weak: ['fire', 'water', 'rock', 'dragon'],
      immune: [],
    },
    water: {
      strong: ['fire', 'ground', 'rock'],
      weak: ['water', 'grass', 'dragon'],
      immune: [],
    },
    grass: {
      strong: ['water', 'ground', 'rock'],
      weak: ['fire', 'grass', 'poison', 'flying', 'bug', 'dragon', 'steel'],
      immune: [],
    },
    // Add more type matchups as needed
  };

  const getEffectiveness = () => {
    if (!attackingType || !defendingTypes.length) return 1;

    const chart = typeChart[attackingType.toLowerCase()];
    if (!chart) return 1;

    let effectiveness = 1;
    defendingTypes.forEach(defType => {
      const defTypeLower = defType.toLowerCase();
      if (chart.immune.includes(defTypeLower)) {
        effectiveness *= 0;
      } else if (chart.strong.includes(defTypeLower)) {
        effectiveness *= 2;
      } else if (chart.weak.includes(defTypeLower)) {
        effectiveness *= 0.5;
      }
    });

    return effectiveness;
  };

  const effectiveness = getEffectiveness();
  
  const getEffectivenessColor = () => {
    if (effectiveness > 1) return '#10B981'; // Super effective - green
    if (effectiveness < 1 && effectiveness > 0) return '#EF4444'; // Not very effective - red
    if (effectiveness === 0) return '#6B7280'; // No effect - gray
    return '#6B7280'; // Normal - gray
  };

  const getEffectivenessText = () => {
    if (effectiveness > 1) return '×' + effectiveness;
    if (effectiveness < 1 && effectiveness > 0) return '×' + effectiveness;
    if (effectiveness === 0) return '×0';
    return '×1';
  };

  if (effectiveness === 1) return null; // Don't show normal effectiveness

  return (
    <View
      style={[
        styles.effectiveness,
        {backgroundColor: getEffectivenessColor()},
        style,
      ]}>
      <Text style={[styles.effectivenessText, {fontSize: size === 'small' ? 10 : 12}]}>
        {getEffectivenessText()}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    alignSelf: 'flex-start',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  group: {
    alignItems: 'flex-start',
  },
  horizontal: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  vertical: {
    flexDirection: 'column',
  },
  horizontalSpacing: {
    marginRight: 6,
    marginBottom: 4,
  },
  verticalSpacing: {
    marginBottom: 4,
  },
  effectiveness: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    minWidth: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  effectivenessText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 10,
  },
});

export default TypeBadge;