/**
 * Performance Optimizations
 * React memo components and performance utilities
 */

import React, {memo, useMemo, useCallback} from 'react';
import {Platform, InteractionManager} from 'react-native';

// Memoized PokemonCard for better list performance
export const MemoizedPokemonCard = memo(({pokemon, ...props}) => {
  const PokemonCard = require('./PokemonCard').default;
  
  return (
    <PokemonCard
      pokemon={pokemon}
      {...props}
    />
  );
}, (prevProps, nextProps) => {
  // Custom comparison for better performance
  return (
    prevProps.pokemon?.id === nextProps.pokemon?.id &&
    prevProps.pokemon?.name === nextProps.pokemon?.name &&
    prevProps.pokemon?.level === nextProps.pokemon?.level &&
    prevProps.showLevel === nextProps.showLevel &&
    prevProps.showTypes === nextProps.showTypes &&
    prevProps.showStats === nextProps.showStats &&
    prevProps.size === nextProps.size
  );
});

// Memoized TeamCard for better list performance
export const MemoizedTeamCard = memo(({team, ...props}) => {
  const TeamCard = require('./TeamCard').default;
  
  return (
    <TeamCard
      team={team}
      {...props}
    />
  );
}, (prevProps, nextProps) => {
  return (
    prevProps.team?.id === nextProps.team?.id &&
    prevProps.team?.name === nextProps.team?.name &&
    prevProps.team?.lastModified === nextProps.team?.lastModified &&
    prevProps.team?.pokemon?.length === nextProps.team?.pokemon?.length &&
    prevProps.showActions === nextProps.showActions &&
    prevProps.showPokemon === nextProps.showPokemon &&
    prevProps.size === nextProps.size
  );
});

// Performance hook for expensive calculations
export const useExpensiveCalculation = (calculator, dependencies, debounceMs = 0) => {
  const [result, setResult] = React.useState(null);
  const [isCalculating, setIsCalculating] = React.useState(false);
  
  const debouncedCalculator = useMemo(() => {
    if (debounceMs === 0) return calculator;
    
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => calculator(...args), debounceMs);
    };
  }, [calculator, debounceMs]);

  React.useEffect(() => {
    setIsCalculating(true);
    
    // Run calculation after interactions are complete
    InteractionManager.runAfterInteractions(() => {
      try {
        const calculationResult = debouncedCalculator();
        
        if (calculationResult instanceof Promise) {
          calculationResult
            .then(setResult)
            .finally(() => setIsCalculating(false));
        } else {
          setResult(calculationResult);
          setIsCalculating(false);
        }
      } catch (error) {
        console.error('Calculation error:', error);
        setIsCalculating(false);
      }
    });
  }, dependencies);

  return {result, isCalculating};
};

// Virtualized list item component
export const VirtualizedListItem = memo(({
  item,
  index,
  renderItem,
  getItemHeight,
  isVisible = true,
}) => {
  const itemHeight = useMemo(() => {
    return getItemHeight ? getItemHeight(item, index) : 60;
  }, [item, index, getItemHeight]);

  if (!isVisible) {
    // Return placeholder with correct height
    return <View style={{height: itemHeight}} />;
  }

  return renderItem({item, index});
});

// Debounced search hook
export const useDebouncedSearch = (searchTerm, delay = 300) => {
  const [debouncedTerm, setDebouncedTerm] = React.useState(searchTerm);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, delay]);

  return debouncedTerm;
};

// Optimized FlatList component
export const OptimizedFlatList = memo(({
  data,
  renderItem,
  keyExtractor,
  getItemLayout,
  estimatedItemSize = 100,
  windowSize = 10,
  maxToRenderPerBatch = 10,
  ...props
}) => {
  const {FlatList} = require('react-native');
  
  const optimizedRenderItem = useCallback(({item, index}) => {
    return (
      <VirtualizedListItem
        item={item}
        index={index}
        renderItem={renderItem}
        getItemHeight={() => estimatedItemSize}
      />
    );
  }, [renderItem, estimatedItemSize]);

  const optimizedGetItemLayout = useCallback((data, index) => {
    if (getItemLayout) {
      return getItemLayout(data, index);
    }
    
    return {
      length: estimatedItemSize,
      offset: estimatedItemSize * index,
      index,
    };
  }, [getItemLayout, estimatedItemSize]);

  return (
    <FlatList
      data={data}
      renderItem={optimizedRenderItem}
      keyExtractor={keyExtractor}
      getItemLayout={optimizedGetItemLayout}
      windowSize={windowSize}
      maxToRenderPerBatch={maxToRenderPerBatch}
      removeClippedSubviews={Platform.OS === 'android'}
      initialNumToRender={windowSize}
      updateCellsBatchingPeriod={50}
      {...props}
    />
  );
});

// Image loading optimization hook
export const useOptimizedImage = (source, placeholder) => {
  const [imageSource, setImageSource] = React.useState(placeholder);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    if (!source) {
      setImageSource(placeholder);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Preload image
    const {Image} = require('react-native');
    Image.prefetch(source)
      .then(() => {
        setImageSource(source);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err);
        setImageSource(placeholder);
        setIsLoading(false);
      });
  }, [source, placeholder]);

  return {imageSource, isLoading, error};
};

// Batch state updates hook
export const useBatchedUpdates = () => {
  const batchedUpdates = useCallback((updates) => {
    // Use React's unstable_batchedUpdates for React 17 and below
    // For React 18+, batching is automatic
    if (React.unstable_batchedUpdates) {
      React.unstable_batchedUpdates(() => {
        updates.forEach(update => update());
      });
    } else {
      updates.forEach(update => update());
    }
  }, []);

  return batchedUpdates;
};

// Memory usage monitoring (dev only)
export const useMemoryMonitor = (componentName) => {
  React.useEffect(() => {
    if (__DEV__) {
      const checkMemory = () => {
        if (global.performance && global.performance.memory) {
          const memory = global.performance.memory;
          console.log(`[${componentName}] Memory Usage:`, {
            used: Math.round(memory.usedJSHeapSize / 1048576) + ' MB',
            total: Math.round(memory.totalJSHeapSize / 1048576) + ' MB',
            limit: Math.round(memory.jsHeapSizeLimit / 1048576) + ' MB',
          });
        }
      };

      const interval = setInterval(checkMemory, 10000); // Check every 10 seconds
      return () => clearInterval(interval);
    }
  }, [componentName]);
};

// Responsive design hook
export const useResponsiveLayout = () => {
  const {Dimensions} = require('react-native');
  const [dimensions, setDimensions] = React.useState(Dimensions.get('window'));

  React.useEffect(() => {
    const subscription = Dimensions.addEventListener('change', ({window}) => {
      setDimensions(window);
    });

    return () => subscription?.remove();
  }, []);

  const layout = useMemo(() => {
    const {width, height} = dimensions;
    const isLandscape = width > height;
    const isTablet = Math.min(width, height) >= 768;
    const isPhone = !isTablet;

    return {
      width,
      height,
      isLandscape,
      isTablet,
      isPhone,
      isSmallPhone: isPhone && Math.min(width, height) < 375,
      isLargePhone: isPhone && Math.min(width, height) >= 414,
      columns: isTablet ? (isLandscape ? 3 : 2) : 1,
    };
  }, [dimensions]);

  return layout;
};

// Lazy component loader
export const createLazyComponent = (importFunction, fallback = null) => {
  const LazyComponent = React.lazy(importFunction);
  
  return React.forwardRef((props, ref) => (
    <React.Suspense fallback={fallback}>
      <LazyComponent {...props} ref={ref} />
    </React.Suspense>
  ));
};

export default {
  MemoizedPokemonCard,
  MemoizedTeamCard,
  useExpensiveCalculation,
  VirtualizedListItem,
  useDebouncedSearch,
  OptimizedFlatList,
  useOptimizedImage,
  useBatchedUpdates,
  useMemoryMonitor,
  useResponsiveLayout,
  createLazyComponent,
};