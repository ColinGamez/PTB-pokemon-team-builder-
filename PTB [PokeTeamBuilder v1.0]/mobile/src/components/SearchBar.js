/**
 * SearchBar Component
 * Enhanced search input with filtering and suggestions
 */

import React, {useState, useRef, useEffect} from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  StyleSheet,
  FlatList,
  Animated,
  Keyboard,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const SearchBar = ({
  placeholder = 'Search...',
  value = '',
  onChangeText,
  onSubmit,
  onClear,
  suggestions = [],
  showSuggestions = false,
  onSuggestionPress,
  autoFocus = false,
  disabled = false,
  style = {},
  inputStyle = {},
  containerStyle = {},
  renderSuggestion,
  maxSuggestions = 5,
  debounceDelay = 300,
  showClearButton = true,
  leftIcon,
  rightIcon,
  onLeftIconPress,
  onRightIconPress,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showSuggestionsState, setShowSuggestionsState] = useState(false);
  const [searchValue, setSearchValue] = useState(value);
  
  const inputRef = useRef(null);
  const animatedValue = useRef(new Animated.Value(0)).current;
  const debounceRef = useRef(null);

  useEffect(() => {
    setSearchValue(value);
  }, [value]);

  useEffect(() => {
    // Animate focus state
    Animated.timing(animatedValue, {
      toValue: isFocused ? 1 : 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  }, [isFocused]);

  useEffect(() => {
    // Debounced search
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      if (onChangeText) {
        onChangeText(searchValue);
      }
    }, debounceDelay);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [searchValue, debounceDelay, onChangeText]);

  const handleFocus = () => {
    setIsFocused(true);
    if (showSuggestions && suggestions.length > 0) {
      setShowSuggestionsState(true);
    }
  };

  const handleBlur = () => {
    setIsFocused(false);
    // Delay hiding suggestions to allow for suggestion tap
    setTimeout(() => {
      setShowSuggestionsState(false);
    }, 150);
  };

  const handleChangeText = (text) => {
    setSearchValue(text);
    if (showSuggestions) {
      setShowSuggestionsState(text.length > 0 && suggestions.length > 0);
    }
  };

  const handleClear = () => {
    setSearchValue('');
    setShowSuggestionsState(false);
    if (onClear) {
      onClear();
    }
    if (onChangeText) {
      onChangeText('');
    }
    inputRef.current?.focus();
  };

  const handleSubmit = () => {
    Keyboard.dismiss();
    setShowSuggestionsState(false);
    if (onSubmit) {
      onSubmit(searchValue);
    }
  };

  const handleSuggestionPress = (suggestion) => {
    setSearchValue(suggestion.text || suggestion);
    setShowSuggestionsState(false);
    Keyboard.dismiss();
    
    if (onSuggestionPress) {
      onSuggestionPress(suggestion);
    }
    if (onChangeText) {
      onChangeText(suggestion.text || suggestion);
    }
  };

  const borderColor = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['#D1D5DB', '#3B82F6'],
  });

  const renderDefaultSuggestion = ({item, index}) => (
    <TouchableOpacity
      style={[
        styles.suggestionItem,
        index === suggestions.length - 1 && styles.suggestionItemLast,
      ]}
      onPress={() => handleSuggestionPress(item)}>
      <Icon name="search" size={16} color="#6B7280" style={styles.suggestionIcon} />
      <Text style={styles.suggestionText} numberOfLines={1}>
        {item.text || item}
      </Text>
      {item.category && (
        <Text style={styles.suggestionCategory}>{item.category}</Text>
      )}
    </TouchableOpacity>
  );

  const filteredSuggestions = suggestions.slice(0, maxSuggestions);

  return (
    <View style={[styles.container, containerStyle]}>
      <Animated.View
        style={[
          styles.searchContainer,
          {borderColor},
          style,
        ]}>
        
        {/* Left Icon */}
        {leftIcon ? (
          <TouchableOpacity
            style={styles.iconButton}
            onPress={onLeftIconPress}>
            <Icon name={leftIcon} size={20} color="#6B7280" />
          </TouchableOpacity>
        ) : (
          <Icon name="search" size={20} color="#6B7280" style={styles.searchIcon} />
        )}

        {/* Text Input */}
        <TextInput
          ref={inputRef}
          style={[styles.input, inputStyle]}
          placeholder={placeholder}
          placeholderTextColor="#9CA3AF"
          value={searchValue}
          onChangeText={handleChangeText}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onSubmitEditing={handleSubmit}
          autoFocus={autoFocus}
          editable={!disabled}
          returnKeyType="search"
          autoCapitalize="none"
          autoCorrect={false}
        />

        {/* Clear Button */}
        {showClearButton && searchValue.length > 0 && (
          <TouchableOpacity
            style={styles.iconButton}
            onPress={handleClear}>
            <Icon name="clear" size={20} color="#6B7280" />
          </TouchableOpacity>
        )}

        {/* Right Icon */}
        {rightIcon && (
          <TouchableOpacity
            style={styles.iconButton}
            onPress={onRightIconPress}>
            <Icon name={rightIcon} size={20} color="#6B7280" />
          </TouchableOpacity>
        )}
      </Animated.View>

      {/* Suggestions */}
      {showSuggestionsState && filteredSuggestions.length > 0 && (
        <View style={styles.suggestionsContainer}>
          <FlatList
            data={filteredSuggestions}
            keyExtractor={(item, index) => 
              item.id || item.text || item.toString() + index
            }
            renderItem={renderSuggestion || renderDefaultSuggestion}
            style={styles.suggestionsList}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          />
        </View>
      )}
    </View>
  );
};

// Search Filter Chips Component
export const SearchFilterChips = ({
  filters = [],
  selectedFilters = [],
  onFilterPress,
  style = {},
}) => {
  return (
    <View style={[styles.filtersContainer, style]}>
      <FlatList
        data={filters}
        keyExtractor={(item) => item.id || item.label}
        renderItem={({item}) => {
          const isSelected = selectedFilters.includes(item.id || item.label);
          return (
            <TouchableOpacity
              style={[
                styles.filterChip,
                isSelected && styles.filterChipSelected,
              ]}
              onPress={() => onFilterPress(item)}>
              <Text
                style={[
                  styles.filterChipText,
                  isSelected && styles.filterChipTextSelected,
                ]}>
                {item.label}
              </Text>
              {isSelected && (
                <Icon name="check" size={14} color="#FFFFFF" style={styles.filterCheckIcon} />
              )}
            </TouchableOpacity>
          );
        }}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filtersContent}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#1F2937',
    paddingVertical: 4,
  },
  iconButton: {
    padding: 4,
    marginLeft: 4,
  },
  suggestionsContainer: {
    position: 'absolute',
    top: '100%',
    left: 0,
    right: 0,
    zIndex: 1000,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    marginTop: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    maxHeight: 200,
  },
  suggestionsList: {
    flex: 1,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  suggestionItemLast: {
    borderBottomWidth: 0,
  },
  suggestionIcon: {
    marginRight: 12,
  },
  suggestionText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
  },
  suggestionCategory: {
    fontSize: 12,
    color: '#6B7280',
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginLeft: 8,
  },
  filtersContainer: {
    marginTop: 12,
  },
  filtersContent: {
    paddingHorizontal: 4,
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  filterChipSelected: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  filterChipText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  filterChipTextSelected: {
    color: '#FFFFFF',
  },
  filterCheckIcon: {
    marginLeft: 4,
  },
});

export default SearchBar;