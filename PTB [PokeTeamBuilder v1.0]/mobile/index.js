/**
 * React Native Entry Point
 * Main entry file for the Pokemon Team Builder mobile app
 */

import React from 'react';
import {AppRegistry} from 'react-native';
import App from './src/App';
import {name as appName} from './package.json';

// Register the main application component
AppRegistry.registerComponent(appName, () => App);

// Optional: Handle app state changes and development logging
if (__DEV__) {
  console.log('Pokemon Team Builder Mobile App - Development Mode');
}