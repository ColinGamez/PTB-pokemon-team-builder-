/**
 * Trading Screen for Pokemon Team Builder Mobile App
 * Pokemon trading system interface
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Modal,
  FlatList,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import {useApp} from '../context/AppContext';
import {ApiService} from '../services/ApiService';

const TradingScreen = ({navigation}) => {
  const {user, teams, offlineMode} = useApp();
  const [activeTrades, setActiveTrades] = useState([]);
  const [tradeOffers, setTradeOffers] = useState([]);
  const [tradingHub, setTradingHub] = useState([]);
  const [selectedConsole, setSelectedConsole] = useState('Switch');
  const [showCreateTrade, setShowCreateTrade] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const consoles = [
    {id: 'Switch', name: 'Nintendo Switch', icon: 'videogame-asset', color: '#E60012'},
    {id: 'DS', name: 'Nintendo DS/3DS', icon: 'games', color: '#0066CC'},
    {id: 'GameCube', name: 'GameCube/Wii', icon: 'sports-esports', color: '#4B0082'},
    {id: 'Mobile', name: 'Pokemon GO', icon: 'smartphone', color: '#FF6B35'},
  ];

  const tradeTypes = [
    {id: 'pokemon', name: 'Pokemon Trade', icon: 'catching-pokemon'},
    {id: 'items', name: 'Item Trade', icon: 'inventory'},
    {id: 'breeding', name: 'Breeding Services', icon: 'child-care'},
    {id: 'services', name: 'Training Services', icon: 'school'},
  ];

  useEffect(() => {
    loadTradingData();
  }, [selectedConsole]);

  const loadTradingData = async () => {
    if (offlineMode) {
      // Show offline message and sample data
      setActiveTrades([]);
      setTradeOffers([]);
      setTradingHub(generateSampleTrades());
      return;
    }

    try {
      setLoading(true);
      const [trades, offers, hub] = await Promise.all([
        ApiService.getActiveTrades(),
        ApiService.getTradeOffers(),
        ApiService.getTradingHub(selectedConsole),
      ]);
      
      setActiveTrades(trades);
      setTradeOffers(offers);
      setTradingHub(hub);
    } catch (error) {
      console.error('Failed to load trading data:', error);
      Alert.alert('Error', 'Failed to load trading data');
    } finally {
      setLoading(false);
    }
  };

  const generateSampleTrades = () => [
    {
      id: '1',
      user: 'TrainerAce',
      type: 'pokemon',
      console: 'Switch',
      offering: 'Shiny Charizard',
      seeking: 'Shiny Blastoise',
      details: 'Perfect IVs, Competitive ready',
      status: 'active',
      created: Date.now() - 3600000,
    },
    {
      id: '2',
      user: 'PokeMaster',
      type: 'breeding',
      console: 'Switch',
      offering: 'Breeding Services',
      seeking: 'Rare Pokemon',
      details: '6IV Ditto available for breeding',
      status: 'active',
      created: Date.now() - 7200000,
    },
    {
      id: '3',
      user: 'ShinyHunter',
      type: 'items',
      console: 'DS',
      offering: 'Master Balls x5',
      seeking: 'Shiny Pokemon',
      details: 'Any shiny Pokemon accepted',
      status: 'active',
      created: Date.now() - 10800000,
    },
  ];

  const createTrade = async (tradeData) => {
    if (offlineMode) {
      Alert.alert('Offline Mode', 'Trading requires an internet connection');
      return;
    }

    try {
      setLoading(true);
      const newTrade = await ApiService.createTrade(tradeData);
      setActiveTrades([newTrade, ...activeTrades]);
      setShowCreateTrade(false);
      Alert.alert('Success', 'Trade posted successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to create trade: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const respondToTrade = async (tradeId, action) => {
    if (offlineMode) {
      Alert.alert('Offline Mode', 'Trading requires an internet connection');
      return;
    }

    try {
      await ApiService.respondToTrade(tradeId, action);
      loadTradingData();
      Alert.alert('Success', `Trade ${action} successfully!`);
    } catch (error) {
      Alert.alert('Error', `Failed to ${action} trade: ` + error.message);
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      pokemon: '#3B82F6',
      items: '#10B981',
      breeding: '#F59E0B',
      services: '#8B5CF6',
    };
    return colors[type] || '#64748B';
  };

  const getConsoleIcon = (console) => {
    const consoleData = consoles.find(c => c.id === console);
    return consoleData ? consoleData.icon : 'device-unknown';
  };

  const getConsoleColor = (console) => {
    const consoleData = consoles.find(c => c.id === console);
    return consoleData ? consoleData.color : '#64748B';
  };

  const renderConsoleSelector = () => (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.consoleSelectorContainer}>
      {consoles.map((console) => (
        <TouchableOpacity
          key={console.id}
          style={[
            styles.consoleChip,
            selectedConsole === console.id && styles.selectedConsoleChip,
            {borderColor: console.color},
          ]}
          onPress={() => setSelectedConsole(console.id)}>
          <Icon
            name={console.icon}
            size={20}
            color={selectedConsole === console.id ? 'white' : console.color}
          />
          <Text
            style={[
              styles.consoleChipText,
              selectedConsole === console.id && styles.selectedConsoleChipText,
              {color: selectedConsole === console.id ? 'white' : console.color},
            ]}>
            {console.name}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  const renderTradeItem = ({item}) => (
    <View style={styles.tradeCard}>
      <View style={styles.tradeHeader}>
        <View style={styles.tradeUser}>
          <Icon name="person" size={20} color="#64748B" />
          <Text style={styles.tradeUsername}>{item.user}</Text>
        </View>
        <View style={styles.tradeConsole}>
          <Icon
            name={getConsoleIcon(item.console)}
            size={16}
            color={getConsoleColor(item.console)}
          />
          <Text style={[styles.consoleText, {color: getConsoleColor(item.console)}]}>
            {item.console}
          </Text>
        </View>
      </View>

      <View style={styles.tradeType}>
        <View style={[styles.typeTag, {backgroundColor: getTypeColor(item.type)}]}>
          <Icon name={tradeTypes.find(t => t.id === item.type)?.icon} size={16} color="white" />
          <Text style={styles.typeText}>
            {tradeTypes.find(t => t.id === item.type)?.name}
          </Text>
        </View>
      </View>

      <View style={styles.tradeContent}>
        <View style={styles.tradeOffering}>
          <Text style={styles.tradeLabel}>Offering:</Text>
          <Text style={styles.tradeValue}>{item.offering}</Text>
        </View>
        <Icon name="swap-horiz" size={24} color="#64748B" style={styles.swapIcon} />
        <View style={styles.tradeSeeking}>
          <Text style={styles.tradeLabel}>Seeking:</Text>
          <Text style={styles.tradeValue}>{item.seeking}</Text>
        </View>
      </View>

      {item.details && (
        <Text style={styles.tradeDetails}>{item.details}</Text>
      )}

      <View style={styles.tradeFooter}>
        <Text style={styles.tradeTime}>
          {new Date(item.created).toLocaleDateString()}
        </Text>
        <View style={styles.tradeActions}>
          <TouchableOpacity
            style={styles.tradeActionButton}
            onPress={() => {
              if (item.user === user?.username) {
                Alert.alert('Your Trade', 'This is your trade posting');
              } else {
                Alert.alert(
                  'Contact Trader',
                  `Would you like to message ${item.user} about this trade?`,
                  [
                    {text: 'Cancel', style: 'cancel'},
                    {text: 'Message', onPress: () => Alert.alert('Coming Soon', 'Messaging feature coming soon!')},
                  ]
                );
              }
            }}>
            <Icon name="message" size={16} color="#3B82F6" />
            <Text style={styles.tradeActionText}>Message</Text>
          </TouchableOpacity>
          
          {item.user !== user?.username && (
            <TouchableOpacity
              style={styles.tradeActionButton}
              onPress={() => respondToTrade(item.id, 'offer')}>
              <Icon name="handshake" size={16} color="#10B981" />
              <Text style={styles.tradeActionText}>Offer</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );

  const renderActiveTradeItem = ({item}) => (
    <View style={[styles.tradeCard, styles.activeTradeCard]}>
      <View style={styles.tradeHeader}>
        <Text style={styles.activeTradeTitle}>Your Trade</Text>
        <View style={[styles.statusBadge, styles.activeStatus]}>
          <Text style={styles.statusText}>Active</Text>
        </View>
      </View>

      <View style={styles.tradeContent}>
        <View style={styles.tradeOffering}>
          <Text style={styles.tradeLabel}>You're offering:</Text>
          <Text style={styles.tradeValue}>{item.offering}</Text>
        </View>
        <Icon name="swap-horiz" size={24} color="#64748B" style={styles.swapIcon} />
        <View style={styles.tradeSeeking}>
          <Text style={styles.tradeLabel}>You want:</Text>
          <Text style={styles.tradeValue}>{item.seeking}</Text>
        </View>
      </View>

      <View style={styles.tradeFooter}>
        <Text style={styles.tradeOffers}>{item.offers || 0} offers received</Text>
        <View style={styles.tradeActions}>
          <TouchableOpacity
            style={styles.tradeActionButton}
            onPress={() => Alert.alert('Coming Soon', 'Trade management coming soon!')}>
            <Icon name="edit" size={16} color="#F59E0B" />
            <Text style={styles.tradeActionText}>Edit</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.tradeActionButton}
            onPress={() => Alert.alert('Coming Soon', 'Trade cancellation coming soon!')}>
            <Icon name="close" size={16} color="#EF4444" />
            <Text style={styles.tradeActionText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );

  const CreateTradeModal = () => (
    <Modal
      visible={showCreateTrade}
      animationType="slide"
      onRequestClose={() => setShowCreateTrade(false)}>
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={() => setShowCreateTrade(false)}>
            <Icon name="close" size={24} color="#1E293B" />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Create Trade</Text>
          <TouchableOpacity>
            <Text style={styles.modalDone}>Post</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <Text style={styles.comingSoonModalText}>
            Trade creation interface coming soon!
          </Text>
          <Text style={styles.comingSoonModalSubtext}>
            Features in development:{'\n'}
            • Pokemon selection from your collection{'\n'}
            • Item trading interface{'\n'}
            • Trade terms and conditions{'\n'}
            • Direct messaging system{'\n'}
            • Trade verification and security
          </Text>
        </ScrollView>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={['#F59E0B', '#D97706']}
        style={styles.header}>
        <Text style={styles.headerTitle}>Trading Hub</Text>
        <Text style={styles.headerSubtitle}>Trade Pokemon with trainers worldwide</Text>
      </LinearGradient>

      {offlineMode && (
        <View style={styles.offlineAlert}>
          <Icon name="cloud-off" size={20} color="#F59E0B" />
          <Text style={styles.offlineText}>
            Trading requires internet connection. Showing sample data.
          </Text>
        </View>
      )}

      <ScrollView style={styles.content}>
        {/* Console Selector */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Platform</Text>
          {renderConsoleSelector()}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActions}>
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => {
                if (offlineMode) {
                  Alert.alert('Offline Mode', 'Trading requires an internet connection');
                } else {
                  setShowCreateTrade(true);
                }
              }}>
              <Icon name="add-circle" size={24} color="#3B82F6" />
              <Text style={styles.quickActionText}>Create Trade</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => Alert.alert('Coming Soon', 'Trade history coming soon!')}>
              <Icon name="history" size={24} color="#10B981" />
              <Text style={styles.quickActionText}>Trade History</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => Alert.alert('Coming Soon', 'Favorites feature coming soon!')}>
              <Icon name="favorite" size={24} color="#EF4444" />
              <Text style={styles.quickActionText}>Favorites</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Active Trades */}
        {activeTrades.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Your Active Trades</Text>
            <FlatList
              data={activeTrades}
              renderItem={renderActiveTradeItem}
              keyExtractor={item => item.id}
              scrollEnabled={false}
            />
          </View>
        )}

        {/* Search */}
        <View style={styles.section}>
          <View style={styles.searchContainer}>
            <Icon name="search" size={20} color="#64748B" />
            <TextInput
              style={styles.searchInput}
              placeholder="Search trades..."
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>
        </View>

        {/* Trading Hub */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Trading Hub</Text>
            <TouchableOpacity onPress={loadTradingData}>
              <Icon name="refresh" size={20} color="#64748B" />
            </TouchableOpacity>
          </View>

          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#F59E0B" />
              <Text style={styles.loadingText}>Loading trades...</Text>
            </View>
          ) : (
            <FlatList
              data={tradingHub.filter(trade =>
                !searchQuery ||
                trade.offering.toLowerCase().includes(searchQuery.toLowerCase()) ||
                trade.seeking.toLowerCase().includes(searchQuery.toLowerCase()) ||
                trade.user.toLowerCase().includes(searchQuery.toLowerCase())
              )}
              renderItem={renderTradeItem}
              keyExtractor={item => item.id}
              scrollEnabled={false}
              ListEmptyComponent={
                <View style={styles.emptyState}>
                  <Icon name="swap-horiz" size={64} color="#D1D5DB" />
                  <Text style={styles.emptyStateTitle}>No Trades Found</Text>
                  <Text style={styles.emptyStateText}>
                    {searchQuery
                      ? 'No trades match your search criteria'
                      : 'No active trades for this platform'}
                  </Text>
                </View>
              }
            />
          )}
        </View>

        {/* Trading Tips */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Trading Tips</Text>
          <View style={styles.tipsList}>
            <View style={styles.tipItem}>
              <Icon name="security" size={16} color="#10B981" />
              <Text style={styles.tipText}>Always verify Pokemon legitimacy before trading</Text>
            </View>
            <View style={styles.tipItem}>
              <Icon name="message" size={16} color="#3B82F6" />
              <Text style={styles.tipText}>Communicate clearly about trade terms</Text>
            </View>
            <View style={styles.tipItem}>
              <Icon name="warning" size={16} color="#F59E0B" />
              <Text style={styles.tipText}>Be cautious of trades that seem too good to be true</Text>
            </View>
            <View style={styles.tipItem}>
              <Icon name="star" size={16} color="#8B5CF6" />
              <Text style={styles.tipText}>Build your reputation through successful trades</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      <CreateTradeModal />
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
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  offlineAlert: {
    backgroundColor: '#FEF3C7',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    marginTop: 8,
    borderRadius: 8,
  },
  offlineText: {
    color: '#92400E',
    fontSize: 12,
    marginLeft: 8,
    flex: 1,
  },
  content: {
    flex: 1,
  },
  section: {
    backgroundColor: 'white',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
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
    marginBottom: 16,
  },
  consoleSelectorContainer: {
    paddingHorizontal: 4,
  },
  consoleChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 2,
    marginRight: 12,
    backgroundColor: 'white',
  },
  selectedConsoleChip: {
    backgroundColor: '#F59E0B',
  },
  consoleChipText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 8,
  },
  selectedConsoleChipText: {
    color: 'white',
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  quickActionButton: {
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flex: 1,
    marginHorizontal: 4,
  },
  quickActionText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1E293B',
    marginTop: 8,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#1E293B',
    marginLeft: 8,
  },
  tradeCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  activeTradeCard: {
    backgroundColor: '#EBF8FF',
    borderColor: '#3B82F6',
  },
  tradeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  tradeUser: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  tradeUsername: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginLeft: 8,
  },
  tradeConsole: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  consoleText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  activeTradeTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  activeStatus: {
    backgroundColor: '#10B981',
  },
  statusText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  tradeType: {
    marginBottom: 12,
  },
  typeTag: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'flex-start',
  },
  typeText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
    marginLeft: 6,
  },
  tradeContent: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  tradeOffering: {
    flex: 1,
  },
  tradeSeeking: {
    flex: 1,
    alignItems: 'flex-end',
  },
  tradeLabel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 4,
  },
  tradeValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
  },
  swapIcon: {
    marginHorizontal: 16,
  },
  tradeDetails: {
    fontSize: 12,
    color: '#64748B',
    fontStyle: 'italic',
    marginBottom: 12,
  },
  tradeFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
  },
  tradeTime: {
    fontSize: 12,
    color: '#94A3B8',
  },
  tradeOffers: {
    fontSize: 12,
    color: '#3B82F6',
    fontWeight: '500',
  },
  tradeActions: {
    flexDirection: 'row',
  },
  tradeActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginLeft: 8,
  },
  tradeActionText: {
    fontSize: 12,
    color: '#64748B',
    marginLeft: 4,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  loadingText: {
    fontSize: 14,
    color: '#64748B',
    marginTop: 12,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
  },
  tipsList: {
    gap: 12,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  tipText: {
    fontSize: 14,
    color: '#64748B',
    flex: 1,
    lineHeight: 20,
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
  modalDone: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  comingSoonModalText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    textAlign: 'center',
    marginBottom: 16,
  },
  comingSoonModalSubtext: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default TradingScreen;