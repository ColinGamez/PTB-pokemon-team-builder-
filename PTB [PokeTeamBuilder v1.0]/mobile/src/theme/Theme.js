/**
 * Pokemon Team Builder Mobile App Theme Configuration
 * Comprehensive design system with Pokemon-inspired colors and styling
 */

import { Dimensions } from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

// Base color palette
const Colors = {
  // Primary brand colors
  primary: '#3B82F6',      // Blue 500
  primaryDark: '#1D4ED8',  // Blue 700
  primaryLight: '#93C5FD', // Blue 300
  
  // Secondary colors
  secondary: '#8B5CF6',    // Violet 500
  secondaryDark: '#7C3AED', // Violet 600
  secondaryLight: '#C4B5FD', // Violet 300
  
  // Status colors
  success: '#10B981',      // Green 500
  successDark: '#059669',  // Green 600
  successLight: '#6EE7B7', // Green 300
  
  warning: '#F59E0B',      // Amber 500
  warningDark: '#D97706',  // Amber 600
  warningLight: '#FCD34D', // Amber 300
  
  error: '#EF4444',        // Red 500
  errorDark: '#DC2626',    // Red 600
  errorLight: '#FCA5A5',   // Red 300
  
  info: '#06B6D4',         // Cyan 500
  infoDark: '#0891B2',     // Cyan 600
  infoLight: '#67E8F9',    // Cyan 300
  
  // Neutral colors
  white: '#FFFFFF',
  black: '#000000',
  
  // Gray scale
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
  gray900: '#111827',
  
  // Pokemon type colors
  types: {
    normal: '#A8A878',
    fighting: '#C03028',
    flying: '#A890F0',
    poison: '#A040A0',
    ground: '#E0C068',
    rock: '#B8A038',
    bug: '#A8B820',
    ghost: '#705898',
    steel: '#B8B8D0',
    fire: '#F08030',
    water: '#6890F0',
    grass: '#78C850',
    electric: '#F8D030',
    psychic: '#F85888',
    ice: '#98D8D8',
    dragon: '#7038F8',
    dark: '#705848',
    fairy: '#EE99AC',
  },
  
  // Background colors
  background: {
    primary: '#F8FAFC',     // Gray 50
    secondary: '#F1F5F9',   // Slate 100
    tertiary: '#FFFFFF',    // White
    elevated: '#FFFFFF',    // White with shadow
  },
  
  // Surface colors
  surface: {
    primary: '#FFFFFF',
    secondary: '#F8FAFC',
    tertiary: '#F1F5F9',
    disabled: '#F3F4F6',
  },
  
  // Text colors
  text: {
    primary: '#1F2937',     // Gray 800
    secondary: '#4B5563',   // Gray 600
    tertiary: '#6B7280',    // Gray 500
    disabled: '#9CA3AF',    // Gray 400
    inverse: '#FFFFFF',     // White
    link: '#3B82F6',        // Blue 500
  },
  
  // Border colors
  border: {
    primary: '#E5E7EB',     // Gray 200
    secondary: '#D1D5DB',   // Gray 300
    focus: '#3B82F6',       // Blue 500
    error: '#EF4444',       // Red 500
  },
  
  // Shadow colors
  shadow: {
    light: 'rgba(0, 0, 0, 0.05)',
    medium: 'rgba(0, 0, 0, 0.1)',
    dark: 'rgba(0, 0, 0, 0.15)',
    intense: 'rgba(0, 0, 0, 0.25)',
  },
  
  // Overlay colors
  overlay: {
    light: 'rgba(0, 0, 0, 0.3)',
    medium: 'rgba(0, 0, 0, 0.5)',
    dark: 'rgba(0, 0, 0, 0.7)',
  },
};

// Dark theme colors
const DarkColors = {
  ...Colors,
  
  // Override specific colors for dark theme
  background: {
    primary: '#0F172A',     // Slate 900
    secondary: '#1E293B',   // Slate 800
    tertiary: '#334155',    // Slate 700
    elevated: '#1E293B',    // Slate 800 with shadow
  },
  
  surface: {
    primary: '#1E293B',     // Slate 800
    secondary: '#334155',   // Slate 700
    tertiary: '#475569',    // Slate 600
    disabled: '#64748B',    // Slate 500
  },
  
  text: {
    primary: '#F8FAFC',     // Slate 50
    secondary: '#E2E8F0',   // Slate 200
    tertiary: '#CBD5E1',    // Slate 300
    disabled: '#94A3B8',    // Slate 400
    inverse: '#1F2937',     // Gray 800
    link: '#60A5FA',        // Blue 400
  },
  
  border: {
    primary: '#475569',     // Slate 600
    secondary: '#64748B',   // Slate 500
    focus: '#60A5FA',       // Blue 400
    error: '#F87171',       // Red 400
  },
  
  shadow: {
    light: 'rgba(0, 0, 0, 0.2)',
    medium: 'rgba(0, 0, 0, 0.3)',
    dark: 'rgba(0, 0, 0, 0.4)',
    intense: 'rgba(0, 0, 0, 0.6)',
  },
};

// Typography scale
const Typography = {
  // Font families
  fonts: {
    regular: 'System',
    medium: 'System',
    semiBold: 'System',
    bold: 'System',
    mono: 'Courier',
  },
  
  // Font sizes
  sizes: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 28,
    '4xl': 32,
    '5xl': 40,
    '6xl': 48,
  },
  
  // Line heights
  lineHeights: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
    loose: 1.8,
  },
  
  // Font weights
  weights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  
  // Typography styles
  styles: {
    display: {
      fontSize: 28,
      fontWeight: '700',
      lineHeight: 34,
    },
    headline: {
      fontSize: 24,
      fontWeight: '600',
      lineHeight: 29,
    },
    title: {
      fontSize: 20,
      fontWeight: '600',
      lineHeight: 24,
    },
    subtitle: {
      fontSize: 18,
      fontWeight: '500',
      lineHeight: 22,
    },
    body: {
      fontSize: 16,
      fontWeight: '400',
      lineHeight: 22,
    },
    bodyMedium: {
      fontSize: 16,
      fontWeight: '500',
      lineHeight: 22,
    },
    caption: {
      fontSize: 14,
      fontWeight: '500',
      lineHeight: 18,
    },
    small: {
      fontSize: 12,
      fontWeight: '500',
      lineHeight: 16,
    },
    tiny: {
      fontSize: 10,
      fontWeight: '500',
      lineHeight: 14,
    },
  },
};

// Spacing scale
const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  '2xl': 24,
  '3xl': 32,
  '4xl': 40,
  '5xl': 48,
  '6xl': 64,
  '7xl': 80,
  '8xl': 96,
};

// Border radius scale
const BorderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 20,
  '3xl': 24,
  full: 9999,
};

// Shadow styles
const Shadows = {
  sm: {
    shadowColor: Colors.shadow.light,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: Colors.shadow.medium,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 4,
    elevation: 4,
  },
  lg: {
    shadowColor: Colors.shadow.dark,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 8,
  },
  xl: {
    shadowColor: Colors.shadow.intense,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 16,
  },
};

// Layout dimensions
const Layout = {
  screen: {
    width: screenWidth,
    height: screenHeight,
  },
  
  // Common dimensions
  header: {
    height: 56,
  },
  
  tabBar: {
    height: 60,
  },
  
  // Container sizes
  container: {
    maxWidth: 1024,
    padding: Spacing.lg,
  },
  
  // Component sizes
  button: {
    height: {
      sm: 32,
      md: 40,
      lg: 48,
      xl: 56,
    },
    minWidth: {
      sm: 64,
      md: 80,
      lg: 96,
      xl: 120,
    },
  },
  
  input: {
    height: {
      sm: 32,
      md: 40,
      lg: 48,
    },
  },
  
  card: {
    minHeight: 120,
    padding: Spacing.lg,
  },
  
  // Pokemon specific sizes
  pokemon: {
    sprite: {
      sm: 48,
      md: 64,
      lg: 96,
      xl: 128,
    },
    card: {
      sm: { width: 160, height: 200 },
      md: { width: 200, height: 240 },
      lg: { width: 240, height: 280 },
    },
  },
  
  team: {
    card: {
      height: 120,
      pokemonPreview: 40,
    },
  },
};

// Animation timings
const Animations = {
  duration: {
    fast: 150,
    normal: 250,
    slow: 350,
    verySlow: 500,
  },
  
  easing: {
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
};

// Theme objects
const LightTheme = {
  colors: Colors,
  typography: Typography,
  spacing: Spacing,
  borderRadius: BorderRadius,
  shadows: Shadows,
  layout: Layout,
  animations: Animations,
  dark: false,
};

const DarkTheme = {
  colors: DarkColors,
  typography: Typography,
  spacing: Spacing,
  borderRadius: BorderRadius,
  shadows: Shadows,
  layout: Layout,
  animations: Animations,
  dark: true,
};

// Utility functions
export const getTypeColor = (type) => {
  return Colors.types[type?.toLowerCase()] || Colors.gray400;
};

export const getStatColor = (statValue) => {
  if (statValue >= 130) return Colors.success;
  if (statValue >= 100) return Colors.warning;
  if (statValue >= 70) return Colors.info;
  return Colors.error;
};

export const getThemeColor = (theme, colorPath) => {
  const paths = colorPath.split('.');
  return paths.reduce((obj, path) => obj?.[path], theme.colors);
};

export const createShadow = (elevation = 1, color = Colors.shadow.medium) => {
  return {
    shadowColor: color,
    shadowOffset: { width: 0, height: elevation },
    shadowOpacity: 1,
    shadowRadius: elevation * 2,
    elevation: elevation * 2,
  };
};

export { Colors, DarkColors, Typography, Spacing, BorderRadius, Shadows, Layout, Animations };
export { LightTheme, DarkTheme };
export default LightTheme;