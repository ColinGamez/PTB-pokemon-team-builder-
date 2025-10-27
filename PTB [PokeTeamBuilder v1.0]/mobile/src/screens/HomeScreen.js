/**
 * Home Screen for Pokemon Team Builder Mobile App
 * Main dashboard with quick access to key features
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Dimensions,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useApp} from '../context/AppContext';
import {ApiService} from '../services/ApiService';

const {width} = Dimensions.get('window');

const HomeScreen = ({navigation}) => {
  const {user, teams, offlineMode, syncStatus, loading} = useApp();
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalTeams: 0,
    totalBattles: 0,
    winRate: 0,
    ranking: 'Beginner'
  });

  useEffect(() => {
    loadStats();
  }, [teams]);

  const loadStats = async () => {
    try {
      // Calculate local stats
      const totalTeams = teams.length;
      
      // Try to get server stats if online
      if (!offlineMode) {
        try {
          const profile = await ApiService.getUserProfile();
          setStats({
            totalTeams,
            totalBattles: profile.battles || 0,
            winRate: profile.winRate || 0,
            ranking: profile.ranking || 'Beginner'
          });
        } catch (error) {
          // Fallback to local stats
          setStats({
            totalTeams,
            totalBattles: 0,
            winRate: 0,
            ranking: 'Beginner'
          });
        }
      } else {
        setStats({
          totalTeams,
          totalBattles: 0,
          winRate: 0,
          ranking: 'Offline Mode'
        });
      }
    } catch (error) {
      console.error('Stats loading error:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  const quickActions = [
    {
      title: 'Build Team',
      icon: 'group-add',
      color: '#3B82F6',
      onPress: () => navigation.navigate('Teams'),
    },
    {
      title: 'Quick Battle',
      icon: 'flash-on',
      color: '#EF4444',
      onPress: () => navigation.navigate('Battle'),
    },
    {
      title: 'Breeding Calc',
      icon: 'child-care',
      color: '#10B981',
      onPress: () => navigation.navigate('Breeding'),
    },
    {
      title: 'Trading',
      icon: 'swap-horiz',
      color: '#F59E0B',
      onPress: () => navigation.navigate('Trading'),
    },
  ];

  const recentTeams = teams.slice(0, 3);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      
      {/* Header */}
      <LinearGradient
        colors={['#3B82F6', '#1D4ED8']}
        style={styles.header}>
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.welcomeText}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.username || 'Trainer'}</Text>
          </View>
          <View style={styles.statusContainer}>
            {offlineMode ? (
              <View style={styles.offlineStatus}>
                <Icon name="cloud-off" size={16} color="#FEF3C7" />
                <Text style={styles.statusText}>Offline</Text>
              </View>
            ) : (
              <View style={styles.onlineStatus}>
                <Icon name="cloud-done" size={16} color="#D1FAE5" />
                <Text style={styles.statusText}>Online</Text>
              </View>
            )}
          </View>
        </View>
      </LinearGradient>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.totalTeams}</Text>
            <Text style={styles.statLabel}>Teams</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.totalBattles}</Text>
            <Text style={styles.statLabel}>Battles</Text>
          </View>
        </View>
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.winRate}%</Text>
            <Text style={styles.statLabel}>Win Rate</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.ranking}</Text>
            <Text style={styles.statLabel}>Rank</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.quickActionCard, {borderLeftColor: action.color}]}
              onPress={action.onPress}>
              <View style={[styles.quickActionIcon, {backgroundColor: action.color}]}>
                <Icon name={action.icon} size={24} color="white" />
              </View>
              <Text style={styles.quickActionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Teams */}
      {recentTeams.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Teams</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Teams')}>
              <Text style={styles.seeAllText}>See All</Text>
            </TouchableOpacity>
          </View>
          {recentTeams.map((team, index) => (
            <TouchableOpacity
              key={team.id || index}
              style={styles.teamCard}
              onPress={() => navigation.navigate('TeamDetail', {team})}>
              <View style={styles.teamInfo}>
                <Text style={styles.teamName}>{team.name}</Text>
                <Text style={styles.teamMeta}>
                  {team.pokemon?.length || 0} Pokemon • {team.format || 'Singles'}
                </Text>
              </View>
              <View style={styles.teamStatus}>
                {team.isLocal && (
                  <Icon name="cloud-off" size={16} color="#6B7280" />
                )}
                <Icon name="chevron-right" size={20} color="#6B7280" />
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Sync Status */}
      {syncStatus.pendingSync > 0 && (
        <View style={styles.syncAlert}>
          <Icon name="sync" size={20} color="#F59E0B" />
          <Text style={styles.syncText}>
            {syncStatus.pendingSync} item(s) waiting to sync
          </Text>
        </View>
      )}

      <View style={styles.bottomSpacing} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  welcomeText: {
    color: '#E0E7FF',
    fontSize: 16,
    fontWeight: '400',
  },
  userName: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 4,
  },
  statusContainer: {
    alignItems: 'flex-end',
  },
  onlineStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  offlineStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(245, 158, 11, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  statsContainer: {
    paddingHorizontal: 20,
    marginTop: -10,
  },
  statsRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '500',
  },
  section: {
    paddingHorizontal: 20,
    marginTop: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  seeAllText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '500',
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 12,
  },
  quickActionCard: {
    width: (width - 60) / 2,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    marginHorizontal: 6,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  quickActionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
  },
  teamCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  teamInfo: {
    flex: 1,
  },
  teamName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 4,
  },
  teamMeta: {
    fontSize: 12,
    color: '#64748B',
  },
  teamStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  syncAlert: {
    backgroundColor: '#FEF3C7',
    margin: 20,
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  syncText: {
    color: '#92400E',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  bottomSpacing: {
    height: 20,
  },
});

export default HomeScreen;