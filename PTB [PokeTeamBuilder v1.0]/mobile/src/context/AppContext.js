/**
 * App Context for Pokemon Team Builder Mobile App
 * Global state management using React Context
 */

import React, {createContext, useContext, useReducer, useEffect} from 'react';
import {OfflineService} from '../services/OfflineService';
import {AuthService} from '../services/AuthService';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  teams: [],
  pokemon: [],
  moves: [],
  abilities: [],
  offlineMode: false,
  syncStatus: {
    isOnline: true,
    pendingSync: 0,
    lastSync: null
  },
  loading: false,
  error: null
};

// Action types
export const ActionTypes = {
  SET_USER: 'SET_USER',
  SET_AUTHENTICATED: 'SET_AUTHENTICATED',
  SET_TEAMS: 'SET_TEAMS',
  ADD_TEAM: 'ADD_TEAM',
  UPDATE_TEAM: 'UPDATE_TEAM',
  DELETE_TEAM: 'DELETE_TEAM',
  SET_POKEMON: 'SET_POKEMON',
  SET_MOVES: 'SET_MOVES',
  SET_ABILITIES: 'SET_ABILITIES',
  SET_OFFLINE_MODE: 'SET_OFFLINE_MODE',
  SET_SYNC_STATUS: 'SET_SYNC_STATUS',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Reducer
const appReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_USER:
      return {...state, user: action.payload};
    case ActionTypes.SET_AUTHENTICATED:
      return {...state, isAuthenticated: action.payload};
    case ActionTypes.SET_TEAMS:
      return {...state, teams: action.payload};
    case ActionTypes.ADD_TEAM:
      return {...state, teams: [...state.teams, action.payload]};
    case ActionTypes.UPDATE_TEAM:
      return {
        ...state,
        teams: state.teams.map(team =>
          team.id === action.payload.id ? action.payload : team
        )
      };
    case ActionTypes.DELETE_TEAM:
      return {
        ...state,
        teams: state.teams.filter(team => team.id !== action.payload)
      };
    case ActionTypes.SET_POKEMON:
      return {...state, pokemon: action.payload};
    case ActionTypes.SET_MOVES:
      return {...state, moves: action.payload};
    case ActionTypes.SET_ABILITIES:
      return {...state, abilities: action.payload};
    case ActionTypes.SET_OFFLINE_MODE:
      return {...state, offlineMode: action.payload};
    case ActionTypes.SET_SYNC_STATUS:
      return {...state, syncStatus: action.payload};
    case ActionTypes.SET_LOADING:
      return {...state, loading: action.payload};
    case ActionTypes.SET_ERROR:
      return {...state, error: action.payload};
    case ActionTypes.CLEAR_ERROR:
      return {...state, error: null};
    default:
      return state;
  }
};

// Create context
const AppContext = createContext();

// Custom hook to use the context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

// Provider component
export const AppProvider = ({children}) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Initialize app data
  useEffect(() => {
    initializeApp();
  }, []);

  // Monitor sync status
  useEffect(() => {
    const updateSyncStatus = () => {
      const status = OfflineService.getSyncStatus();
      dispatch({type: ActionTypes.SET_SYNC_STATUS, payload: status});
      dispatch({type: ActionTypes.SET_OFFLINE_MODE, payload: !status.isOnline});
    };

    const interval = setInterval(updateSyncStatus, 5000); // Check every 5 seconds
    updateSyncStatus(); // Initial check

    return () => clearInterval(interval);
  }, []);

  const initializeApp = async () => {
    try {
      dispatch({type: ActionTypes.SET_LOADING, payload: true});

      // Check authentication
      const isAuth = await AuthService.isAuthenticated();
      dispatch({type: ActionTypes.SET_AUTHENTICATED, payload: isAuth});

      if (isAuth) {
        const user = await AuthService.getCurrentUser();
        dispatch({type: ActionTypes.SET_USER, payload: user});
        
        // Load initial data
        await loadTeams();
        await loadPokemonData();
      }

      dispatch({type: ActionTypes.SET_LOADING, payload: false});
    } catch (error) {
      console.error('App initialization error:', error);
      dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
      dispatch({type: ActionTypes.SET_LOADING, payload: false});
    }
  };

  // Action creators
  const actions = {
    // Authentication actions
    login: async (username, password) => {
      try {
        dispatch({type: ActionTypes.SET_LOADING, payload: true});
        dispatch({type: ActionTypes.CLEAR_ERROR});
        
        const result = await AuthService.login(username, password);
        dispatch({type: ActionTypes.SET_USER, payload: result.user});
        dispatch({type: ActionTypes.SET_AUTHENTICATED, payload: true});
        
        // Load user data after login
        await loadTeams();
        await loadPokemonData();
        
        dispatch({type: ActionTypes.SET_LOADING, payload: false});
        return result;
      } catch (error) {
        dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
        dispatch({type: ActionTypes.SET_LOADING, payload: false});
        throw error;
      }
    },

    logout: async () => {
      try {
        await AuthService.logout();
        dispatch({type: ActionTypes.SET_USER, payload: null});
        dispatch({type: ActionTypes.SET_AUTHENTICATED, payload: false});
        dispatch({type: ActionTypes.SET_TEAMS, payload: []});
      } catch (error) {
        console.error('Logout error:', error);
      }
    },

    // Team actions
    loadTeams: async () => {
      await loadTeams();
    },

    createTeam: async (teamData) => {
      try {
        const team = await OfflineService.saveTeamOffline(teamData);
        dispatch({type: ActionTypes.ADD_TEAM, payload: team});
        return team;
      } catch (error) {
        dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
        throw error;
      }
    },

    updateTeam: async (teamData) => {
      try {
        const team = await OfflineService.saveTeamOffline(teamData);
        dispatch({type: ActionTypes.UPDATE_TEAM, payload: team});
        return team;
      } catch (error) {
        dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
        throw error;
      }
    },

    deleteTeam: async (teamId) => {
      try {
        await OfflineService.deleteTeamOffline(teamId);
        dispatch({type: ActionTypes.DELETE_TEAM, payload: teamId});
      } catch (error) {
        dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
        throw error;
      }
    },

    // Pokemon data actions
    loadPokemonData: async () => {
      await loadPokemonData();
    },

    getPokemonDetail: async (pokemonId) => {
      try {
        return await OfflineService.getPokemonDetail(pokemonId);
      } catch (error) {
        dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
        throw error;
      }
    },

    // Utility actions
    clearError: () => {
      dispatch({type: ActionTypes.CLEAR_ERROR});
    },

    setLoading: (loading) => {
      dispatch({type: ActionTypes.SET_LOADING, payload: loading});
    }
  };

  // Helper functions
  const loadTeams = async () => {
    try {
      const teams = await OfflineService.getOfflineTeams();
      dispatch({type: ActionTypes.SET_TEAMS, payload: teams});
    } catch (error) {
      console.error('Load teams error:', error);
      dispatch({type: ActionTypes.SET_ERROR, payload: error.message});
    }
  };

  const loadPokemonData = async () => {
    try {
      // Load cached or fresh Pokemon data
      const pokemon = await OfflineService.getPokemonList();
      dispatch({type: ActionTypes.SET_POKEMON, payload: pokemon});
    } catch (error) {
      console.error('Load Pokemon data error:', error);
      // Don't set error for Pokemon data - it's not critical for app function
    }
  };

  const value = {
    ...state,
    ...actions
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};