/**
 * API Service for Pokemon Team Builder Mobile App
 * Handles all communication with the web server backend
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {Alert} from 'react-native';

// Configuration
const BASE_URL = __DEV__ 
  ? 'http://localhost:5000'  // Development server
  : 'https://your-domain.com'; // Production server

class ApiServiceClass {
  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  handleAuthError = async () => {
    await AsyncStorage.multiRemove(['authToken', 'currentUser']);
    Alert.alert('Session Expired', 'Please log in again');
    // Navigate to login screen would be handled by app state
  };

  // Authentication APIs
  async login(username, password) {
    try {
      const response = await this.client.post('/api/auth/login', {
        username,
        password,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async register(userData) {
    try {
      const response = await this.client.post('/api/auth/register', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async validateToken(token) {
    try {
      const response = await this.client.get('/api/auth/validate', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Team Management APIs
  async getTeams() {
    try {
      const response = await this.client.get('/api/teams');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTeam(teamData) {
    try {
      const response = await this.client.post('/api/teams', teamData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateTeam(teamId, teamData) {
    try {
      const response = await this.client.put(`/api/teams/${teamId}`, teamData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteTeam(teamId) {
    try {
      const response = await this.client.delete(`/api/teams/${teamId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async analyzeTeam(teamId) {
    try {
      const response = await this.client.get(`/api/teams/${teamId}/analyze`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Pokemon Data APIs
  async getPokemonList(generation = 'all') {
    try {
      const response = await this.client.get('/api/pokemon', {
        params: { generation }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPokemonDetail(pokemonId) {
    try {
      const response = await this.client.get(`/api/pokemon/${pokemonId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getMoves() {
    try {
      const response = await this.client.get('/api/moves');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAbilities() {
    try {
      const response = await this.client.get('/api/abilities');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Battle APIs
  async getBattles() {
    try {
      const response = await this.client.get('/api/battles');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createBattle(battleData) {
    try {
      const response = await this.client.post('/api/multiplayer/create_battle', battleData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async joinBattle(battleId) {
    try {
      const response = await this.client.post('/api/multiplayer/join_battle', {
        battle_id: battleId
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getBattleState(battleId) {
    try {
      const response = await this.client.get(`/api/multiplayer/battle/${battleId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Breeding Calculator APIs
  async calculateBreeding(parentData) {
    try {
      const response = await this.client.post('/api/breeding/calculate', parentData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getBreedingPath(targetPokemon) {
    try {
      const response = await this.client.post('/api/breeding/path', {
        target: targetPokemon
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Tournament APIs
  async getTournaments() {
    try {
      const response = await this.client.get('/api/tournaments');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async joinTournament(tournamentId) {
    try {
      const response = await this.client.post(`/api/tournaments/${tournamentId}/join`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Trading APIs
  async getTradingOffers() {
    try {
      const response = await this.client.get('/api/trading/offers');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTradingOffer(offerData) {
    try {
      const response = await this.client.post('/api/trading/offers', offerData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // User Profile APIs
  async getUserProfile() {
    try {
      const response = await this.client.get('/api/user/profile');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateUserProfile(profileData) {
    try {
      const response = await this.client.put('/api/user/profile', profileData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Status APIs
  async getServerStatus() {
    try {
      const response = await this.client.get('/api/status');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  handleError(error) {
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.message || 'Server error occurred';
      return new Error(message);
    } else if (error.request) {
      // Network error
      return new Error('Network error - please check your connection');
    } else {
      // Other error
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  // Utility methods
  async checkConnection() {
    try {
      await this.getServerStatus();
      return true;
    } catch (error) {
      return false;
    }
  }

  getBaseUrl() {
    return BASE_URL;
  }
}

export const ApiService = new ApiServiceClass();