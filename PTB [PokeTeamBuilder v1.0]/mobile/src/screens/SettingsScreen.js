/**
 * Settings Screen for Pokemon Team Builder Mobile App
 * App settings and preferences management
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Switch,
  Alert,
  Modal,
  FlatList,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useApp} from '../context/AppContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SettingsScreen = ({navigation}) => {
  const {user, offlineMode} = useApp();
  const [settings, setSettings] = useState({
    // Notifications
    pushNotifications: true,
    battleNotifications: true,
    tradeNotifications: true,
    systemNotifications: true,
    
    // Privacy
    publicProfile: true,
    showOnlineStatus: true,
    allowTradeRequests: true,
    shareUsageData: false,
    
    // Appearance
    darkMode: false,
    colorTheme: 'blue',
    language: 'English',
    
    // Gameplay
    autoSave: true,
    offlineMode: false,
    syncOnWifi: true,
    showTutorials: true,
    
    // Advanced
    cacheSize: '100MB',
    apiTimeout: 30,
    debugMode: false,
  });

  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);

  const themes = [
    {id: 'blue', name: 'Ocean Blue', color: '#3B82F6'},
    {id: 'green', name: 'Forest Green', color: '#10B981'},
    {id: 'purple', name: 'Royal Purple', color: '#8B5CF6'},
    {id: 'red', name: 'Fire Red', color: '#EF4444'},
    {id: 'orange', name: 'Electric Orange', color: '#F59E0B'},
    {id: 'pink', name: 'Fairy Pink', color: '#EC4899'},
  ];

  const languages = [
    {id: 'en', name: 'English', flag: '🇺🇸'},
    {id: 'es', name: 'Español', flag: '🇪🇸'},
    {id: 'fr', name: 'Français', flag: '🇫🇷'},
    {id: 'de', name: 'Deutsch', flag: '🇩🇪'},
    {id: 'ja', name: '日本語', flag: '🇯🇵'},
    {id: 'ko', name: '한국어', flag: '🇰🇷'},
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const savedSettings = await AsyncStorage.getItem('app_settings');
      if (savedSettings) {
        setSettings({...settings, ...JSON.parse(savedSettings)});
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async (newSettings) => {
    try {
      await AsyncStorage.setItem('app_settings', JSON.stringify(newSettings));
      setSettings(newSettings);
    } catch (error) {
      console.error('Failed to save settings:', error);
      Alert.alert('Error', 'Failed to save settings');
    }
  };

  const updateSetting = (key, value) => {
    const newSettings = {...settings, [key]: value};
    saveSettings(newSettings);
  };

  const clearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will remove all cached data. The app may take longer to load content next time.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            try {
              // Clear specific cache keys, not all AsyncStorage
              const keysToRemove = [
                'pokemon_data_cache',
                'team_cache',
                'battle_cache',
                'image_cache',
              ];
              await AsyncStorage.multiRemove(keysToRemove);
              Alert.alert('Success', 'Cache cleared successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to clear cache');
            }
          },
        },
      ]
    );
  };

  const resetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'This will reset all settings to their default values.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            const defaultSettings = {
              pushNotifications: true,
              battleNotifications: true,
              tradeNotifications: true,
              systemNotifications: true,
              publicProfile: true,
              showOnlineStatus: true,
              allowTradeRequests: true,
              shareUsageData: false,
              darkMode: false,
              colorTheme: 'blue',
              language: 'English',
              autoSave: true,
              offlineMode: false,
              syncOnWifi: true,
              showTutorials: true,
              cacheSize: '100MB',
              apiTimeout: 30,
              debugMode: false,
            };
            saveSettings(defaultSettings);
            Alert.alert('Success', 'Settings reset to defaults');
          },
        },
      ]
    );
  };

  const renderSettingItem = (title, description, value, onToggle, icon) => (
    <View style={styles.settingItem}>
      <View style={styles.settingLeft}>
        <View style={styles.settingIcon}>
          <Icon name={icon} size={20} color="#64748B" />
        </View>
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          {description && <Text style={styles.settingDescription}>{description}</Text>}
        </View>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{false: '#E2E8F0', true: '#3B82F6'}}
        thumbColor={value ? 'white' : '#94A3B8'}
      />
    </View>
  );

  const renderActionItem = (title, description, onPress, icon, destructive = false) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress}>
      <View style={styles.settingLeft}>
        <View style={styles.settingIcon}>
          <Icon name={icon} size={20} color={destructive ? '#EF4444' : '#64748B'} />
        </View>
        <View style={styles.settingText}>
          <Text style={[styles.settingTitle, destructive && {color: '#EF4444'}]}>
            {title}
          </Text>
          {description && <Text style={styles.settingDescription}>{description}</Text>}
        </View>
      </View>
      <Icon name="chevron-right" size={20} color="#94A3B8" />
    </TouchableOpacity>
  );

  const renderThemeItem = ({item}) => (
    <TouchableOpacity
      style={[
        styles.themeItem,
        settings.colorTheme === item.id && styles.selectedThemeItem
      ]}
      onPress={() => {
        updateSetting('colorTheme', item.id);
        setShowThemeSelector(false);
      }}>
      <View style={[styles.themeColor, {backgroundColor: item.color}]} />
      <Text style={styles.themeName}>{item.name}</Text>
      {settings.colorTheme === item.id && (
        <Icon name="check" size={20} color="#3B82F6" />
      )}
    </TouchableOpacity>
  );

  const renderLanguageItem = ({item}) => (
    <TouchableOpacity
      style={[
        styles.languageItem,
        settings.language === item.name && styles.selectedLanguageItem
      ]}
      onPress={() => {
        updateSetting('language', item.name);
        setShowLanguageSelector(false);
        Alert.alert('Language Changed', 'App will restart to apply language changes');
      }}>
      <Text style={styles.languageFlag}>{item.flag}</Text>
      <Text style={styles.languageName}>{item.name}</Text>
      {settings.language === item.name && (
        <Icon name="check" size={20} color="#3B82F6" />
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-back" size={24} color="#1E293B" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{width: 24}} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          {renderSettingItem(
            'Push Notifications',
            'Receive push notifications',
            settings.pushNotifications,
            (value) => updateSetting('pushNotifications', value),
            'notifications'
          )}
          {renderSettingItem(
            'Battle Notifications',
            'Notify when battles start or end',
            settings.battleNotifications,
            (value) => updateSetting('battleNotifications', value),
            'flash-on'
          )}
          {renderSettingItem(
            'Trade Notifications',
            'Notify about trade requests and updates',
            settings.tradeNotifications,
            (value) => updateSetting('tradeNotifications', value),
            'swap-horiz'
          )}
          {renderSettingItem(
            'System Notifications',
            'App updates and maintenance alerts',
            settings.systemNotifications,
            (value) => updateSetting('systemNotifications', value),
            'system-update'
          )}
        </View>

        {/* Privacy Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Privacy</Text>
          {renderSettingItem(
            'Public Profile',
            'Make your profile visible to other trainers',
            settings.publicProfile,
            (value) => updateSetting('publicProfile', value),
            'public'
          )}
          {renderSettingItem(
            'Show Online Status',
            'Let others see when you\'re online',
            settings.showOnlineStatus,
            (value) => updateSetting('showOnlineStatus', value),
            'visibility'
          )}
          {renderSettingItem(
            'Allow Trade Requests',
            'Receive trade requests from other trainers',
            settings.allowTradeRequests,
            (value) => updateSetting('allowTradeRequests', value),
            'handshake'
          )}
          {renderSettingItem(
            'Share Usage Data',
            'Help improve the app by sharing anonymous usage data',
            settings.shareUsageData,
            (value) => updateSetting('shareUsageData', value),
            'analytics'
          )}
        </View>

        {/* Appearance Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Appearance</Text>
          {renderSettingItem(
            'Dark Mode',
            'Use dark theme throughout the app',
            settings.darkMode,
            (value) => updateSetting('darkMode', value),
            'dark-mode'
          )}
          
          {renderActionItem(
            'Color Theme',
            `Current: ${themes.find(t => t.id === settings.colorTheme)?.name}`,
            () => setShowThemeSelector(true),
            'palette'
          )}
          
          {renderActionItem(
            'Language',
            `Current: ${settings.language}`,
            () => setShowLanguageSelector(true),
            'language'
          )}
        </View>

        {/* Gameplay Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Gameplay</Text>
          {renderSettingItem(
            'Auto Save',
            'Automatically save your progress',
            settings.autoSave,
            (value) => updateSetting('autoSave', value),
            'save'
          )}
          {renderSettingItem(
            'Sync on WiFi Only',
            'Only sync data when connected to WiFi',
            settings.syncOnWifi,
            (value) => updateSetting('syncOnWifi', value),
            'wifi'
          )}
          {renderSettingItem(
            'Show Tutorials',
            'Display helpful tips and tutorials',
            settings.showTutorials,
            (value) => updateSetting('showTutorials', value),
            'school'
          )}
        </View>

        {/* Storage & Data Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Storage & Data</Text>
          
          {renderActionItem(
            'Clear Cache',
            `Cache size: ${settings.cacheSize}`,
            clearCache,
            'cleaning-services'
          )}
          
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <View style={styles.settingIcon}>
                <Icon name="storage" size={20} color="#64748B" />
              </View>
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Data Usage</Text>
                <Text style={styles.settingDescription}>
                  {offlineMode ? 'Offline mode active' : 'Using mobile data'}
                </Text>
              </View>
            </View>
            <Text style={styles.dataUsage}>~{Math.floor(Math.random() * 50) + 10}MB</Text>
          </View>
        </View>

        {/* Advanced Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Advanced</Text>
          {renderSettingItem(
            'Debug Mode',
            'Show debug information (for developers)',
            settings.debugMode,
            (value) => updateSetting('debugMode', value),
            'bug-report'
          )}
          
          {renderActionItem(
            'Reset Settings',
            'Restore all settings to defaults',
            resetSettings,
            'restore',
            true
          )}
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          
          {renderActionItem(
            'Privacy Policy',
            'Read our privacy policy',
            () => Alert.alert('Coming Soon', 'Privacy policy coming soon!'),
            'privacy-tip'
          )}
          
          {renderActionItem(
            'Terms of Service',
            'Read our terms of service',
            () => Alert.alert('Coming Soon', 'Terms of service coming soon!'),
            'description'
          )}
          
          {renderActionItem(
            'Help & Support',
            'Get help or contact support',
            () => Alert.alert('Coming Soon', 'Help center coming soon!'),
            'help'
          )}
          
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <View style={styles.settingIcon}>
                <Icon name="info" size={20} color="#64748B" />
              </View>
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>App Version</Text>
                <Text style={styles.settingDescription}>Pokemon Team Builder v1.0.0</Text>
              </View>
            </View>
          </View>
        </View>

        <View style={styles.bottomSpacing} />
      </ScrollView>

      {/* Theme Selector Modal */}
      <Modal
        visible={showThemeSelector}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowThemeSelector(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowThemeSelector(false)}>
              <Text style={styles.modalCancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Choose Theme</Text>
            <View style={{width: 60}} />
          </View>
          <FlatList
            data={themes}
            renderItem={renderThemeItem}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.modalList}
          />
        </View>
      </Modal>

      {/* Language Selector Modal */}
      <Modal
        visible={showLanguageSelector}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowLanguageSelector(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowLanguageSelector(false)}>
              <Text style={styles.modalCancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Choose Language</Text>
            <View style={{width: 60}} />
          </View>
          <FlatList
            data={languages}
            renderItem={renderLanguageItem}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.modalList}
          />
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  section: {
    backgroundColor: 'white',
    marginTop: 16,
    marginHorizontal: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F1F5F9',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingText: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1E293B',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 16,
  },
  dataUsage: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '500',
  },
  bottomSpacing: {
    height: 40,
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
  modalCancel: {
    fontSize: 16,
    color: '#64748B',
  },
  modalList: {
    padding: 16,
  },
  themeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 8,
    backgroundColor: '#F8FAFC',
  },
  selectedThemeItem: {
    backgroundColor: '#EBF8FF',
    borderWidth: 1,
    borderColor: '#3B82F6',
  },
  themeColor: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 16,
    borderWidth: 2,
    borderColor: '#E2E8F0',
  },
  themeName: {
    fontSize: 16,
    color: '#1E293B',
    flex: 1,
  },
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 8,
    backgroundColor: '#F8FAFC',
  },
  selectedLanguageItem: {
    backgroundColor: '#EBF8FF',
    borderWidth: 1,
    borderColor: '#3B82F6',
  },
  languageFlag: {
    fontSize: 24,
    marginRight: 16,
  },
  languageName: {
    fontSize: 16,
    color: '#1E293B',
    flex: 1,
  },
});

export default SettingsScreen;