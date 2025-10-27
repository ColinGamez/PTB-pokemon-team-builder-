/**
 * Offline Service for Pokemon Team Builder Mobile App
 * Handles data synchronization and offline functionality
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import {ApiService} from './ApiService';

class OfflineServiceClass {
  constructor() {
    this.isInitialized = false;
    this.syncQueue = [];
    this.isOnline = true;
    this.netInfoUnsubscribe = null;
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      // Set up network status monitoring
      this.netInfoUnsubscribe = NetInfo.addEventListener(state => {
        const wasOnline = this.isOnline;
        this.isOnline = state.isConnected && state.isInternetReachable;
        
        if (!wasOnline && this.isOnline) {
          // Just came back online - sync data
          this.syncOfflineData();
        }
      });

      // Get initial network state
      const netInfo = await NetInfo.fetch();
      this.isOnline = netInfo.isConnected && netInfo.isInternetReachable;

      // Load sync queue from storage
      await this.loadSyncQueue();

      this.isInitialized = true;
      console.log('OfflineService initialized, online:', this.isOnline);
    } catch (error) {
      console.error('OfflineService initialization error:', error);
    }
  }

  // Network status
  async isOffline() {
    return !this.isOnline;
  }

  // Data caching methods
  async cacheData(key, data, expiration = 24 * 60 * 60 * 1000) { // 24 hours default
    try {
      const cacheItem = {
        data,
        timestamp: Date.now(),
        expiration
      };
      await AsyncStorage.setItem(`cache_${key}`, JSON.stringify(cacheItem));
    } catch (error) {
      console.error('Cache storage error:', error);
    }
  }

  async getCachedData(key) {
    try {
      const cached = await AsyncStorage.getItem(`cache_${key}`);
      if (!cached) return null;

      const cacheItem = JSON.parse(cached);
      const age = Date.now() - cacheItem.timestamp;

      if (age > cacheItem.expiration) {
        // Cache expired
        await AsyncStorage.removeItem(`cache_${key}`);
        return null;
      }

      return cacheItem.data;
    } catch (error) {
      console.error('Cache retrieval error:', error);
      return null;
    }
  }

  async clearCache(key = null) {
    try {
      if (key) {
        await AsyncStorage.removeItem(`cache_${key}`);
      } else {
        // Clear all cache items
        const keys = await AsyncStorage.getAllKeys();
        const cacheKeys = keys.filter(k => k.startsWith('cache_'));
        await AsyncStorage.multiRemove(cacheKeys);
      }
    } catch (error) {
      console.error('Cache clear error:', error);
    }
  }

  // Offline team management
  async saveTeamOffline(team) {
    try {
      // Generate local ID if new team
      if (!team.id) {
        team.id = `local_${Date.now()}`;
        team.isLocal = true;
      }

      // Save to local storage
      const teams = await this.getOfflineTeams();
      const existingIndex = teams.findIndex(t => t.id === team.id);
      
      if (existingIndex >= 0) {
        teams[existingIndex] = team;
      } else {
        teams.push(team);
      }

      await AsyncStorage.setItem('offline_teams', JSON.stringify(teams));

      // Add to sync queue if we have changes to sync
      if (!team.isLocal || team.needsSync) {
        await this.addToSyncQueue('team', team.isLocal ? 'create' : 'update', team);
      }

      return team;
    } catch (error) {
      console.error('Offline team save error:', error);
      throw error;
    }
  }

  async getOfflineTeams() {
    try {
      const teams = await AsyncStorage.getItem('offline_teams');
      return teams ? JSON.parse(teams) : [];
    } catch (error) {
      console.error('Offline teams retrieval error:', error);
      return [];
    }
  }

  async deleteTeamOffline(teamId) {
    try {
      const teams = await this.getOfflineTeams();
      const filteredTeams = teams.filter(t => t.id !== teamId);
      await AsyncStorage.setItem('offline_teams', JSON.stringify(filteredTeams));

      // Add deletion to sync queue if it's a server team
      const deletedTeam = teams.find(t => t.id === teamId);
      if (deletedTeam && !deletedTeam.isLocal) {
        await this.addToSyncQueue('team', 'delete', {id: teamId});
      }
    } catch (error) {
      console.error('Offline team deletion error:', error);
      throw error;
    }
  }

  // Sync queue management
  async addToSyncQueue(type, action, data) {
    try {
      const queueItem = {
        id: Date.now(),
        type,
        action,
        data,
        timestamp: Date.now(),
        retries: 0
      };

      this.syncQueue.push(queueItem);
      await this.saveSyncQueue();

      // Try to sync immediately if online
      if (this.isOnline) {
        this.syncOfflineData();
      }
    } catch (error) {
      console.error('Sync queue error:', error);
    }
  }

  async loadSyncQueue() {
    try {
      const queue = await AsyncStorage.getItem('sync_queue');
      this.syncQueue = queue ? JSON.parse(queue) : [];
    } catch (error) {
      console.error('Sync queue load error:', error);
      this.syncQueue = [];
    }
  }

  async saveSyncQueue() {
    try {
      await AsyncStorage.setItem('sync_queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.error('Sync queue save error:', error);
    }
  }

  async syncOfflineData() {
    if (!this.isOnline || this.syncQueue.length === 0) return;

    console.log(`Syncing ${this.syncQueue.length} items...`);

    const failedItems = [];

    for (const item of this.syncQueue) {
      try {
        await this.syncItem(item);
      } catch (error) {
        console.error(`Sync failed for item ${item.id}:`, error);
        item.retries = (item.retries || 0) + 1;
        
        // Keep trying up to 3 times
        if (item.retries < 3) {
          failedItems.push(item);
        }
      }
    }

    // Update sync queue with failed items
    this.syncQueue = failedItems;
    await this.saveSyncQueue();

    console.log(`Sync complete. ${failedItems.length} items failed.`);
  }

  async syncItem(item) {
    switch (item.type) {
      case 'team':
        await this.syncTeam(item);
        break;
      default:
        console.warn(`Unknown sync item type: ${item.type}`);
    }
  }

  async syncTeam(item) {
    switch (item.action) {
      case 'create':
        const createdTeam = await ApiService.createTeam(item.data);
        // Update local team with server ID
        await this.updateLocalTeamId(item.data.id, createdTeam.id);
        break;
      case 'update':
        await ApiService.updateTeam(item.data.id, item.data);
        break;
      case 'delete':
        await ApiService.deleteTeam(item.data.id);
        break;
    }
  }

  async updateLocalTeamId(localId, serverId) {
    try {
      const teams = await this.getOfflineTeams();
      const team = teams.find(t => t.id === localId);
      if (team) {
        team.id = serverId;
        team.isLocal = false;
        team.needsSync = false;
        await AsyncStorage.setItem('offline_teams', JSON.stringify(teams));
      }
    } catch (error) {
      console.error('Local team ID update error:', error);
    }
  }

  // Pokemon data caching with smart refresh
  async getPokemonList(generation = 'all', forceRefresh = false) {
    const cacheKey = `pokemon_list_${generation}`;
    
    if (!forceRefresh && !this.isOnline) {
      // Return cached data when offline
      const cached = await this.getCachedData(cacheKey);
      if (cached) return cached;
      throw new Error('No cached Pokemon data available offline');
    }

    if (!forceRefresh) {
      // Check cache first
      const cached = await this.getCachedData(cacheKey);
      if (cached) return cached;
    }

    try {
      // Fetch from server
      const data = await ApiService.getPokemonList(generation);
      await this.cacheData(cacheKey, data);
      return data;
    } catch (error) {
      // Fallback to cache if server fails
      const cached = await this.getCachedData(cacheKey);
      if (cached) return cached;
      throw error;
    }
  }

  async getPokemonDetail(pokemonId, forceRefresh = false) {
    const cacheKey = `pokemon_detail_${pokemonId}`;
    
    if (!forceRefresh && !this.isOnline) {
      const cached = await this.getCachedData(cacheKey);
      if (cached) return cached;
      throw new Error('No cached Pokemon detail available offline');
    }

    if (!forceRefresh) {
      const cached = await this.getCachedData(cacheKey);
      if (cached) return cached;
    }

    try {
      const data = await ApiService.getPokemonDetail(pokemonId);
      await this.cacheData(cacheKey, data);
      return data;
    } catch (error) {
      const cached = await this.getCachedData(cacheKey);
      if (cached) return cached;
      throw error;
    }
  }

  // Cleanup method
  async cleanup() {
    if (this.netInfoUnsubscribe) {
      this.netInfoUnsubscribe();
    }
  }

  // Get sync status
  getSyncStatus() {
    return {
      isOnline: this.isOnline,
      pendingSync: this.syncQueue.length,
      lastSync: null // Could be enhanced to track last sync time
    };
  }
}

export const OfflineService = new OfflineServiceClass();