/**
 * Breeding Screen for Pokemon Team Builder Mobile App
 * Pokemon breeding calculator and management interface
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  TextInput,
  Alert,
  Modal,
  FlatList,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import {useApp} from '../context/AppContext';
import {ApiService} from '../services/ApiService';

const BreedingScreen = ({navigation}) => {
  const {pokemonData, offlineMode} = useApp();
  const [parent1, setParent1] = useState(null);
  const [parent2, setParent2] = useState(null);
  const [breedingResult, setBreedingResult] = useState(null);
  const [showPokemonPicker, setShowPokemonPicker] = useState(false);
  const [selectedParent, setSelectedParent] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredPokemon, setFilteredPokemon] = useState([]);
  const [breedingHistory, setBreedingHistory] = useState([]);

  const natures = [
    'Hardy', 'Lonely', 'Brave', 'Adamant', 'Naughty',
    'Bold', 'Docile', 'Relaxed', 'Impish', 'Lax',
    'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive',
    'Modest', 'Mild', 'Quiet', 'Bashful', 'Rash',
    'Calm', 'Gentle', 'Sassy', 'Careful', 'Quirky'
  ];

  useEffect(() => {
    if (pokemonData && searchQuery) {
      const filtered = pokemonData.filter(pokemon =>
        pokemon.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pokemon.species?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredPokemon(filtered.slice(0, 50));
    } else {
      setFilteredPokemon(pokemonData?.slice(0, 50) || []);
    }
  }, [searchQuery, pokemonData]);

  useEffect(() => {
    if (parent1 && parent2) {
      calculateBreeding();
    } else {
      setBreedingResult(null);
    }
  }, [parent1, parent2]);

  const calculateBreeding = () => {
    if (!parent1 || !parent2) return;

    // Check if Pokemon can breed
    const compatibility = checkBreedingCompatibility(parent1, parent2);
    
    if (!compatibility.canBreed) {
      setBreedingResult({
        canBreed: false,
        reason: compatibility.reason,
      });
      return;
    }

    // Calculate offspring possibilities
    const offspring = calculateOffspring(parent1, parent2);
    
    setBreedingResult({
      canBreed: true,
      offspring,
      compatibility: compatibility.level,
      eggCycles: compatibility.eggCycles,
      possibleAbilities: offspring.abilities,
      inheritedMoves: offspring.moves,
      ivRange: offspring.ivs,
    });
  };

  const checkBreeedingCompatibility = (p1, p2) => {
    // Simplified breeding compatibility check
    if (p1.name === p2.name) {
      return {
        canBreed: false,
        reason: 'Pokemon cannot breed with themselves'
      };
    }

    // Check egg groups (simplified)
    const eggGroups1 = p1.eggGroups || ['Unknown'];
    const eggGroups2 = p2.eggGroups || ['Unknown'];
    
    const hasCommonGroup = eggGroups1.some(group => eggGroups2.includes(group));
    
    if (eggGroups1.includes('Undiscovered') || eggGroups2.includes('Undiscovered')) {
      return {
        canBreed: false,
        reason: 'One or both Pokemon cannot breed'
      };
    }

    if (!hasCommonGroup && !eggGroups1.includes('Ditto') && !eggGroups2.includes('Ditto')) {
      return {
        canBreed: false,
        reason: 'Pokemon are not compatible for breeding'
      };
    }

    return {
      canBreed: true,
      level: hasCommonGroup ? 'High' : 'Medium',
      eggCycles: Math.floor(Math.random() * 30) + 20 // Random for demo
    };
  };

  const calculateOffspring = (p1, p2) => {
    // Determine offspring species (simplified)
    const femaleParent = Math.random() > 0.5 ? p1 : p2;
    const offspring = {
      species: femaleParent.name,
      types: femaleParent.types,
    };

    // Calculate possible abilities
    const allAbilities = [...(p1.abilities || []), ...(p2.abilities || [])];
    offspring.abilities = [...new Set(allAbilities)];

    // Calculate inherited moves
    const p1Moves = p1.learnableMoves || p1.moves || [];
    const p2Moves = p2.learnableMoves || p2.moves || [];
    const inheritedMoves = [...p1Moves, ...p2Moves].filter((move, index, arr) => 
      arr.indexOf(move) === index
    ).slice(0, 10); // Limit for display

    offspring.moves = inheritedMoves;

    // IV inheritance (simplified)
    offspring.ivs = {
      guaranteed: 3, // 3 perfect IVs guaranteed from parents
      range: {min: 0, max: 31}
    };

    return offspring;
  };

  const selectPokemon = (pokemon) => {
    const selectedPokemon = {
      ...pokemon,
      level: 50,
      nature: natures[Math.floor(Math.random() * natures.length)],
      ivs: {
        hp: Math.floor(Math.random() * 32),
        attack: Math.floor(Math.random() * 32),
        defense: Math.floor(Math.random() * 32),
        spattack: Math.floor(Math.random() * 32),
        spdefense: Math.floor(Math.random() * 32),
        speed: Math.floor(Math.random() * 32),
      },
      ability: pokemon.abilities?.[0] || 'Unknown',
      moves: (pokemon.moves || []).slice(0, 4),
    };

    if (selectedParent === 1) {
      setParent1(selectedPokemon);
    } else {
      setParent2(selectedPokemon);
    }
    
    setShowPokemonPicker(false);
  };

  const clearParent = (parentNumber) => {
    if (parentNumber === 1) {
      setParent1(null);
    } else {
      setParent2(null);
    }
  };

  const saveBreedingResult = () => {
    if (!breedingResult || !breedingResult.canBreed) {
      Alert.alert('Nothing to Save', 'No valid breeding result to save.');
      return;
    }

    const newRecord = {
      id: Date.now().toString(),
      parent1: parent1.name,
      parent2: parent2.name,
      offspring: breedingResult.offspring.species,
      compatibility: breedingResult.compatibility,
      date: new Date().toISOString(),
    };

    setBreedingHistory([newRecord, ...breedingHistory.slice(0, 9)]); // Keep 10 records
    Alert.alert('Saved', 'Breeding calculation saved to history!');
  };

  const getTypeColor = (type) => {
    const colors = {
      normal: '#A8A878', fire: '#F08030', water: '#6890F0', electric: '#F8D030',
      grass: '#78C850', ice: '#98D8D8', fighting: '#C03028', poison: '#A040A0',
      ground: '#E0C068', flying: '#A890F0', psychic: '#F85888', bug: '#A8B820',
      rock: '#B8A038', ghost: '#705898', dragon: '#7038F8', dark: '#705848',
      steel: '#B8B8D0', fairy: '#EE99AC',
    };
    return colors[type?.toLowerCase()] || '#68A090';
  };

  const renderPokemonCard = (pokemon, parentNumber) => (
    <View style={styles.parentCard}>
      <View style={styles.parentHeader}>
        <Text style={styles.parentTitle}>Parent {parentNumber}</Text>
        {pokemon && (
          <TouchableOpacity onPress={() => clearParent(parentNumber)}>
            <Icon name="close" size={20} color="#EF4444" />
          </TouchableOpacity>
        )}
      </View>

      {pokemon ? (
        <View style={styles.pokemonInfo}>
          <Text style={styles.pokemonName}>{pokemon.name}</Text>
          <Text style={styles.pokemonLevel}>Level {pokemon.level}</Text>
          
          <View style={styles.pokemonTypes}>
            {pokemon.types?.map((type, index) => (
              <View key={index} style={[styles.typeTag, {backgroundColor: getTypeColor(type)}]}>
                <Text style={styles.typeText}>{type}</Text>
              </View>
            ))}
          </View>

          <View style={styles.pokemonDetails}>
            <Text style={styles.detailLabel}>Nature: <Text style={styles.detailValue}>{pokemon.nature}</Text></Text>
            <Text style={styles.detailLabel}>Ability: <Text style={styles.detailValue}>{pokemon.ability}</Text></Text>
          </View>

          <View style={styles.ivsContainer}>
            <Text style={styles.ivsTitle}>IVs:</Text>
            <View style={styles.ivsList}>
              {Object.entries(pokemon.ivs || {}).map(([stat, value]) => (
                <Text key={stat} style={styles.ivStat}>
                  {stat.toUpperCase()}: {value}
                </Text>
              ))}
            </View>
          </View>
        </View>
      ) : (
        <TouchableOpacity
          style={styles.selectPokemonButton}
          onPress={() => {
            setSelectedParent(parentNumber);
            setShowPokemonPicker(true);
          }}>
          <Icon name="add-circle-outline" size={48} color="#3B82F6" />
          <Text style={styles.selectPokemonText}>Select Pokemon</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderBreedingResult = () => {
    if (!breedingResult) return null;

    if (!breedingResult.canBreed) {
      return (
        <View style={[styles.resultCard, styles.errorResult]}>
          <Icon name="error-outline" size={32} color="#EF4444" />
          <Text style={styles.errorTitle}>Cannot Breed</Text>
          <Text style={styles.errorReason}>{breedingResult.reason}</Text>
        </View>
      );
    }

    return (
      <View style={styles.resultCard}>
        <View style={styles.resultHeader}>
          <Icon name="child-care" size={24} color="#10B981" />
          <Text style={styles.resultTitle}>Breeding Result</Text>
          <TouchableOpacity
            style={styles.saveButton}
            onPress={saveBreedingResult}>
            <Icon name="save" size={20} color="#3B82F6" />
          </TouchableOpacity>
        </View>

        <View style={styles.offspringInfo}>
          <Text style={styles.offspringTitle}>Offspring: {breedingResult.offspring.species}</Text>
          <Text style={styles.compatibilityText}>
            Compatibility: {breedingResult.compatibility} ({breedingResult.eggCycles} egg cycles)
          </Text>

          <View style={styles.offspringTypes}>
            {breedingResult.offspring.types?.map((type, index) => (
              <View key={index} style={[styles.typeTag, {backgroundColor: getTypeColor(type)}]}>
                <Text style={styles.typeText}>{type}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.inheritanceSection}>
          <Text style={styles.inheritanceTitle}>Possible Abilities:</Text>
          <View style={styles.abilitiesList}>
            {breedingResult.possibleAbilities?.slice(0, 3).map((ability, index) => (
              <View key={index} style={styles.abilityTag}>
                <Text style={styles.abilityText}>{ability}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.inheritanceSection}>
          <Text style={styles.inheritanceTitle}>Egg Moves:</Text>
          <View style={styles.movesList}>
            {breedingResult.inheritedMoves?.slice(0, 6).map((move, index) => (
              <View key={index} style={styles.moveTag}>
                <Text style={styles.moveText}>{move}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.ivSection}>
          <Text style={styles.inheritanceTitle}>IV Inheritance:</Text>
          <Text style={styles.ivInfo}>
            {breedingResult.ivRange?.guaranteed} guaranteed perfect IVs from parents
          </Text>
        </View>
      </View>
    );
  };

  const renderPokemonItem = ({item}) => (
    <TouchableOpacity
      style={styles.pokemonItem}
      onPress={() => selectPokemon(item)}>
      <View style={styles.pokemonItemContent}>
        <Text style={styles.pokemonItemName}>{item.name}</Text>
        <View style={styles.pokemonItemTypes}>
          {item.types?.map((type, index) => (
            <View key={index} style={[styles.miniTypeTag, {backgroundColor: getTypeColor(type)}]}>
              <Text style={styles.miniTypeText}>{type}</Text>
            </View>
          ))}
        </View>
        <Text style={styles.pokemonItemInfo}>
          Species: {item.species || 'Unknown'}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={['#10B981', '#059669']}
        style={styles.header}>
        <Text style={styles.headerTitle}>Breeding Calculator</Text>
        <Text style={styles.headerSubtitle}>Calculate Pokemon breeding possibilities</Text>
      </LinearGradient>

      <ScrollView style={styles.content}>
        {/* Parent Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Parents</Text>
          <View style={styles.parentsContainer}>
            {renderPokemonCard(parent1, 1)}
            
            <View style={styles.breedingIcon}>
              <Icon name="favorite" size={24} color="#EC4899" />
            </View>
            
            {renderPokemonCard(parent2, 2)}
          </View>
        </View>

        {/* Breeding Result */}
        {(parent1 && parent2) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Breeding Result</Text>
            {renderBreedingResult()}
          </View>
        )}

        {/* Breeding History */}
        {breedingHistory.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Calculations</Text>
            {breedingHistory.map((record, index) => (
              <View key={record.id} style={styles.historyItem}>
                <View style={styles.historyHeader}>
                  <Text style={styles.historyParents}>
                    {record.parent1} × {record.parent2}
                  </Text>
                  <Text style={styles.historyDate}>
                    {new Date(record.date).toLocaleDateString()}
                  </Text>
                </View>
                <Text style={styles.historyOffspring}>
                  Offspring: {record.offspring}
                </Text>
                <Text style={styles.historyCompatibility}>
                  Compatibility: {record.compatibility}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Tips Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Breeding Tips</Text>
          <View style={styles.tipsList}>
            <View style={styles.tipItem}>
              <Icon name="lightbulb-outline" size={16} color="#F59E0B" />
              <Text style={styles.tipText}>Pokemon in the same Egg Group can breed</Text>
            </View>
            <View style={styles.tipItem}>
              <Icon name="lightbulb-outline" size={16} color="#F59E0B" />
              <Text style={styles.tipText}>Ditto can breed with most Pokemon</Text>
            </View>
            <View style={styles.tipItem}>
              <Icon name="lightbulb-outline" size={16} color="#F59E0B" />
              <Text style={styles.tipText}>Offspring inherit 3 perfect IVs from parents</Text>
            </View>
            <View style={styles.tipItem}>
              <Icon name="lightbulb-outline" size={16} color="#F59E0B" />
              <Text style={styles.tipText}>Nature can be inherited with Everstone</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* Pokemon Picker Modal */}
      <Modal
        visible={showPokemonPicker}
        animationType="slide"
        onRequestClose={() => setShowPokemonPicker(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowPokemonPicker(false)}>
              <Icon name="close" size={24} color="#1E293B" />
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Select Parent {selectedParent}</Text>
            <View style={{width: 24}} />
          </View>

          <TextInput
            style={styles.searchInput}
            placeholder="Search Pokemon..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />

          <FlatList
            data={filteredPokemon}
            renderItem={renderPokemonItem}
            keyExtractor={item => item.id?.toString() || item.name}
            showsVerticalScrollIndicator={false}
          />
        </View>
      </Modal>
    </View>
  );
};

// Fix the function name typo
const checkBreedingCompatibility = (p1, p2) => {
  // Simplified breeding compatibility check
  if (p1.name === p2.name) {
    return {
      canBreed: false,
      reason: 'Pokemon cannot breed with themselves'
    };
  }

  // Check egg groups (simplified)
  const eggGroups1 = p1.eggGroups || ['Unknown'];
  const eggGroups2 = p2.eggGroups || ['Unknown'];
  
  const hasCommonGroup = eggGroups1.some(group => eggGroups2.includes(group));
  
  if (eggGroups1.includes('Undiscovered') || eggGroups2.includes('Undiscovered')) {
    return {
      canBreed: false,
      reason: 'One or both Pokemon cannot breed'
    };
  }

  if (!hasCommonGroup && !eggGroups1.includes('Ditto') && !eggGroups2.includes('Ditto')) {
    return {
      canBreed: false,
      reason: 'Pokemon are not compatible for breeding'
    };
  }

  return {
    canBreed: true,
    level: hasCommonGroup ? 'High' : 'Medium',
    eggCycles: Math.floor(Math.random() * 30) + 20 // Random for demo
  };
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
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 16,
  },
  parentsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  parentCard: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  parentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  parentTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  selectPokemonButton: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  selectPokemonText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '500',
    marginTop: 8,
  },
  pokemonInfo: {
    alignItems: 'center',
  },
  pokemonName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  pokemonLevel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 8,
  },
  pokemonTypes: {
    flexDirection: 'row',
    marginBottom: 12,
    gap: 4,
  },
  typeTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  typeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
  },
  pokemonDetails: {
    alignItems: 'center',
    marginBottom: 12,
  },
  detailLabel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 2,
  },
  detailValue: {
    fontWeight: '600',
    color: '#1E293B',
  },
  ivsContainer: {
    alignItems: 'center',
  },
  ivsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 4,
  },
  ivsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  ivStat: {
    fontSize: 10,
    color: '#64748B',
    backgroundColor: '#E2E8F0',
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
  },
  breedingIcon: {
    marginHorizontal: 16,
    padding: 8,
  },
  resultCard: {
    backgroundColor: '#F0FDF4',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#BBF7D0',
  },
  errorResult: {
    backgroundColor: '#FEF2F2',
    borderColor: '#FECACA',
    alignItems: 'center',
    paddingVertical: 24,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#EF4444',
    marginVertical: 8,
  },
  errorReason: {
    fontSize: 14,
    color: '#DC2626',
    textAlign: 'center',
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#059669',
    flex: 1,
    marginLeft: 8,
  },
  saveButton: {
    padding: 4,
  },
  offspringInfo: {
    marginBottom: 16,
  },
  offspringTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  compatibilityText: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 8,
  },
  offspringTypes: {
    flexDirection: 'row',
    gap: 4,
  },
  inheritanceSection: {
    marginBottom: 12,
  },
  inheritanceTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 8,
  },
  abilitiesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  abilityTag: {
    backgroundColor: '#DBEAFE',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  abilityText: {
    fontSize: 12,
    color: '#1D4ED8',
    fontWeight: '500',
  },
  movesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  moveTag: {
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  moveText: {
    fontSize: 12,
    color: '#92400E',
    fontWeight: '500',
  },
  ivSection: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
  },
  ivInfo: {
    fontSize: 12,
    color: '#374151',
    fontStyle: 'italic',
  },
  historyItem: {
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#10B981',
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  historyParents: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
  },
  historyDate: {
    fontSize: 12,
    color: '#64748B',
  },
  historyOffspring: {
    fontSize: 12,
    color: '#059669',
    marginBottom: 2,
  },
  historyCompatibility: {
    fontSize: 12,
    color: '#64748B',
  },
  tipsList: {
    gap: 8,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
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
  searchInput: {
    margin: 16,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    fontSize: 16,
    backgroundColor: '#F9FAFB',
  },
  pokemonItem: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  pokemonItemContent: {
    flex: 1,
  },
  pokemonItemName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  pokemonItemTypes: {
    flexDirection: 'row',
    marginBottom: 4,
    gap: 4,
  },
  miniTypeTag: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  miniTypeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '500',
  },
  pokemonItemInfo: {
    fontSize: 12,
    color: '#64748B',
  },
});

export default BreedingScreen;