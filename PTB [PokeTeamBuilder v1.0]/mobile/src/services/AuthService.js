/**
 * Authentication Service for Pokemon Team Builder Mobile App
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import {ApiService} from './ApiService';

class AuthServiceClass {
  constructor() {
    this.currentUser = null;
    this.token = null;
  }

  async login(username, password) {
    try {
      const response = await ApiService.login(username, password);
      
      if (response.success) {
        this.token = response.token;
        this.currentUser = response.user;
        
        // Store in AsyncStorage
        await AsyncStorage.setItem('authToken', this.token);
        await AsyncStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        
        return { success: true, user: this.currentUser, token: this.token };
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  }

  async register(userData) {
    try {
      const response = await ApiService.register(userData);
      
      if (response.success) {
        // Auto-login after successful registration
        return await this.login(userData.username, userData.password);
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      throw error;
    }
  }

  async logout() {
    try {
      // Clear stored data
      await AsyncStorage.multiRemove(['authToken', 'currentUser']);
      this.token = null;
      this.currentUser = null;
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async getCurrentUser() {
    if (!this.currentUser) {
      try {
        const userData = await AsyncStorage.getItem('currentUser');
        this.currentUser = userData ? JSON.parse(userData) : null;
      } catch (error) {
        console.error('Get current user error:', error);
      }
    }
    return this.currentUser;
  }

  async getToken() {
    if (!this.token) {
      try {
        this.token = await AsyncStorage.getItem('authToken');
      } catch (error) {
        console.error('Get token error:', error);
      }
    }
    return this.token;
  }

  async isAuthenticated() {
    const token = await this.getToken();
    const user = await this.getCurrentUser();
    return !!(token && user);
  }

  async validateToken() {
    try {
      const token = await this.getToken();
      if (!token) return false;
      
      await ApiService.validateToken(token);
      return true;
    } catch (error) {
      // Token invalid, clear auth data
      await this.logout();
      return false;
    }
  }
}

export const AuthService = new AuthServiceClass();