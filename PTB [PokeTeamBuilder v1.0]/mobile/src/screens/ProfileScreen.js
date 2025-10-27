/**
 * Profile Screen for Pokemon Team Builder Mobile App
 * User profile and account management interface
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Image,
  Modal,
  TextInput,
  Switch,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import {useApp} from '../context/AppContext';
import {ApiService} from '../services/ApiService';
import {AuthService} from '../services/AuthService';

const ProfileScreen = ({navigation}) => {
  const {user, logout, teams, offlineMode} = useApp();
  const [stats, setStats] = useState({
    totalTeams: 0,
    totalBattles: 0,
    winRate: 0,
    totalTrades: 0,
    joinedDate: null,
    rank: 'Beginner',
    experience: 0,
  });
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [editForm, setEditForm] = useState({
    username: '',
    email: '',
    bio: '',
  });
  const [settings, setSettings] = useState({
    notifications: true,
    publicProfile: true,
    showOnlineStatus: true,
    allowTradeRequests: true,
  });

  useEffect(() => {
    loadUserStats();
    if (user) {
      setEditForm({
        username: user.username || '',
        email: user.email || '',
        bio: user.bio || '',
      });
    }
  }, [user, teams]);

  const loadUserStats = async () => {
    try {
      const totalTeams = teams.length;
      
      if (!offlineMode && user && !user.isOffline) {
        try {
          const userStats = await ApiService.getUserStats();
          setStats({
            totalTeams,
            totalBattles: userStats.battles || 0,
            winRate: userStats.winRate || 0,
            totalTrades: userStats.trades || 0,
            joinedDate: userStats.joinedDate,
            rank: userStats.rank || 'Beginner',
            experience: userStats.experience || 0,
          });
        } catch (error) {
          console.error('Failed to load user stats:', error);
          setStats({
            totalTeams,
            totalBattles: 0,
            winRate: 0,
            totalTrades: 0,
            joinedDate: user?.joinedDate || new Date().toISOString(),
            rank: 'Beginner',
            experience: 0,
          });
        }
      } else {
        setStats({
          totalTeams,
          totalBattles: 0,
          winRate: 0,
          totalTrades: 0,
          joinedDate: new Date().toISOString(),
          rank: offlineMode ? 'Offline Mode' : 'Beginner',
          experience: 0,
        });
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            try {
              await logout();
              navigation.navigate('Login');
            } catch (error) {
              Alert.alert('Error', 'Failed to sign out');
            }
          },
        },
      ]
    );
  };

  const handleUpdateProfile = async () => {
    if (!editForm.username.trim()) {
      Alert.alert('Error', 'Username cannot be empty');
      return;
    }

    if (!editForm.email.trim() || !/\S+@\S+\.\S+/.test(editForm.email)) {
      Alert.alert('Error', 'Please enter a valid email');
      return;
    }

    if (offlineMode) {
      Alert.alert('Offline Mode', 'Profile updates require an internet connection');
      return;
    }

    try {
      await ApiService.updateUserProfile(editForm);
      setShowEditProfile(false);
      Alert.alert('Success', 'Profile updated successfully!');
      loadUserStats(); // Reload stats
    } catch (error) {
      Alert.alert('Error', 'Failed to update profile: ' + error.message);
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. All your data will be permanently deleted.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Delete Account',
          style: 'destructive',
          onPress: () => {
            Alert.alert(
              'Confirm Deletion',
              'Type "DELETE" to confirm account deletion',
              [
                {text: 'Cancel', style: 'cancel'},
                {
                  text: 'Confirm',
                  style: 'destructive',
                  onPress: async () => {
                    if (offlineMode) {
                      Alert.alert('Offline Mode', 'Account deletion requires internet connection');
                      return;
                    }
                    try {
                      await ApiService.deleteAccount();
                      await logout();
                      Alert.alert('Account Deleted', 'Your account has been permanently deleted');
                    } catch (error) {
                      Alert.alert('Error', 'Failed to delete account: ' + error.message);
                    }
                  },
                },
              ]
            );
          },
        },
      ]
    );
  };

  const getRankColor = (rank) => {
    const colors = {
      Beginner: '#64748B',
      Bronze: '#CD7F32',
      Silver: '#C0C0C0',
      Gold: '#FFD700',
      Platinum: '#E5E4E2',
      Master: '#B8860B',
      'Offline Mode': '#F59E0B',
    };
    return colors[rank] || '#64748B';
  };

  const getRankIcon = (rank) => {
    const icons = {
      Beginner: 'school',
      Bronze: 'military-tech',
      Silver: 'workspace-premium',
      Gold: 'emoji-events',
      Platinum: 'diamond',
      Master: 'crown',
      'Offline Mode': 'cloud-off',
    };
    return icons[rank] || 'school';
  };

  const menuItems = [
    {
      id: 'edit',
      title: 'Edit Profile',
      icon: 'edit',
      onPress: () => setShowEditProfile(true),
    },
    {
      id: 'teams',
      title: 'My Teams',
      icon: 'group',
      onPress: () => navigation.navigate('Teams'),
      badge: stats.totalTeams,
    },
    {
      id: 'battles',
      title: 'Battle History',
      icon: 'history',
      onPress: () => Alert.alert('Coming Soon', 'Battle history coming soon!'),
      badge: stats.totalBattles,
    },
    {
      id: 'trades',
      title: 'Trade History',
      icon: 'swap-horiz',
      onPress: () => Alert.alert('Coming Soon', 'Trade history coming soon!'),
      badge: stats.totalTrades,
    },
    {
      id: 'achievements',
      title: 'Achievements',
      icon: 'star',
      onPress: () => Alert.alert('Coming Soon', 'Achievements coming soon!'),
    },
    {
      id: 'settings',
      title: 'Settings',
      icon: 'settings',
      onPress: () => Alert.alert('Coming Soon', 'Settings coming soon!'),
    },
  ];

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <LinearGradient
          colors={['#8B5CF6', '#7C3AED']}
          style={styles.header}>
          
          {/* Profile Picture */}
          <View style={styles.profilePictureContainer}>
            <View style={styles.profilePicture}>
              <Icon name="person" size={64} color="white" />
            </View>
            <TouchableOpacity style={styles.editPictureButton}>
              <Icon name="camera-alt" size={16} color="white" />
            </TouchableOpacity>
          </View>

          {/* User Info */}
          <View style={styles.userInfo}>
            <Text style={styles.username}>{user?.username || 'Guest User'}</Text>
            <Text style={styles.email}>{user?.email || 'No email'}</Text>
            
            {/* Rank Badge */}
            <View style={[styles.rankBadge, {backgroundColor: getRankColor(stats.rank)}]}>
              <Icon name={getRankIcon(stats.rank)} size={16} color="white" />
              <Text style={styles.rankText}>{stats.rank}</Text>
            </View>

            {/* Join Date */}
            <Text style={styles.joinDate}>
              Joined {stats.joinedDate ? new Date(stats.joinedDate).toLocaleDateString() : 'Recently'}
            </Text>
          </View>

          {/* Status Indicator */}
          {offlineMode && (
            <View style={styles.statusIndicator}>
              <Icon name="cloud-off" size={16} color="#F59E0B" />
              <Text style={styles.statusText}>Offline</Text>
            </View>
          )}
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
              <Text style={styles.statNumber}>{stats.totalTrades}</Text>
              <Text style={styles.statLabel}>Trades</Text>
            </View>
          </View>
        </View>

        {/* Bio Section */}
        {user?.bio && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>About</Text>
            <Text style={styles.bioText}>{user.bio}</Text>
          </View>
        )}

        {/* Menu Items */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Profile</Text>
          {menuItems.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={styles.menuItem}
              onPress={item.onPress}>
              <View style={styles.menuItemLeft}>
                <View style={styles.menuItemIcon}>
                  <Icon name={item.icon} size={20} color="#64748B" />
                </View>
                <Text style={styles.menuItemTitle}>{item.title}</Text>
              </View>
              <View style={styles.menuItemRight}>
                {item.badge !== undefined && (
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>{item.badge}</Text>
                  </View>
                )}
                <Icon name="chevron-right" size={20} color="#94A3B8" />
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Account Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          
          <TouchableOpacity style={styles.menuItem} onPress={handleLogout}>
            <View style={styles.menuItemLeft}>
              <View style={styles.menuItemIcon}>
                <Icon name="logout" size={20} color="#EF4444" />
              </View>
              <Text style={[styles.menuItemTitle, {color: '#EF4444'}]}>Sign Out</Text>
            </View>
          </TouchableOpacity>

          {!user?.isOffline && (
            <TouchableOpacity style={styles.menuItem} onPress={handleDeleteAccount}>
              <View style={styles.menuItemLeft}>
                <View style={styles.menuItemIcon}>
                  <Icon name="delete-forever" size={20} color="#DC2626" />
                </View>
                <Text style={[styles.menuItemTitle, {color: '#DC2626'}]}>Delete Account</Text>
              </View>
            </TouchableOpacity>
          )}
        </View>

        {/* App Info */}
        <View style={styles.appInfo}>
          <Text style={styles.appInfoText}>Pokemon Team Builder v1.0</Text>
          <Text style={styles.appInfoText}>Made with ❤️ for trainers worldwide</Text>
        </View>
      </ScrollView>

      {/* Edit Profile Modal */}
      <Modal
        visible={showEditProfile}
        animationType="slide"
        onRequestClose={() => setShowEditProfile(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowEditProfile(false)}>
              <Icon name="close" size={24} color="#1E293B" />
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Edit Profile</Text>
            <TouchableOpacity onPress={handleUpdateProfile}>
              <Text style={styles.modalSave}>Save</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Username</Text>
              <TextInput
                style={styles.input}
                value={editForm.username}
                onChangeText={(text) => setEditForm({...editForm, username: text})}
                placeholder="Enter username"
                maxLength={30}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Email</Text>
              <TextInput
                style={styles.input}
                value={editForm.email}
                onChangeText={(text) => setEditForm({...editForm, email: text})}
                placeholder="Enter email"
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Bio</Text>
              <TextInput
                style={[styles.input, styles.bioInput]}
                value={editForm.bio}
                onChangeText={(text) => setEditForm({...editForm, bio: text})}
                placeholder="Tell other trainers about yourself..."
                multiline
                numberOfLines={4}
                maxLength={200}
                textAlignVertical="top"
              />
              <Text style={styles.characterCount}>
                {editForm.bio.length}/200 characters
              </Text>
            </View>
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
    position: 'relative',
  },
  profilePictureContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  profilePicture: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: 'white',
  },
  editPictureButton: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'white',
  },
  userInfo: {
    alignItems: 'center',
  },
  username: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  email: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 12,
  },
  rankBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginBottom: 8,
  },
  rankText: {
    fontSize: 14,
    fontWeight: '600',
    color: 'white',
    marginLeft: 6,
  },
  joinDate: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
  },
  statusIndicator: {
    position: 'absolute',
    top: 60,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(245, 158, 11, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    color: '#F59E0B',
    fontWeight: '500',
    marginLeft: 4,
  },
  statsContainer: {
    paddingHorizontal: 20,
    marginTop: -15,
  },
  statsRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginHorizontal: 6,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  statNumber: {
    fontSize: 28,
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
    backgroundColor: 'white',
    margin: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  bioText: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
    padding: 16,
    paddingTop: 0,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  menuItemIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  menuItemTitle: {
    fontSize: 16,
    color: '#1E293B',
    fontWeight: '500',
  },
  menuItemRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badge: {
    backgroundColor: '#3B82F6',
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginRight: 8,
    minWidth: 20,
    alignItems: 'center',
  },
  badgeText: {
    fontSize: 12,
    color: 'white',
    fontWeight: 'bold',
  },
  appInfo: {
    alignItems: 'center',
    paddingVertical: 24,
    paddingHorizontal: 20,
  },
  appInfoText: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
    marginBottom: 4,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  modalSave: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  inputGroup: {
    marginBottom: 24,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#F9FAFB',
  },
  bioInput: {
    height: 100,
    textAlignVertical: 'top',
  },
  characterCount: {
    fontSize: 12,
    color: '#64748B',
    textAlign: 'right',
    marginTop: 4,
  },
});

export default ProfileScreen;