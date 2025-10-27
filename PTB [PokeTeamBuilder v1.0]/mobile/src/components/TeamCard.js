/**
 * TeamCard Component
 * Displays team information with Pokemon preview
 */

import React from 'react';
import {View, Text, TouchableOpacity, StyleSheet, ScrollView} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import PokemonCard from './PokemonCard';

const TeamCard = ({
  team,
  onPress,
  onEdit,
  onDelete,
  onShare,
  showActions = true,
  showPokemon = true,
  size = 'medium', // 'small', 'medium', 'large'
  style = {},
}) => {
  if (!team) return null;

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          container: styles.smallContainer,
          title: styles.smallTitle,
          subtitle: styles.smallSubtitle,
        };
      case 'large':
        return {
          container: styles.largeContainer,
          title: styles.largeTitle,
          subtitle: styles.largeSubtitle,
        };
      default:
        return {
          container: styles.mediumContainer,
          title: styles.mediumTitle,
          subtitle: styles.mediumSubtitle,
        };
    }
  };

  const sizeStyles = getSizeStyles();
  const pokemonList = team.pokemon || team.members || [];
  const teamSize = pokemonList.length;

  const getTeamTypeDistribution = () => {
    const types = {};
    pokemonList.forEach(pokemon => {
      if (pokemon.types) {
        pokemon.types.forEach(type => {
          types[type] = (types[type] || 0) + 1;
        });
      }
    });
    return Object.entries(types)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3);
  };

  const topTypes = getTeamTypeDistribution();

  const getTeamStrength = () => {
    if (teamSize === 0) return 0;
    const totalStats = pokemonList.reduce((sum, pokemon) => {
      if (pokemon.stats) {
        return sum + Object.values(pokemon.stats).reduce((statSum, stat) => statSum + (stat || 0), 0);
      }
      return sum;
    }, 0);
    return Math.min(Math.round(totalStats / (teamSize * 6)), 100); // Normalize to 0-100
  };

  const teamStrength = getTeamStrength();

  return (
    <TouchableOpacity
      style={[styles.card, sizeStyles.container, style]}
      onPress={onPress}
      activeOpacity={0.8}>
      
      <LinearGradient
        colors={['#FFFFFF', '#F8FAFC']}
        style={styles.gradient}>
        
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.teamInfo}>
            <Text style={[styles.teamName, sizeStyles.title]} numberOfLines={1}>
              {team.name || 'Unnamed Team'}
            </Text>
            
            <View style={styles.teamMeta}>
              <Text style={[styles.teamSize, sizeStyles.subtitle]}>
                {teamSize}/6 Pokémon
              </Text>
              
              {team.format && (
                <View style={styles.formatTag}>
                  <Text style={styles.formatText}>{team.format}</Text>
                </View>
              )}
            </View>
          </View>

          {/* Actions Menu */}
          {showActions && (
            <View style={styles.actionsContainer}>
              {onEdit && (
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={() => onEdit(team)}>
                  <Icon name="edit" size={18} color="#6B7280" />
                </TouchableOpacity>
              )}
              
              {onShare && (
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={() => onShare(team)}>
                  <Icon name="share" size={18} color="#6B7280" />
                </TouchableOpacity>
              )}
              
              {onDelete && (
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={() => onDelete(team)}>
                  <Icon name="delete" size={18} color="#EF4444" />
                </TouchableOpacity>
              )}
            </View>
          )}
        </View>

        {/* Team Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Icon name="trending-up" size={16} color="#10B981" />
            <Text style={styles.statLabel}>Strength</Text>
            <View style={styles.strengthBar}>
              <View
                style={[
                  styles.strengthFill,
                  {width: `${teamStrength}%`, backgroundColor: teamStrength > 70 ? '#10B981' : teamStrength > 40 ? '#F59E0B' : '#EF4444'}
                ]}
              />
            </View>
            <Text style={styles.statValue}>{teamStrength}%</Text>
          </View>

          {topTypes.length > 0 && (
            <View style={styles.typesContainer}>
              <Text style={styles.typesLabel}>Top Types:</Text>
              {topTypes.map(([type, count]) => (
                <View key={type} style={styles.typeChip}>
                  <Text style={styles.typeText}>{type} ({count})</Text>
                </View>
              ))}
            </View>
          )}
        </View>

        {/* Pokemon Preview */}
        {showPokemon && pokemonList.length > 0 && (
          <View style={styles.pokemonContainer}>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.pokemonList}>
              {pokemonList.slice(0, 6).map((pokemon, index) => (
                <View key={index} style={styles.pokemonPreview}>
                  <PokemonCard
                    pokemon={pokemon}
                    size="small"
                    showLevel={false}
                    showTypes={false}
                    showStats={false}
                    style={styles.pokemonPreviewCard}
                  />
                </View>
              ))}
              
              {/* Empty slots */}
              {Array.from({length: 6 - pokemonList.length}).map((_, index) => (
                <View key={`empty-${index}`} style={styles.emptySlot}>
                  <Icon name="add" size={20} color="#D1D5DB" />
                </View>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Team Details */}
        {team.description && (
          <Text style={styles.description} numberOfLines={2}>
            {team.description}
          </Text>
        )}

        {/* Footer */}
        <View style={styles.footer}>
          <View style={styles.footerLeft}>
            {team.createdAt && (
              <Text style={styles.dateText}>
                Created {new Date(team.createdAt).toLocaleDateString()}
              </Text>
            )}
          </View>

          <View style={styles.footerRight}>
            {team.wins !== undefined && team.losses !== undefined && (
              <Text style={styles.recordText}>
                {team.wins}W - {team.losses}L
              </Text>
            )}
            
            {team.rating && (
              <View style={styles.ratingContainer}>
                <Icon name="star" size={14} color="#F59E0B" />
                <Text style={styles.ratingText}>{team.rating}</Text>
              </View>
            )}
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    marginBottom: 16,
    overflow: 'hidden',
  },
  gradient: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  teamInfo: {
    flex: 1,
  },
  teamName: {
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  teamMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  teamSize: {
    color: '#6B7280',
  },
  formatTag: {
    backgroundColor: '#EBF8FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#3B82F6',
  },
  formatText: {
    fontSize: 10,
    color: '#3B82F6',
    fontWeight: '600',
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: 4,
  },
  actionButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#F9FAFB',
  },
  statsContainer: {
    marginBottom: 12,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  strengthBar: {
    flex: 1,
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    overflow: 'hidden',
  },
  strengthFill: {
    height: '100%',
    borderRadius: 3,
  },
  statValue: {
    fontSize: 12,
    color: '#374151',
    fontWeight: '600',
    minWidth: 32,
    textAlign: 'right',
  },
  typesContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  typesLabel: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  typeChip: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  typeText: {
    fontSize: 10,
    color: '#374151',
    fontWeight: '500',
  },
  pokemonContainer: {
    marginBottom: 12,
  },
  pokemonList: {
    gap: 8,
  },
  pokemonPreview: {
    width: 80,
  },
  pokemonPreviewCard: {
    margin: 0,
  },
  emptySlot: {
    width: 80,
    height: 60,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },
  description: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  footerLeft: {
    flex: 1,
  },
  footerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  dateText: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  recordText: {
    fontSize: 12,
    color: '#374151',
    fontWeight: '600',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
  },
  ratingText: {
    fontSize: 12,
    color: '#374151',
    fontWeight: '600',
  },
  // Size variants
  smallContainer: {
    marginBottom: 8,
  },
  mediumContainer: {
    marginBottom: 16,
  },
  largeContainer: {
    marginBottom: 20,
  },
  smallTitle: {
    fontSize: 16,
  },
  mediumTitle: {
    fontSize: 18,
  },
  largeTitle: {
    fontSize: 20,
  },
  smallSubtitle: {
    fontSize: 12,
  },
  mediumSubtitle: {
    fontSize: 14,
  },
  largeSubtitle: {
    fontSize: 16,
  },
});

export default TeamCard;