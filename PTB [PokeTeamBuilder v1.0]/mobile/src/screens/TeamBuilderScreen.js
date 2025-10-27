/**
 * Team Builder Screen for Pokemon Team Builder Mobile App
 * Main team creation and editing interface
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  FlatList,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useApp} from '../context/AppContext';
import {ApiService} from '../services/ApiService';

const {width} = Dimensions.get('window');

const TeamBuilderScreen = ({navigation, route}) => {
  const {teams, addTeam, updateTeam, pokemonData, loading} = useApp();
  const [currentTeam, setCurrentTeam] = useState({
    name: '',
    format: 'Singles',
    pokemon: [],
    description: '',
  });
  const [showPokemonPicker, setShowPokemonPicker] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredPokemon, setFilteredPokemon] = useState([]);
  const [showMoveSelector, setShowMoveSelector] = useState(false);
  const [selectedPokemon, setSelectedPokemon] = useState(null);

  const teamFormats = ['Singles', 'Doubles', 'VGC', 'OU', 'UU', 'RU', 'NU'];

  useEffect(() => {
    // If editing existing team
    if (route.params?.team) {
      setCurrentTeam(route.params.team);
    }
  }, [route.params]);

  useEffect(() => {
    // Filter Pokemon based on search
    if (pokemonData && searchQuery) {
      const filtered = pokemonData.filter(pokemon =>
        pokemon.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pokemon.types.some(type => 
          type.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
      setFilteredPokemon(filtered.slice(0, 50)); // Limit for performance
    } else {
      setFilteredPokemon(pokemonData?.slice(0, 50) || []);
    }
  }, [searchQuery, pokemonData]);

  const handleSaveTeam = async () => {
    if (!currentTeam.name.trim()) {
      Alert.alert('Error', 'Please enter a team name');
      return;
    }

    if (currentTeam.pokemon.length === 0) {
      Alert.alert('Error', 'Please add at least one Pokemon to your team');
      return;
    }

    try {
      if (route.params?.team) {
        // Update existing team
        await updateTeam(currentTeam);
        Alert.alert('Success', 'Team updated successfully!');
      } else {
        // Create new team
        await addTeam(currentTeam);
        Alert.alert('Success', 'Team created successfully!');
      }
      navigation.goBack();
    } catch (error) {
      Alert.alert('Error', 'Failed to save team: ' + error.message);
    }
  };

  const handleAddPokemon = (pokemon) => {
    const newPokemon = {
      ...pokemon,
      level: 50,
      ability: pokemon.abilities?.[0] || 'Unknown',
      nature: 'Hardy',
      item: null,
      moves: [],
      evs: {hp: 0, attack: 0, defense: 0, spattack: 0, spdefense: 0, speed: 0},
      ivs: {hp: 31, attack: 31, defense: 31, spattack: 31, spdefense: 31, speed: 31},
    };

    const updatedPokemon = [...currentTeam.pokemon];
    updatedPokemon[selectedSlot] = newPokemon;
    
    setCurrentTeam({...currentTeam, pokemon: updatedPokemon});
    setShowPokemonPicker(false);
  };

  const handleRemovePokemon = (index) => {
    Alert.alert(
      'Remove Pokemon',
      'Are you sure you want to remove this Pokemon?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => {
            const updatedPokemon = [...currentTeam.pokemon];
            updatedPokemon.splice(index, 1);
            setCurrentTeam({...currentTeam, pokemon: updatedPokemon});
          },
        },
      ]
    );
  };

  const renderPokemonSlot = (index) => {
    const pokemon = currentTeam.pokemon[index];
    
    return (
      <TouchableOpacity
        key={index}
        style={[styles.pokemonSlot, pokemon ? styles.filledSlot : styles.emptySlot]}
        onPress={() => {
          setSelectedSlot(index);
          if (pokemon) {
            setSelectedPokemon(pokemon);
            setShowMoveSelector(true);
          } else {
            setShowPokemonPicker(true);
          }
        }}>
        {pokemon ? (
          <View style={styles.pokemonSlotContent}>
            <View style={styles.pokemonInfo}>
              <Text style={styles.pokemonName}>{pokemon.name}</Text>
              <Text style={styles.pokemonLevel}>Lv. {pokemon.level}</Text>
              <View style={styles.typesContainer}>
                {pokemon.types.map((type, typeIndex) => (
                  <View key={typeIndex} style={[styles.typeTag, {backgroundColor: getTypeColor(type)}]}>
                    <Text style={styles.typeText}>{type}</Text>
                  </View>
                ))}
              </View>
            </View>
            <TouchableOpacity
              style={styles.removeButton}
              onPress={() => handleRemovePokemon(index)}>
              <Icon name="close" size={16} color="#EF4444" />
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.emptySlotContent}>
            <Icon name="add" size={32} color="#94A3B8" />
            <Text style={styles.emptySlotText}>Add Pokemon</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const getTypeColor = (type) => {
    const colors = {
      normal: '#A8A878',
      fire: '#F08030',
      water: '#6890F0',
      electric: '#F8D030',
      grass: '#78C850',
      ice: '#98D8D8',
      fighting: '#C03028',
      poison: '#A040A0',
      ground: '#E0C068',
      flying: '#A890F0',
      psychic: '#F85888',
      bug: '#A8B820',
      rock: '#B8A038',
      ghost: '#705898',
      dragon: '#7038F8',
      dark: '#705848',
      steel: '#B8B8D0',
      fairy: '#EE99AC',
    };
    return colors[type.toLowerCase()] || '#68A090';
  };

  const renderPokemonItem = ({item}) => (
    <TouchableOpacity
      style={styles.pokemonItem}
      onPress={() => handleAddPokemon(item)}>
      <View style={styles.pokemonItemContent}>
        <Text style={styles.pokemonItemName}>{item.name}</Text>
        <View style={styles.pokemonItemTypes}>
          {item.types.map((type, index) => (
            <View key={index} style={[styles.typeTag, {backgroundColor: getTypeColor(type)}]}>
              <Text style={styles.typeText}>{type}</Text>
            </View>
          ))}
        </View>
        <Text style={styles.pokemonStats}>
          HP: {item.stats?.hp || 0} | ATK: {item.stats?.attack || 0} | DEF: {item.stats?.defense || 0}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-back" size={24} color="#1E293B" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>
          {route.params?.team ? 'Edit Team' : 'Build Team'}
        </Text>
        <TouchableOpacity onPress={handleSaveTeam}>
          <Text style={styles.saveButton}>Save</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Team Details */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Team Details</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Team Name"
            value={currentTeam.name}
            onChangeText={(text) => setCurrentTeam({...currentTeam, name: text})}
            maxLength={50}
          />

          <View style={styles.formatSelector}>
            <Text style={styles.formatLabel}>Format:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {teamFormats.map((format) => (
                <TouchableOpacity
                  key={format}
                  style={[
                    styles.formatChip,
                    currentTeam.format === format && styles.selectedFormatChip
                  ]}
                  onPress={() => setCurrentTeam({...currentTeam, format})}>
                  <Text style={[
                    styles.formatChipText,
                    currentTeam.format === format && styles.selectedFormatChipText
                  ]}>
                    {format}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          <TextInput
            style={styles.descriptionInput}
            placeholder="Team Description (optional)"
            value={currentTeam.description}
            onChangeText={(text) => setCurrentTeam({...currentTeam, description: text})}
            multiline
            numberOfLines={3}
            maxLength={200}
          />
        </View>

        {/* Pokemon Team */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Pokemon Team ({currentTeam.pokemon.length}/6)</Text>
          <View style={styles.teamGrid}>
            {[0, 1, 2, 3, 4, 5].map(renderPokemonSlot)}
          </View>
        </View>

        {/* Team Analysis */}
        {currentTeam.pokemon.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Team Analysis</Text>
            <TouchableOpacity style={styles.analysisButton}>
              <Icon name="analytics" size={20} color="#3B82F6" />
              <Text style={styles.analysisButtonText}>Analyze Team</Text>
            </TouchableOpacity>
          </View>
        )}
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
            <Text style={styles.modalTitle}>Choose Pokemon</Text>
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
            keyExtractor={(item) => item.id?.toString() || item.name}
            showsVerticalScrollIndicator={false}
          />
        </View>
      </Modal>

      {/* Move Selector Modal */}
      <Modal
        visible={showMoveSelector}
        animationType="slide"
        onRequestClose={() => setShowMoveSelector(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowMoveSelector(false)}>
              <Icon name="close" size={24} color="#1E293B" />
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Edit {selectedPokemon?.name}</Text>
            <TouchableOpacity>
              <Text style={styles.saveButton}>Save</Text>
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.pokemonDetails}>
            <Text style={styles.comingSoonText}>
              Detailed Pokemon editing coming soon!
            </Text>
            <Text style={styles.comingSoonSubtext}>
              • Move selection{'\n'}
              • EV/IV training{'\n'}
              • Ability & Nature{'\n'}
              • Item selection
            </Text>
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
  saveButton: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
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
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 12,
    backgroundColor: '#F9FAFB',
  },
  formatSelector: {
    marginBottom: 12,
  },
  formatLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8,
  },
  formatChip: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  selectedFormatChip: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  formatChipText: {
    fontSize: 12,
    color: '#374151',
    fontWeight: '500',
  },
  selectedFormatChipText: {
    color: 'white',
  },
  descriptionInput: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#F9FAFB',
    textAlignVertical: 'top',
  },
  teamGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  pokemonSlot: {
    width: (width - 80) / 2,
    height: 120,
    marginBottom: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderStyle: 'dashed',
  },
  emptySlot: {
    borderColor: '#D1D5DB',
    backgroundColor: '#F9FAFB',
  },
  filledSlot: {
    borderColor: '#3B82F6',
    backgroundColor: 'white',
    borderStyle: 'solid',
  },
  emptySlotContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptySlotText: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 4,
  },
  pokemonSlotContent: {
    flex: 1,
    padding: 8,
    justifyContent: 'space-between',
  },
  pokemonInfo: {
    flex: 1,
  },
  pokemonName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 2,
  },
  pokemonLevel: {
    fontSize: 11,
    color: '#64748B',
    marginBottom: 4,
  },
  typesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  typeTag: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginRight: 4,
    marginBottom: 2,
  },
  typeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  removeButton: {
    alignSelf: 'flex-end',
    padding: 4,
  },
  analysisButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#EBF8FF',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#3B82F6',
  },
  analysisButtonText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '600',
    marginLeft: 8,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
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
  },
  pokemonStats: {
    fontSize: 12,
    color: '#64748B',
  },
  pokemonDetails: {
    flex: 1,
    padding: 20,
  },
  comingSoonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    textAlign: 'center',
    marginBottom: 16,
  },
  comingSoonSubtext: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default TeamBuilderScreen;