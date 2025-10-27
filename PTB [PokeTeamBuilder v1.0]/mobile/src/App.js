/**
 * Pokemon Team Builder Mobile App - Main Application Component
 * Enhanced with theme provider, navigation, error boundaries, and performance optimizations
 */

import React, { useEffect, useState, useMemo } from 'react';
import {
  StatusBar,
  LogBox,
  Platform,
  UIManager,
  AppState,
  useColorScheme,
  Alert,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

// Theme and context
import { LightTheme, DarkTheme } from './theme/Theme';
import { AppProvider } from './context/AppContext';
import { ErrorBoundary } from './components/ErrorBoundary';

// Screens
import HomeScreen from './screens/HomeScreen';
import TeamsScreen from './screens/TeamsScreen';
import TeamBuilderScreen from './screens/TeamBuilderScreen';
import BattleScreen from './screens/BattleScreen';
import BreedingScreen from './screens/BreedingScreen';
import TradingScreen from './screens/TradingScreen';
import ProfileScreen from './screens/ProfileScreen';
import SettingsScreen from './screens/SettingsScreen';
import LoginScreen from './screens/LoginScreen';
import PokemonDetailScreen from './screens/PokemonDetailScreen';
import TeamDetailScreen from './screens/TeamDetailScreen';
import BattleRoomScreen from './screens/BattleRoomScreen';

// Services
import { AuthService } from './services/AuthService';
import { ApiService } from './services/ApiService';
import { OfflineService } from './services/OfflineService';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Tab Navigator Component
const TabNavigator = () => {
  const tabScreens = [
    {
      name: 'Home',
      component: HomeScreen,
      icon: 'home',
      label: 'Home',
    },
    {
      name: 'Teams',
      component: TeamsScreen,
      icon: 'group',
      label: 'Teams',
    },
    {
      name: 'Builder',
      component: TeamBuilderScreen,
      icon: 'add-circle',
      label: 'Builder',
    },
    {
      name: 'Battle',
      component: BattleScreen,
      icon: 'flash-on',
      label: 'Battle',
    },
    {
      name: 'Profile',
      component: ProfileScreen,
      icon: 'person',
      label: 'Profile',
    },
  ];

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const screen = tabScreens.find(s => s.name === route.name);
          return (
            <Icon
              name={screen?.icon || 'help'}
              size={size}
              color={color}
            />
          );
        },
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: '#6B7280',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E5E7EB',
          paddingTop: 4,
          paddingBottom: Platform.OS === 'ios' ? 20 : 4,
          height: Platform.OS === 'ios' ? 80 : 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
          marginTop: 2,
        },
        headerShown: false,
      })}
    >
      {tabScreens.map((screen) => (
        <Tab.Screen
          key={screen.name}
          name={screen.name}
          component={screen.component}
          options={{
            tabBarLabel: screen.label,
          }}
        />
      ))}
    </Tab.Navigator>
  );
};

// Main App Component
const App = () => {
  const isDarkMode = useColorScheme() === 'dark';
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check authentication status
      const token = await AsyncStorage.getItem('authToken');
      const user = await AsyncStorage.getItem('currentUser');
      
      if (token && user) {
        // Verify token with server
        try {
          await ApiService.validateToken(token);
          setIsAuthenticated(true);
        } catch (error) {
          // Token invalid, clear storage
          await AsyncStorage.multiRemove(['authToken', 'currentUser']);
          setIsAuthenticated(false);
        }
      }

      // Initialize offline service
      await OfflineService.initialize();
      
      // Check if we're in offline mode
      const offline = await OfflineService.isOffline();
      setOfflineMode(offline);

      setIsLoading(false);
    } catch (error) {
      console.error('App initialization error:', error);
      Alert.alert('Error', 'Failed to initialize app');
      setIsLoading(false);
    }
  };

  const handleLogin = async (token, user) => {
    try {
      await AsyncStorage.setItem('authToken', token);
      await AsyncStorage.setItem('currentUser', JSON.stringify(user));
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login storage error:', error);
      Alert.alert('Error', 'Failed to save login data');
    }
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.multiRemove(['authToken', 'currentUser']);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    // Show loading screen
    return null; // Add a proper loading component here
  }

  return (
    <AppProvider value={{
      isAuthenticated,
      offlineMode,
      onLogin: handleLogin,
      onLogout: handleLogout,
    }}>
      <NavigationContainer theme={isDarkMode ? PokemonDarkTheme : PokemonTheme}>
        <StatusBar
          barStyle={isDarkMode ? 'light-content' : 'dark-content'}
          backgroundColor={isDarkMode ? '#0F172A' : '#F8FAFC'}
        />
        <Stack.Navigator screenOptions={{headerShown: false}}>
          {!isAuthenticated ? (
            <Stack.Screen name="Login" component={LoginScreen} />
          ) : (
            <>
              <Stack.Screen name="Main" component={TabNavigator} />
              <Stack.Screen name="PokemonDetail" component={PokemonDetailScreen} />
              <Stack.Screen name="TeamDetail" component={TeamDetailScreen} />
              <Stack.Screen name="BattleRoom" component={BattleRoomScreen} />
              <Stack.Screen name="Breeding" component={BreedingScreen} />
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </AppProvider>
  );
};

export default App;