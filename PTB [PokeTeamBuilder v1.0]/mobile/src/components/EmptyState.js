/**
 * EmptyState Component
 * Display empty states with illustrations and actions
 */

import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import CustomButton from './CustomButton';

const EmptyState = ({
  icon = 'inbox',
  title = 'Nothing here yet',
  description,
  actionText,
  onActionPress,
  secondaryActionText,
  onSecondaryActionPress,
  variant = 'default', // 'default', 'search', 'error', 'offline'
  size = 'medium', // 'small', 'medium', 'large'
  style = {},
  iconStyle = {},
  titleStyle = {},
  descriptionStyle = {},
}) => {
  const getVariantConfig = () => {
    const configs = {
      default: {
        icon: icon || 'inbox',
        iconColor: '#9CA3AF',
        backgroundColor: '#F9FAFB',
      },
      search: {
        icon: 'search-off',
        iconColor: '#6B7280',
        backgroundColor: '#F9FAFB',
        title: 'No results found',
        description: 'Try adjusting your search terms',
      },
      error: {
        icon: 'error-outline',
        iconColor: '#EF4444',
        backgroundColor: '#FEF2F2',
        title: 'Something went wrong',
        description: 'Please try again later',
      },
      offline: {
        icon: 'cloud-off',
        iconColor: '#F59E0B',
        backgroundColor: '#FFFBEF',
        title: 'You\'re offline',
        description: 'Check your internet connection',
      },
    };

    return configs[variant] || configs.default;
  };

  const getSizeConfig = () => {
    const configs = {
      small: {
        iconSize: 48,
        titleSize: 16,
        descriptionSize: 14,
        padding: 24,
      },
      medium: {
        iconSize: 64,
        titleSize: 20,
        descriptionSize: 16,
        padding: 32,
      },
      large: {
        iconSize: 80,
        titleSize: 24,
        descriptionSize: 18,
        padding: 40,
      },
    };

    return configs[size] || configs.medium;
  };

  const variantConfig = getVariantConfig();
  const sizeConfig = getSizeConfig();

  const displayTitle = title || variantConfig.title;
  const displayDescription = description || variantConfig.description;

  return (
    <View style={[styles.container, {padding: sizeConfig.padding}, style]}>
      {/* Icon Circle */}
      <View
        style={[
          styles.iconContainer,
          {
            backgroundColor: variantConfig.backgroundColor,
            width: sizeConfig.iconSize + 32,
            height: sizeConfig.iconSize + 32,
          },
          iconStyle,
        ]}>
        <Icon
          name={variantConfig.icon}
          size={sizeConfig.iconSize}
          color={variantConfig.iconColor}
        />
      </View>

      {/* Title */}
      {displayTitle && (
        <Text
          style={[
            styles.title,
            {fontSize: sizeConfig.titleSize},
            titleStyle,
          ]}>
          {displayTitle}
        </Text>
      )}

      {/* Description */}
      {displayDescription && (
        <Text
          style={[
            styles.description,
            {fontSize: sizeConfig.descriptionSize},
            descriptionStyle,
          ]}>
          {displayDescription}
        </Text>
      )}

      {/* Actions */}
      <View style={styles.actionsContainer}>
        {actionText && onActionPress && (
          <CustomButton
            title={actionText}
            onPress={onActionPress}
            variant="primary"
            size={size === 'large' ? 'large' : 'medium'}
            style={styles.primaryAction}
          />
        )}

        {secondaryActionText && onSecondaryActionPress && (
          <CustomButton
            title={secondaryActionText}
            onPress={onSecondaryActionPress}
            variant="ghost"
            size={size === 'large' ? 'large' : 'medium'}
            style={styles.secondaryAction}
          />
        )}
      </View>
    </View>
  );
};

// Specialized empty state components
export const NoTeamsState = ({onCreateTeam}) => (
  <EmptyState
    icon="group"
    title="No teams yet"
    description="Create your first Pokemon team to get started"
    actionText="Create Team"
    onActionPress={onCreateTeam}
  />
);

export const NoSearchResultsState = ({onClearSearch, searchTerm}) => (
  <EmptyState
    variant="search"
    description={searchTerm ? `No results found for "${searchTerm}"` : 'Try different search terms'}
    actionText="Clear Search"
    onActionPress={onClearSearch}
  />
);

export const ErrorState = ({onRetry, message}) => (
  <EmptyState
    variant="error"
    description={message || 'Something went wrong. Please try again.'}
    actionText="Retry"
    onActionPress={onRetry}
  />
);

export const OfflineState = ({onRetry}) => (
  <EmptyState
    variant="offline"
    actionText="Try Again"
    onActionPress={onRetry}
  />
);

export const NoPokemonState = ({onAddPokemon}) => (
  <EmptyState
    icon="catching-pokemon"
    title="No Pokémon in your team"
    description="Add some Pokémon to build your perfect team"
    actionText="Add Pokémon"
    onActionPress={onAddPokemon}
  />
);

export const LoadingErrorState = ({onRetry, error}) => (
  <EmptyState
    variant="error"
    title="Failed to load"
    description={error?.message || 'Something went wrong while loading data'}
    actionText="Try Again"
    onActionPress={onRetry}
  />
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  iconContainer: {
    borderRadius: 100,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  title: {
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  description: {
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
    maxWidth: 280,
  },
  actionsContainer: {
    width: '100%',
    maxWidth: 280,
    gap: 12,
  },
  primaryAction: {
    width: '100%',
  },
  secondaryAction: {
    width: '100%',
  },
});

export default EmptyState;