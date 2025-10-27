/**
 * Battle Screen for Pokemon Team Builder Mobile App
 * Battle simulation and management interface
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
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import {useApp} from '../context/AppContext';
import {ApiService} from '../services/ApiService';

const BattleScreen = ({navigation}) => {
  const {user, teams, offlineMode} = useApp();
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [currentBattle, setCurrentBattle] = useState(null);
  const [battleHistory, setBattleHistory] = useState([]);
  const [showTeamSelector, setShowTeamSelector] = useState(false);
  const [loading, setLoading] = useState(false);
  const [battleMode, setBattleMode] = useState('quick'); // quick, ranked, tournament

  const battleModes = [
    {
      id: 'quick',
      name: 'Quick Battle',
      description: 'Fast battles against AI',
      icon: 'flash-on',
      color: '#10B981',
    },
    {
      id: 'ranked',
      name: 'Ranked Battle',
      description: 'Competitive matches',
      icon: 'emoji-events',
      color: '#F59E0B',
      disabled: offlineMode,
    },
    {
      id: 'tournament',
      name: 'Tournament',
      description: 'Join tournaments',
      icon: 'military-tech',
      color: '#8B5CF6',
      disabled: offlineMode,
    },
  ];

  useEffect(() => {
    loadBattleHistory();
  }, []);

  const loadBattleHistory = async () => {
    try {
      if (!offlineMode) {
        const history = await ApiService.getBattleHistory();
        setBattleHistory(history);
      } else {
        // Load from local storage or show empty state
        setBattleHistory([]);
      }
    } catch (error) {
      console.error('Failed to load battle history:', error);
    }
  };

  const startBattle = async () => {
    if (!selectedTeam) {
      Alert.alert('No Team Selected', 'Please select a team before starting a battle.');
      return;
    }

    if (selectedTeam.pokemon.length === 0) {
      Alert.alert('Empty Team', 'Your selected team has no Pokemon!');
      return;
    }

    setLoading(true);
    try {
      let battle;
      
      if (battleMode === 'quick' || offlineMode) {
        // Start AI battle (works offline)
        battle = await startAIBattle();
      } else if (battleMode === 'ranked') {
        // Start ranked battle (online only)
        battle = await ApiService.startRankedBattle(selectedTeam.id);
      } else if (battleMode === 'tournament') {
        // Join tournament (online only)
        battle = await ApiService.joinTournament(selectedTeam.id);
      }

      setCurrentBattle(battle);
      
      // Navigate to battle interface
      navigation.navigate('BattleInterface', {
        battle,
        team: selectedTeam,
        mode: battleMode,
      });
      
    } catch (error) {
      Alert.alert('Battle Error', error.message || 'Failed to start battle');
    } finally {
      setLoading(false);
    }
  };

  const startAIBattle = async () => {
    // Simulate AI battle creation (works offline)
    const aiTeam = generateAITeam();
    
    const battle = {
      id: `battle_${Date.now()}`,
      mode: 'quick',
      playerTeam: selectedTeam,
      opponentTeam: aiTeam,
      status: 'active',
      turn: 1,
      playerActive: selectedTeam.pokemon[0],
      opponentActive: aiTeam.pokemon[0],
      battleLog: [`Battle started against AI Trainer!`],
      created: new Date().toISOString(),
    };

    return battle;
  };

  const generateAITeam = () => {
    // Generate a random AI team based on selected team's format
    const aiPokemon = [
      {
        name: 'Pikachu',
        level: 50,
        types: ['Electric'],
        stats: {hp: 100, attack: 95, defense: 80, spattack: 100, spdefense: 80, speed: 110},
        currentHP: 100,
        moves: ['Thunderbolt', 'Quick Attack', 'Thunder Wave', 'Agility'],
      },
      {
        name: 'Charizard',
        level: 50,
        types: ['Fire', 'Flying'],
        stats: {hp: 120, attack: 104, defense: 98, spattack: 129, spdefense: 105, speed: 120},
        currentHP: 120,
        moves: ['Flamethrower', 'Air Slash', 'Dragon Pulse', 'Roost'],
      },
      {
        name: 'Blastoise',
        level: 50,
        types: ['Water'],
        stats: {hp: 125, attack: 103, defense: 120, spattack: 105, spdefense: 125, speed: 98},
        currentHP: 125,
        moves: ['Surf', 'Ice Beam', 'Rapid Spin', 'Rest'],
      },
    ];

    return {
      id: 'ai_team',
      name: 'AI Trainer Team',
      format: selectedTeam.format,
      pokemon: aiPokemon.slice(0, Math.min(selectedTeam.pokemon.length, 3)),
      isAI: true,
    };
  };

  const getTypeColor = (type) => {
    const colors = {
      normal: '#A8A878', fire: '#F08030', water: '#6890F0', electric: '#F8D030',
      grass: '#78C850', ice: '#98D8D8', fighting: '#C03028', poison: '#A040A0',
      ground: '#E0C068', flying: '#A890F0', psychic: '#F85888', bug: '#A8B820',
      rock: '#B8A038', ghost: '#705898', dragon: '#7038F8', dark: '#705848',
      steel: '#B8B8D0', fairy: '#EE99AC',
    };
    return colors[type.toLowerCase()] || '#68A090';
  };

  const renderTeamItem = ({item}) => (
    <TouchableOpacity
      style={[
        styles.teamItem,
        selectedTeam?.id === item.id && styles.selectedTeamItem
      ]}
      onPress={() => setSelectedTeam(item)}>
      <View style={styles.teamItemHeader}>
        <Text style={styles.teamItemName}>{item.name}</Text>
        <Text style={styles.teamItemFormat}>{item.format}</Text>
      </View>
      <Text style={styles.teamItemCount}>
        {item.pokemon?.length || 0}/6 Pokemon
      </Text>
      <View style={styles.teamItemPokemon}>
        {item.pokemon?.slice(0, 6).map((pokemon, index) => (
          <View key={index} style={styles.pokemonPreview}>
            <Text style={styles.pokemonPreviewName}>{pokemon.name}</Text>
            <View style={styles.pokemonPreviewTypes}>
              {pokemon.types?.slice(0, 2).map((type, typeIndex) => (
                <View
                  key={typeIndex}
                  style={[
                    styles.typeIndicator,
                    {backgroundColor: getTypeColor(type)}
                  ]}
                />
              ))}
            </View>
          </View>
        ))}
      </View>
    </TouchableOpacity>
  );

  const renderBattleHistory = ({item}) => (
    <TouchableOpacity style={styles.historyItem}>
      <View style={styles.historyHeader}>
        <View style={[
          styles.resultBadge,
          {backgroundColor: item.result === 'win' ? '#10B981' : item.result === 'loss' ? '#EF4444' : '#F59E0B'}
        ]}>
          <Text style={styles.resultText}>
            {item.result?.toUpperCase() || 'DRAW'}
          </Text>
        </View>
        <Text style={styles.historyDate}>
          {new Date(item.date).toLocaleDateString()}
        </Text>
      </View>
      <Text style={styles.historyMode}>{item.mode} Battle</Text>
      <Text style={styles.historyOpponent}>vs {item.opponent}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={['#EF4444', '#DC2626']}
        style={styles.header}>
        <Text style={styles.headerTitle}>Battle Arena</Text>
        <Text style={styles.headerSubtitle}>Choose your team and battle!</Text>
      </LinearGradient>

      <ScrollView style={styles.content}>
        {/* Battle Modes */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Battle Modes</Text>
          <View style={styles.battleModes}>
            {battleModes.map((mode) => (
              <TouchableOpacity
                key={mode.id}
                style={[
                  styles.battleModeCard,
                  battleMode === mode.id && styles.selectedBattleMode,
                  mode.disabled && styles.disabledBattleMode,
                ]}
                onPress={() => !mode.disabled && setBattleMode(mode.id)}
                disabled={mode.disabled}>
                <View style={[styles.battleModeIcon, {backgroundColor: mode.color}]}>
                  <Icon name={mode.icon} size={24} color="white" />
                </View>
                <View style={styles.battleModeInfo}>
                  <Text style={[
                    styles.battleModeName,
                    mode.disabled && styles.disabledText
                  ]}>
                    {mode.name}
                  </Text>
                  <Text style={[
                    styles.battleModeDescription,
                    mode.disabled && styles.disabledText
                  ]}>
                    {mode.description}
                    {mode.disabled && ' (Online Only)'}
                  </Text>
                </View>
                {mode.disabled && (
                  <Icon name="lock" size={20} color="#94A3B8" />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Team Selection */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Select Team</Text>
            <TouchableOpacity
              style={styles.changeTeamButton}
              onPress={() => setShowTeamSelector(true)}>
              <Text style={styles.changeTeamText}>Change Team</Text>
            </TouchableOpacity>
          </View>

          {selectedTeam ? (
            <View style={styles.selectedTeamCard}>
              <View style={styles.selectedTeamHeader}>
                <Text style={styles.selectedTeamName}>{selectedTeam.name}</Text>
                <View style={[
                  styles.formatBadge,
                  {backgroundColor: getBattleModeColor(selectedTeam.format)}
                ]}>
                  <Text style={styles.formatText}>{selectedTeam.format}</Text>
                </View>
              </View>
              <Text style={styles.selectedTeamCount}>
                {selectedTeam.pokemon?.length || 0}/6 Pokemon Ready
              </Text>
              <View style={styles.selectedTeamPokemon}>
                {selectedTeam.pokemon?.map((pokemon, index) => (
                  <View key={index} style={styles.pokemonCard}>
                    <Text style={styles.pokemonCardName}>{pokemon.name}</Text>
                    <Text style={styles.pokemonCardLevel}>Lv.{pokemon.level}</Text>
                    <View style={styles.pokemonCardTypes}>
                      {pokemon.types?.map((type, typeIndex) => (
                        <View
                          key={typeIndex}
                          style={[
                            styles.typeTag,
                            {backgroundColor: getTypeColor(type)}
                          ]}>
                          <Text style={styles.typeTagText}>{type}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                ))}
              </View>
            </View>
          ) : (
            <TouchableOpacity
              style={styles.noTeamCard}
              onPress={() => setShowTeamSelector(true)}>
              <Icon name="add-circle-outline" size={48} color="#94A3B8" />
              <Text style={styles.noTeamText}>Select a team to battle</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Battle Button */}
        <View style={styles.section}>
          <TouchableOpacity
            style={[
              styles.battleButton,
              (!selectedTeam || loading) && styles.battleButtonDisabled
            ]}
            onPress={startBattle}
            disabled={!selectedTeam || loading}>
            {loading ? (
              <ActivityIndicator color="white" size="small" />
            ) : (
              <>
                <Icon name="flash-on" size={24} color="white" />
                <Text style={styles.battleButtonText}>Start Battle</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* Battle History */}
        {battleHistory.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Battles</Text>
            <FlatList
              data={battleHistory.slice(0, 5)}
              renderItem={renderBattleHistory}
              keyExtractor={item => item.id}
              scrollEnabled={false}
            />
          </View>
        )}
      </ScrollView>

      {/* Team Selector Modal */}
      <Modal
        visible={showTeamSelector}
        animationType="slide"
        onRequestClose={() => setShowTeamSelector(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowTeamSelector(false)}>
              <Icon name="close" size={24} color="#1E293B" />
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Select Team</Text>
            <TouchableOpacity onPress={() => {
              setShowTeamSelector(false);
              navigation.navigate('TeamBuilder');
            }}>
              <Text style={styles.createTeamText}>New Team</Text>
            </TouchableOpacity>
          </View>

          <FlatList
            data={teams}
            renderItem={renderTeamItem}
            keyExtractor={item => item.id?.toString() || item.name}
            contentContainerStyle={styles.teamsList}
            ListEmptyComponent={
              <View style={styles.emptyTeams}>
                <Icon name="group-add" size={64} color="#D1D5DB" />
                <Text style={styles.emptyTeamsTitle}>No Teams Found</Text>
                <Text style={styles.emptyTeamsText}>
                  Create your first team to start battling!
                </Text>
                <TouchableOpacity
                  style={styles.createFirstTeamButton}
                  onPress={() => {
                    setShowTeamSelector(false);
                    navigation.navigate('TeamBuilder');
                  }}>
                  <Text style={styles.createFirstTeamText}>Create Team</Text>
                </TouchableOpacity>
              </View>
            }
          />
        </View>
      </Modal>
    </View>
  );
};

const getBattleModeColor = (format) => {
  const colors = {
    Singles: '#3B82F6',
    Doubles: '#10B981',
    VGC: '#F59E0B',
    OU: '#8B5CF6',
    UU: '#EF4444',
    RU: '#EC4899',
    NU: '#6366F1',
  };
  return colors[format] || '#64748B';
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
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 12,
  },
  battleModes: {
    gap: 12,
  },
  battleModeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E2E8F0',
    backgroundColor: '#F8FAFC',
  },
  selectedBattleMode: {
    borderColor: '#3B82F6',
    backgroundColor: '#EBF8FF',
  },
  disabledBattleMode: {
    opacity: 0.5,
  },
  battleModeIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  battleModeInfo: {
    flex: 1,
  },
  battleModeName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 4,
  },
  battleModeDescription: {
    fontSize: 14,
    color: '#64748B',
  },
  disabledText: {
    color: '#94A3B8',
  },
  changeTeamButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: '#3B82F6',
  },
  changeTeamText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  selectedTeamCard: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  selectedTeamHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  selectedTeamName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  formatBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  formatText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  selectedTeamCount: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 12,
  },
  selectedTeamPokemon: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  pokemonCard: {
    flex: 1,
    minWidth: 100,
    backgroundColor: 'white',
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  pokemonCardName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 2,
  },
  pokemonCardLevel: {
    fontSize: 10,
    color: '#64748B',
    marginBottom: 4,
  },
  pokemonCardTypes: {
    flexDirection: 'row',
    gap: 2,
  },
  typeTag: {
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
  },
  typeTagText: {
    fontSize: 8,
    color: 'white',
    fontWeight: '500',
  },
  noTeamCard: {
    padding: 32,
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E2E8F0',
    borderStyle: 'dashed',
    backgroundColor: '#F8FAFC',
  },
  noTeamText: {
    fontSize: 16,
    color: '#94A3B8',
    marginTop: 12,
  },
  battleButton: {
    backgroundColor: '#EF4444',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
  },
  battleButtonDisabled: {
    backgroundColor: '#94A3B8',
  },
  battleButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  historyItem: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#F8FAFC',
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  resultBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  resultText: {
    fontSize: 10,
    color: 'white',
    fontWeight: 'bold',
  },
  historyDate: {
    fontSize: 12,
    color: '#64748B',
  },
  historyMode: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1E293B',
    marginBottom: 2,
  },
  historyOpponent: {
    fontSize: 12,
    color: '#64748B',
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
  createTeamText: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
  },
  teamsList: {
    padding: 16,
  },
  teamItem: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#F8FAFC',
    borderWidth: 2,
    borderColor: '#E2E8F0',
    marginBottom: 12,
  },
  selectedTeamItem: {
    borderColor: '#3B82F6',
    backgroundColor: '#EBF8FF',
  },
  teamItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  teamItemName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  teamItemFormat: {
    fontSize: 12,
    color: '#64748B',
    backgroundColor: '#E2E8F0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  teamItemCount: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 8,
  },
  teamItemPokemon: {
    flexDirection: 'row',
    gap: 8,
  },
  pokemonPreview: {
    alignItems: 'center',
    minWidth: 40,
  },
  pokemonPreviewName: {
    fontSize: 10,
    fontWeight: '500',
    color: '#1E293B',
    marginBottom: 2,
    textAlign: 'center',
  },
  pokemonPreviewTypes: {
    flexDirection: 'row',
    gap: 2,
  },
  typeIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  emptyTeams: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyTeamsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyTeamsText: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 24,
  },
  createFirstTeamButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  createFirstTeamText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default BattleScreen;