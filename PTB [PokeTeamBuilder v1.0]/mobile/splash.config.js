/**
 * Splash Screen Configuration for Production Build
 * Enhanced splash screen with animations and brand identity
 */

module.exports = {
  // Basic splash screen configuration
  backgroundColor: '#3B82F6', // Primary blue color
  image: './assets/splash-icon.png', // App icon for splash
  imageWidth: 200,
  
  // Dark mode splash screen
  dark: {
    backgroundColor: '#0F172A', // Dark slate color
    image: './assets/splash-icon-dark.png',
    imageWidth: 200,
  },
  
  // Platform specific configurations
  android: {
    backgroundColor: '#3B82F6',
    image: './assets/splash-icon-android.png',
    imageWidth: 200,
    resizeMode: 'contain',
    
    // Adaptive icon support
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon-foreground.png',
      backgroundImage: './assets/adaptive-icon-background.png',
      backgroundColor: '#3B82F6',
    },
    
    // Status bar configuration
    statusBar: {
      backgroundColor: '#1D4ED8',
      barStyle: 'light-content',
      translucent: false,
    },
  },
  
  ios: {
    backgroundColor: '#3B82F6',
    image: './assets/splash-icon-ios.png',
    imageWidth: 200,
    resizeMode: 'contain',
    
    // iOS specific splash screen images
    splashScreenImages: [
      {
        image: './assets/ios/splash-1242x2688.png',
        width: 1242,
        height: 2688,
      },
      {
        image: './assets/ios/splash-1125x2436.png',
        width: 1125,
        height: 2436,
      },
      {
        image: './assets/ios/splash-828x1792.png',
        width: 828,
        height: 1792,
      },
      {
        image: './assets/ios/splash-750x1334.png',
        width: 750,
        height: 1334,
      },
      {
        image: './assets/ios/splash-1242x2208.png',
        width: 1242,
        height: 2208,
      },
      {
        image: './assets/ios/splash-2048x2732.png',
        width: 2048,
        height: 2732,
      },
    ],
  },
  
  // Web configuration (if using Expo Web)
  web: {
    backgroundColor: '#3B82F6',
    image: './assets/splash-icon-web.png',
    imageWidth: 200,
    resizeMode: 'contain',
  },
};