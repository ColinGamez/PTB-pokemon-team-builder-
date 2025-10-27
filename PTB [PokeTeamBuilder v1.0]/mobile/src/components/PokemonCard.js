/**
 * PokemonCard Component
 * Reusable Pokemon display card with comprehensive information
 */

import React from 'react';
import {View, Text, TouchableOpacity, StyleSheet, Image} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

const PokemonCard = ({
  pokemon,
  onPress,
  showLevel = true,
  showTypes = true,
  showStats = false,
  showMoves = false,
  size = 'medium',
  style = {},
}) => {
  if (!pokemon) return null;

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

  const getTypeGradient = (types) => {
    if (!types || types.length === 0) return ['#68A090', '#68A090'];
    if (types.length === 1) {
      const color = getTypeColor(types[0]);
      return [color, color];
    }
    return [getTypeColor(types[0]), getTypeColor(types[1])];
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          container: styles.smallContainer,
          pokemonName: styles.smallPokemonName,
          pokemonLevel: styles.smallPokemonLevel,
        };
      case 'large':
        return {
          container: styles.largeContainer,
          pokemonName: styles.largePokemonName,
          pokemonLevel: styles.largePokemonLevel,
        };
      default:
        return {
          container: styles.mediumContainer,
          pokemonName: styles.mediumPokemonName,
          pokemonLevel: styles.mediumPokemonLevel,
        };
    }
  };

  const sizeStyles = getSizeStyles();
  const gradientColors = getTypeGradient(pokemon.types);

  return (
    <TouchableOpacity
      style={[styles.card, sizeStyles.container, style]}
      onPress={onPress}
      activeOpacity={0.8}>
      
      <LinearGradient
        colors={[...gradientColors, 'rgba(255,255,255,0.9)']}
        style={styles.gradient}
        start={{x: 0, y: 0}}
        end={{x: 1, y: 1}}>
        
        {/* Pokemon Image Placeholder */}
        <View style={styles.imageContainer}>
          <View style={[styles.pokemonImage, {backgroundColor: gradientColors[0]}]}>
            <Icon name="catching-pokemon" size={size === 'large' ? 40 : size === 'small' ? 20 : 30} color="white" />
          </View>
        </View>

        {/* Pokemon Info */}
        <View style={styles.pokemonInfo}>
          <Text style={[styles.pokemonName, sizeStyles.pokemonName]} numberOfLines={1}>
            {pokemon.name}
          </Text>
          
          {showLevel && pokemon.level && (
            <Text style={[styles.pokemonLevel, sizeStyles.pokemonLevel]}>
              Level {pokemon.level}
            </Text>
          )}

          {/* Types */}
          {showTypes && pokemon.types && (
            <View style={styles.typesContainer}>
              {pokemon.types.slice(0, 2).map((type, index) => (
                <View
                  key={index}
                  style={[styles.typeTag, {backgroundColor: getTypeColor(type)}]}>
                  <Text style={styles.typeText}>{type}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Stats */}
          {showStats && pokemon.stats && (
            <View style={styles.statsContainer}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>HP</Text>
                <Text style={styles.statValue}>{pokemon.stats.hp || pokemon.currentHP || 0}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>ATK</Text>
                <Text style={styles.statValue}>{pokemon.stats.attack || 0}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>DEF</Text>
                <Text style={styles.statValue}>{pokemon.stats.defense || 0}</Text>
              </View>
            </View>
          )}

          {/* Moves */}
          {showMoves && pokemon.moves && pokemon.moves.length > 0 && (
            <View style={styles.movesContainer}>
              {pokemon.moves.slice(0, 2).map((move, index) => (
                <View key={index} style={styles.moveTag}>
                  <Text style={styles.moveText}>{move}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Additional Info */}
          {pokemon.ability && (
            <Text style={styles.abilityText}>
              <Icon name="star" size={12} color="#F59E0B" /> {pokemon.ability}
            </Text>
          )}
        </View>

        {/* Status Indicators */}
        <View style={styles.statusContainer}>
          {pokemon.isShiny && (
            <Icon name="auto-awesome" size={16} color="#FFD700" />
          )}
          {pokemon.item && (
            <Icon name="inventory" size={14} color="#8B5CF6" />
          )}
          {pokemon.currentHP !== undefined && pokemon.stats?.hp && pokemon.currentHP < pokemon.stats.hp && (
            <Icon name="healing" size={14} color="#EF4444" />
          )}
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 5,
    marginBottom: 8,
  },
  gradient: {
    flex: 1,
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  imageContainer: {
    marginRight: 12,
  },
  pokemonImage: {
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  pokemonInfo: {
    flex: 1,
  },
  pokemonName: {
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 2,
  },
  pokemonLevel: {
    color: '#64748B',
    fontSize: 12,
    marginBottom: 6,
  },
  typesContainer: {
    flexDirection: 'row',
    marginBottom: 6,
    gap: 4,
  },
  typeTag: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  typeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  statsContainer: {
    flexDirection: 'row',
    marginBottom: 6,
    gap: 8,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 8,
    color: '#64748B',
    fontWeight: '500',
  },
  statValue: {
    fontSize: 12,
    color: '#1E293B',
    fontWeight: 'bold',
  },
  movesContainer: {
    flexDirection: 'row',
    gap: 4,
    marginBottom: 4,
  },
  moveTag: {
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(59, 130, 246, 0.3)',
  },
  moveText: {
    fontSize: 10,
    color: '#3B82F6',
    fontWeight: '500',
  },
  abilityText: {
    fontSize: 10,
    color: '#64748B',
    fontStyle: 'italic',
  },
  statusContainer: {
    flexDirection: 'column',
    alignItems: 'center',
    gap: 4,
  },
  // Size variants
  smallContainer: {
    minHeight: 70,
  },
  mediumContainer: {
    minHeight: 90,
  },
  largeContainer: {
    minHeight: 120,
  },
  smallPokemonName: {
    fontSize: 14,
  },
  mediumPokemonName: {
    fontSize: 16,
  },
  largePokemonName: {
    fontSize: 18,
  },
  smallPokemonLevel: {
    fontSize: 10,
  },
  mediumPokemonLevel: {
    fontSize: 12,
  },
  largePokemonLevel: {
    fontSize: 14,
  },
});

export default PokemonCard;