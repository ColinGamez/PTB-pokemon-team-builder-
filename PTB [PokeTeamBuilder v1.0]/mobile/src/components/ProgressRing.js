/**
 * ProgressRing Component
 * Animated circular progress indicator
 */

import React, {useRef, useEffect} from 'react';
import {View, Text, StyleSheet, Animated} from 'react-native';
import Svg, {Circle} from 'react-native-svg';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

const ProgressRing = ({
  progress = 0, // 0-100
  size = 100,
  strokeWidth = 8,
  color = '#3B82F6',
  backgroundColor = '#E5E7EB',
  showPercentage = true,
  animated = true,
  duration = 1000,
  children,
  style = {},
  textStyle = {},
}) => {
  const animatedValue = useRef(new Animated.Value(0)).current;
  
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  
  useEffect(() => {
    if (animated) {
      Animated.timing(animatedValue, {
        toValue: progress,
        duration,
        useNativeDriver: false,
      }).start();
    } else {
      animatedValue.setValue(progress);
    }
  }, [progress, animated, duration]);

  const strokeDashoffset = animatedValue.interpolate({
    inputRange: [0, 100],
    outputRange: [circumference, 0],
  });

  const displayProgress = Math.round(progress);

  return (
    <View style={[styles.container, {width: size, height: size}, style]}>
      <Svg width={size} height={size} style={styles.svg}>
        {/* Background Circle */}
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Progress Circle */}
        <AnimatedCircle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
      
      {/* Center Content */}
      <View style={styles.centerContent}>
        {children || (showPercentage && (
          <Text style={[styles.percentageText, {fontSize: size * 0.16}, textStyle]}>
            {displayProgress}%
          </Text>
        ))}
      </View>
    </View>
  );
};

// Multi-ring progress component
export const MultiProgressRing = ({
  data = [], // Array of {progress, color, strokeWidth, label}
  size = 120,
  spacing = 4,
  showLabels = false,
  centerContent,
  style = {},
}) => {
  const maxStrokeWidth = Math.max(...data.map(item => item.strokeWidth || 8));
  const totalRadius = size / 2 - maxStrokeWidth / 2;
  
  return (
    <View style={[styles.container, {width: size, height: size}, style]}>
      <Svg width={size} height={size} style={styles.svg}>
        {data.map((item, index) => {
          const strokeWidth = item.strokeWidth || 8;
          const radius = totalRadius - (index * (strokeWidth + spacing));
          const circumference = radius * 2 * Math.PI;
          const strokeDashoffset = circumference - (circumference * (item.progress || 0)) / 100;
          
          return (
            <React.Fragment key={index}>
              {/* Background */}
              <Circle
                cx={size / 2}
                cy={size / 2}
                r={radius}
                stroke="#E5E7EB"
                strokeWidth={strokeWidth}
                fill="transparent"
                opacity={0.3}
              />
              
              {/* Progress */}
              <Circle
                cx={size / 2}
                cy={size / 2}
                r={radius}
                stroke={item.color || '#3B82F6'}
                strokeWidth={strokeWidth}
                fill="transparent"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                transform={`rotate(-90 ${size / 2} ${size / 2})`}
              />
            </React.Fragment>
          );
        })}
      </Svg>
      
      {/* Center Content */}
      <View style={styles.centerContent}>
        {centerContent}
      </View>
      
      {/* Labels */}
      {showLabels && (
        <View style={styles.labelsContainer}>
          {data.map((item, index) => (
            <View key={index} style={styles.labelItem}>
              <View
                style={[
                  styles.labelColor,
                  {backgroundColor: item.color || '#3B82F6'},
                ]}
              />
              <Text style={styles.labelText}>
                {item.label} ({Math.round(item.progress || 0)}%)
              </Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
};

// Stat ring for Pokemon stats
export const StatRing = ({
  stats = {},
  size = 120,
  maxStat = 255,
  colors = {
    hp: '#EF4444',
    attack: '#F97316',
    defense: '#EAB308',
    specialAttack: '#3B82F6',
    specialDefense: '#8B5CF6',
    speed: '#10B981',
  },
  style = {},
}) => {
  const statEntries = Object.entries(stats);
  const data = statEntries.map(([key, value]) => ({
    progress: (value / maxStat) * 100,
    color: colors[key] || '#6B7280',
    strokeWidth: 6,
    label: key.charAt(0).toUpperCase() + key.slice(1),
  }));

  const total = statEntries.reduce((sum, [, value]) => sum + value, 0);

  return (
    <MultiProgressRing
      data={data}
      size={size}
      spacing={2}
      centerContent={
        <View style={styles.statCenter}>
          <Text style={styles.statTotal}>{total}</Text>
          <Text style={styles.statLabel}>Total</Text>
        </View>
      }
      style={style}
    />
  );
};

// Health bar component
export const HealthRing = ({
  currentHP = 100,
  maxHP = 100,
  size = 80,
  animated = true,
  showNumbers = true,
  style = {},
}) => {
  const healthPercentage = (currentHP / maxHP) * 100;
  
  const getHealthColor = () => {
    if (healthPercentage > 60) return '#10B981'; // Green
    if (healthPercentage > 30) return '#F59E0B'; // Yellow
    return '#EF4444'; // Red
  };

  return (
    <ProgressRing
      progress={healthPercentage}
      size={size}
      color={getHealthColor()}
      backgroundColor="#FEE2E2"
      animated={animated}
      showPercentage={false}
      style={style}>
      
      {showNumbers && (
        <View style={styles.healthContent}>
          <Text style={styles.healthNumbers}>
            {currentHP}/{maxHP}
          </Text>
          <Text style={styles.healthLabel}>HP</Text>
        </View>
      )}
    </ProgressRing>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  svg: {
    position: 'absolute',
  },
  centerContent: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  percentageText: {
    fontWeight: 'bold',
    color: '#1F2937',
  },
  labelsContainer: {
    marginTop: 16,
    alignItems: 'flex-start',
  },
  labelItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  labelColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  labelText: {
    fontSize: 12,
    color: '#6B7280',
  },
  statCenter: {
    alignItems: 'center',
  },
  statTotal: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  healthContent: {
    alignItems: 'center',
  },
  healthNumbers: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  healthLabel: {
    fontSize: 10,
    color: '#6B7280',
    marginTop: 2,
  },
});

export default ProgressRing;