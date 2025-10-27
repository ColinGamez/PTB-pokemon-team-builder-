/**
 * Component Index
 * Exports all reusable UI components
 */

// Core Components
export { default as PokemonCard } from './PokemonCard';
export { default as TeamCard } from './TeamCard';
export { default as SearchBar, SearchFilterChips } from './SearchBar';
export { default as CustomButton, FloatingActionButton, ButtonGroup } from './CustomButton';
export { default as LoadingSpinner, LoadingOverlay, InlineLoading } from './LoadingSpinner';

// Form Components
export { default as CustomInput, PasswordInput, EmailInput, NumberInput } from './CustomInput';

// Layout Components
export { default as Card, InfoCard, StatCard, ActionCard } from './Card';
export { default as EmptyState, NoTeamsState, NoSearchResultsState, ErrorState, OfflineState, NoPokemonState, LoadingErrorState } from './EmptyState';

// Modal Components  
export { default as BottomSheet, ActionSheet } from './BottomSheet';

// Stats Components
export { default as StatBar, StatBars, StatSummary, StatComparison } from './StatBar';
export { default as TypeBadge, TypeBadgeGroup, TypeEffectiveness } from './TypeBadge';
export { default as ProgressRing, MultiProgressRing, StatRing, HealthRing } from './ProgressRing';

// Animation Components
export { default as AnimatedComponents, FadeInView, SlideInView, ScaleView, BounceView, PulseView, ShakeView, SwipeableCard, StaggeredList, TypingText } from './AnimatedComponents';

// Error Handling Components
export { default as ErrorBoundary, useErrorHandler, withErrorBoundary, NetworkErrorHandler, ValidationErrorDisplay } from './ErrorBoundary';

// Performance Components
export { default as PerformanceOptimizations, MemoizedPokemonCard, MemoizedTeamCard, useExpensiveCalculation, useDebouncedSearch, OptimizedFlatList, useOptimizedImage, useResponsiveLayout } from './PerformanceOptimizations';