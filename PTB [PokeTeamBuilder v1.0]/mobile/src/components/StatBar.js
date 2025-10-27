/**
 * StatBar Component
 * Pokemon stat visualization with animated bars
 */

import React, {useRef, useEffect} from 'react';
import {View, Text, StyleSheet, Animated} from 'react-native';

const StatBar = ({
  label,
  value = 0,
  maxValue = 255, // Default max stat for Pokemon
  color,
  showValue = true,
  showLabel = true,
  animated = true,
  height = 8,
  style = {},
  labelStyle = {},
  valueStyle = {},
  barStyle = {},
}) => {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (animated) {
      Animated.timing(animatedValue, {
        toValue: value,
        duration: 1000,
        useNativeDriver: false,
      }).start();
    } else {
      animatedValue.setValue(value);
    }
  }, [value, animated]);

  const getStatColor = (statValue) => {
    if (color) return color;
    
    // Color based on stat value
    if (statValue >= 130) return '#10B981'; // Excellent - Green
    if (statValue >= 100) return '#3B82F6'; // Good - Blue  
    if (statValue >= 80) return '#F59E0B';  // Average - Yellow
    if (statValue >= 60) return '#EF4444';  // Poor - Red
    return '#6B7280'; // Very poor - Gray
  };

  const percentage = Math.min((value / maxValue) * 100, 100);
  const statColor = getStatColor(value);

  const animatedWidth = animatedValue.interpolate({
    inputRange: [0, maxValue],
    outputRange: ['0%', '100%'],
    extrapolate: 'clamp',
  });

  return (
    <View style={[styles.container, style]}>
      {/* Label and Value Row */}
      <View style={styles.header}>
        {showLabel && (
          <Text style={[styles.label, labelStyle]}>
            {label}
          </Text>
        )}
        
        {showValue && (
          <Text style={[styles.value, {color: statColor}, valueStyle]}>
            {value}
          </Text>
        )}
      </View>

      {/* Progress Bar */}
      <View style={[styles.barContainer, {height}, barStyle]}>
        <Animated.View
          style={[
            styles.bar,
            {
              width: animatedWidth,
              backgroundColor: statColor,
              height,
            },
          ]}
        />
      </View>
    </View>
  );
};

// Multi-stat display component
export const StatBars = ({
  stats = {},
  maxValue = 255,
  animated = true,
  showTotal = false,
  style = {},
  statStyle = {},
}) => {
  const statLabels = {
    hp: 'HP',
    attack: 'ATK',
    defense: 'DEF',
    specialAttack: 'SP.ATK',
    specialDefense: 'SP.DEF',
    speed: 'SPD',
  };

  const statOrder = ['hp', 'attack', 'defense', 'specialAttack', 'specialDefense', 'speed'];
  
  const total = Object.values(stats).reduce((sum, value) => sum + (value || 0), 0);

  return (
    <View style={[styles.statsContainer, style]}>
      {statOrder.map((statKey) => {
        const statValue = stats[statKey] || 0;
        const statLabel = statLabels[statKey] || statKey.toUpperCase();
        
        return (
          <StatBar
            key={statKey}
            label={statLabel}
            value={statValue}
            maxValue={maxValue}
            animated={animated}  
            style={[styles.statItem, statStyle]}
          />
        );
      })}
      
      {showTotal && (
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total</Text>
          <Text style={styles.totalValue}>{total}</Text>
        </View>
      )}
    </View>
  );
};

// Compact stat display for cards
export const StatSummary = ({
  stats = {},
  maxStats = 6,
  size = 'small',
  horizontal = false,
  style = {},
}) => {
  const statEntries = Object.entries(stats).slice(0, maxStats);
  
  const getSizeStyles = () => {
    switch (size) {
      case 'large':
        return {fontSize: 14, padding: 8};
      case 'medium':
        return {fontSize: 12, padding: 6};
      default:
        return {fontSize: 10, padding: 4};
    }
  };

  const sizeStyles = getSizeStyles();

  return (
    <View
      style={[
        styles.summaryContainer,
        horizontal ? styles.summaryHorizontal : styles.summaryVertical,
        style,
      ]}>
      {statEntries.map(([key, value]) => (
        <View key={key} style={styles.summaryItem}>
          <Text style={[styles.summaryLabel, {fontSize: sizeStyles.fontSize}]}>
            {key.charAt(0).toUpperCase()}
          </Text>
          <Text style={[styles.summaryValue, {fontSize: sizeStyles.fontSize}]}>
            {value}
          </Text>
        </View>
      ))}
    </View>
  );
};

// Stat comparison component
export const StatComparison = ({
  stats1 = {},
  stats2 = {},
  labels = ['Pokemon 1', 'Pokemon 2'],
  colors = ['#3B82F6', '#EF4444'],
  style = {},
}) => {
  const statKeys = ['hp', 'attack', 'defense', 'specialAttack', 'specialDefense', 'speed'];
  
  return (
    <View style={[styles.comparisonContainer, style]}>
      {statKeys.map((statKey) => {
        const value1 = stats1[statKey] || 0;
        const value2 = stats2[statKey] || 0;
        const maxValue = Math.max(value1, value2, 100);
        
        return (
          <View key={statKey} style={styles.comparisonRow}>
            <Text style={styles.comparisonLabel}>
              {statKey.charAt(0).toUpperCase() + statKey.slice(1)}
            </Text>
            
            <View style={styles.comparisonBars}>
              <View style={styles.comparisonBarContainer}>
                <View
                  style={[
                    styles.comparisonBar,
                    {
                      width: `${(value1 / maxValue) * 100}%`,
                      backgroundColor: colors[0],
                    },
                  ]}
                />
                <Text style={styles.comparisonValue}>{value1}</Text>
              </View>
              
              <View style={styles.comparisonBarContainer}>
                <View
                  style={[
                    styles.comparisonBar,
                    {
                      width: `${(value2 / maxValue) * 100}%`,
                      backgroundColor: colors[1],
                    },
                  ]}
                />
                <Text style={styles.comparisonValue}>{value2}</Text>
              </View>
            </View>
          </View>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  value: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  barContainer: {
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
  },
  bar: {
    borderRadius: 4,
  },
  statsContainer: {
    padding: 16,
  },
  statItem: {
    marginBottom: 12,
  },
  totalContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  totalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  summaryContainer: {
    padding: 8,
  },
  summaryHorizontal: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryVertical: {
    flexDirection: 'column',
  },
  summaryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minWidth: 40,
    marginBottom: 2,
  },
  summaryLabel: {
    fontWeight: '600',
    color: '#6B7280',
  },
  summaryValue: {
    fontWeight: 'bold',
    color: '#1F2937',
    marginLeft: 4,
  },
  comparisonContainer: {
    padding: 16,
  },
  comparisonRow: {
    marginBottom: 16,
  },
  comparisonLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  comparisonBars: {
    gap: 4,
  },
  comparisonBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 24,
  },
  comparisonBar: {
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  comparisonValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    minWidth: 30,
  },
});

export default StatBar;