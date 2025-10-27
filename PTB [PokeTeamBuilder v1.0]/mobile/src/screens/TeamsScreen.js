/**
 * Teams Screen for Pokemon Team Builder Mobile App
 * Display all user teams with management options
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  Alert,
  RefreshControl,
} from 'react-native';
import {useApp} from '../context/AppContext';
import {
  TeamCard,
  SearchBar,
  SearchFilterChips,
  FloatingActionButton,
  NoTeamsState,
  NoSearchResultsState,
  FadeInView,
  LoadingSpinner,
  ActionSheet,
  BottomSheet,
  CustomButton,
} from '../components';

const TeamsScreen = ({navigation}) => {
  const {teams, deleteTeam, offlineMode, loading} = useApp();
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [showFilterSheet, setShowFilterSheet] = useState(false);
  const [showActionSheet, setShowActionSheet] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [filters, setFilters] = useState({
    format: 'All',
    sortBy: 'name',
    sortOrder: 'asc',
  });

  const filterChips = [
    {id: 'recent', label: 'Recent'},
    {id: 'favorites', label: 'Favorites'}, 
    {id: 'competitive', label: 'Competitive'},
    {id: 'casual', label: 'Casual'},
  ];
  
  const formats = ['All', 'Singles', 'Doubles', 'VGC', 'OU', 'UU', 'RU', 'NU'];
  const sortOptions = [
    {value: 'name', label: 'Name'},
    {value: 'created', label: 'Date Created'},
    {value: 'modified', label: 'Last Modified'},
    {value: 'format', label: 'Format'},
  ];

  useEffect(() => {
    filterAndSortTeams();
  }, [teams, searchQuery, filters]);

  const filterAndSortTeams = () => {
    let filtered = [...teams];

    // Apply search filter
    if (searchQuery.trim()) {
      filtered = filtered.filter(team =>
        team.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.format.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.pokemon?.some(pokemon =>
          pokemon.name?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    }

    // Apply chip filters
    if (selectedFilters.length > 0) {
      filtered = filtered.filter(team => {
        return selectedFilters.some(filterId => {
          switch (filterId) {
            case 'recent':
              return team.modified && 
                new Date(team.modified) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
            case 'favorites':
              return team.favorite;
            case 'competitive':
              return team.format && ['Singles', 'Doubles', 'VGC', 'OU'].includes(team.format);
            case 'casual':
              return !team.format || ['Casual', 'Custom'].includes(team.format);
            default:
              return true;
          }
        });
      });
    }

    // Apply format filter
    if (filters.format !== 'All') {
      filtered = filtered.filter(team => team.format === filters.format);
    }

    // Apply sorting with favorites priority
    filtered.sort((a, b) => {
      // Favorites first
      if (a.favorite && !b.favorite) return -1;
      if (!a.favorite && b.favorite) return 1;
      
      let aValue = a[filters.sortBy];
      let bValue = b[filters.sortBy];

      if (filters.sortBy === 'name') {
        aValue = aValue?.toLowerCase() || '';
        bValue = bValue?.toLowerCase() || '';
      }

      if (filters.sortOrder === 'desc') {
        return bValue > aValue ? 1 : -1;
      }
      return aValue > bValue ? 1 : -1;
    });

    setFilteredTeams(filtered);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    // Teams are managed by context, so just simulate refresh
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleFilterPress = (filter) => {
    setSelectedFilters(prev => {
      if (prev.includes(filter.id)) {
        return prev.filter(id => id !== filter.id);
      } else {
        return [...prev, filter.id];
      }
    });
  };

  const handleTeamAction = (team, action) => {
    setSelectedTeam(team);
    switch (action) {
      case 'edit':
        navigation.navigate('TeamBuilder', {team});
        break;
      case 'duplicate':
        handleDuplicateTeam(team);
        break;
      case 'share':
        handleShareTeam(team);
        break;
      case 'delete':
        setShowActionSheet(true);
        break;
    }
  };

  const handleDeleteTeam = async () => {
    if (selectedTeam) {
      try {
        await deleteTeam(selectedTeam.id);
        setShowActionSheet(false);
        setSelectedTeam(null);
      } catch (error) {
        Alert.alert('Error', 'Failed to delete team: ' + error.message);
      }
    }
  };

  const handleShareTeam = (team) => {
    Alert.alert('Coming Soon', 'Team sharing will be available soon!');
  };

  const handleDuplicateTeam = (team) => {
    const duplicatedTeam = {
      ...team,
      id: null, // Will be assigned when saved
      name: `${team.name} (Copy)`,
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
    };
    
    navigation.navigate('TeamBuilder', {team: duplicatedTeam});
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

  const renderTeamItem = ({item, index}) => (
    <FadeInView delay={index * 50}>
      <TeamCard
        team={{
          ...item,
          members: item.pokemon, // Map pokemon to members for TeamCard
          createdAt: item.created,
          lastModified: item.modified,
        }}
        onPress={() => navigation.navigate('TeamDetail', {team: item})}
        onEdit={() => handleTeamAction(item, 'edit')}
        onDelete={() => handleTeamAction(item, 'delete')}
        onShare={() => handleTeamAction(item, 'share')}
        showActions={true}
        showPokemon={true}
        style={styles.teamCard}
      />
    </FadeInView>
  );

  const showTeamMenu = (team) => {
    Alert.alert(
      team.name,
      'Choose an action',
      [
        {text: 'Edit', onPress: () => navigation.navigate('TeamBuilder', {team})},
        {text: 'Duplicate', onPress: () => handleDuplicateTeam(team)},
        {text: 'Share', onPress: () => Alert.alert('Coming Soon', 'Team sharing will be available soon!')},
        {text: 'Delete', style: 'destructive', onPress: () => handleDeleteTeam(team)},
        {text: 'Cancel', style: 'cancel'},
      ]
    );
  };

  const getFormatColor = (format) => {
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

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const renderEmptyState = () => {
    if (searchQuery.trim() && filteredTeams.length === 0) {
      return (
        <NoSearchResultsState
          searchTerm={searchQuery}
          onClearSearch={() => setSearchQuery('')}
        />
      );
    }
    
    return (
      <NoTeamsState
        onCreateTeam={() => navigation.navigate('TeamBuilder')}
      />
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner
          variant="pokeball"
          message="Loading your teams..."
          size="large"
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>My Teams</Text>
          <Text style={styles.headerSubtitle}>
            {filteredTeams.length} team{filteredTeams.length !== 1 ? 's' : ''}
          </Text>
        </View>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <SearchBar
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Search teams and Pokémon..."
          rightIcon="filter-list"
          onRightIconPress={() => setShowFilterSheet(true)}
          showClearButton={true}
          style={styles.searchBar}
        />
      </View>

      {/* Filter Chips */}
      <SearchFilterChips
        filters={filterChips}
        selectedFilters={selectedFilters}
        onFilterPress={handleFilterPress}
        style={styles.filterChips}
      />

      {/* Teams List */}
      <FlatList
        data={filteredTeams}
        renderItem={renderTeamItem}
        keyExtractor={item => item.id?.toString() || item.name}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={filteredTeams.length === 0 ? styles.emptyContainer : styles.listContainer}
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        windowSize={10}
      />

      {/* Floating Action Button */}
      <FloatingActionButton
        icon="add"
        onPress={() => navigation.navigate('TeamBuilder')}
        backgroundColor="#3B82F6"
      />

      {/* Filter Bottom Sheet */}
      <BottomSheet
        visible={showFilterSheet}
        onClose={() => setShowFilterSheet(false)}
        title="Filter & Sort Teams"
        showHandle={true}>
        
        <View style={styles.filterSheetContent}>
          {/* Format Filter */}
          <View style={styles.filterSection}>
            <Text style={styles.filterTitle}>Format</Text>
            <View style={styles.filterOptions}>
              {formats.map(format => (
                <CustomButton
                  key={format}
                  title={format}
                  variant={filters.format === format ? 'primary' : 'outline'}
                  size="small"
                  onPress={() => setFilters({...filters, format})}
                  style={styles.formatButton}
                />
              ))}
            </View>
          </View>

          {/* Sort Options */}
          <View style={styles.filterSection}>
            <Text style={styles.filterTitle}>Sort By</Text>
            {sortOptions.map(option => (
              <CustomButton
                key={option.value}
                title={option.label}
                variant={filters.sortBy === option.value ? 'primary' : 'ghost'}
                onPress={() => setFilters({...filters, sortBy: option.value})}
                style={styles.sortButton}
                icon={filters.sortBy === option.value ? 'check' : undefined}
                iconPosition="right"
              />
            ))}
          </View>

          {/* Sort Order */}
          <View style={styles.filterSection}>
            <Text style={styles.filterTitle}>Order</Text>
            <CustomButton
              title={filters.sortOrder === 'asc' ? 'Ascending' : 'Descending'}
              variant="outline"
              icon={filters.sortOrder === 'asc' ? 'keyboard-arrow-up' : 'keyboard-arrow-down'}
              iconPosition="right"
              onPress={() => setFilters({
                ...filters,
                sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc'
              })}
              style={styles.sortOrderButton}
            />
          </View>
        </View>
      </BottomSheet>

      {/* Delete Confirmation Action Sheet */}
      <ActionSheet
        visible={showActionSheet}
        onClose={() => setShowActionSheet(false)}
        title={selectedTeam ? `Delete "${selectedTeam.name}"?` : 'Delete Team'}
        actions={[
          {
            title: 'Delete Team',
            icon: 'delete',
            onPress: handleDeleteTeam,
          },
        ]}
        destructiveIndex={0}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  headerContent: {
    alignItems: 'flex-start',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#64748B',
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    backgroundColor: '#F8FAFC',
  },
  searchBar: {
    marginBottom: 0,
  },
  filterChips: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    backgroundColor: '#F8FAFC',
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  teamCard: {
    marginHorizontal: 0,
    marginBottom: 16,
  },
  teamHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  teamInfo: {
    flex: 1,
  },
  teamName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  teamMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  formatBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  formatText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  pokemonCount: {
    fontSize: 12,
    color: '#64748B',
    marginRight: 8,
    marginBottom: 4,
  },
  menuButton: {
    padding: 4,
  },
  pokemonPreview: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  pokemonSlot: {
    width: 45,
    height: 45,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filledPokemonSlot: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  emptyPokemonSlot: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderStyle: 'dashed',
  },
  pokemonSlotContent: {
    alignItems: 'center',
  },
  pokemonSlotName: {
    fontSize: 8,
    fontWeight: '600',
    color: '#1E293B',
    textAlign: 'center',
    marginBottom: 2,
  },
  pokemonTypes: {
    flexDirection: 'row',
  },
  miniTypeTag: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginHorizontal: 1,
  },
  teamDescription: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 12,
    lineHeight: 20,
  },
  teamFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  lastModified: {
    fontSize: 12,
    color: '#94A3B8',
  },
  teamActions: {
    flexDirection: 'row',
  },
  actionButton: {
    padding: 8,
    marginLeft: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1E293B',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  createButton: {
    backgroundColor: '#3B82F6',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 24,
  },
  createButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  filterSheetContent: {
    paddingVertical: 16,
  },
  filterSection: {
    marginBottom: 24,
  },
  filterTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 16,
  },
  filterOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  formatButton: {
    marginRight: 0,
    marginBottom: 8,
  },
  sortButton: {
    marginBottom: 8,
    width: '100%',
  },
  sortOrderButton: {
    width: '100%',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default TeamsScreen;