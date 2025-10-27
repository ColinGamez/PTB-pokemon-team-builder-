/**
 * ErrorBoundary Component
 * React Error Boundary for graceful error handling
 */

import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import {ErrorState} from './EmptyState';
import CustomButton from './CustomButton';
import Icon from 'react-native-vector-icons/MaterialIcons';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {hasError: false, error: null, errorInfo: null};
  }

  static getDerivedStateFromError(error) {
    return {hasError: true};
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
    
    // Log error to crash reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // You can also log the error to an error reporting service like Sentry
    // Sentry.captureException(error);
  }

  handleRetry = () => {
    this.setState({hasError: false, error: null, errorInfo: null});
    
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom error UI
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      return (
        <View style={styles.container}>
          <View style={styles.errorContainer}>
            <Icon name="error-outline" size={64} color="#EF4444" />
            
            <Text style={styles.title}>Something went wrong</Text>
            
            <Text style={styles.message}>
              {this.props.message || 'An unexpected error has occurred. Please try again.'}
            </Text>

            {this.state.error && __DEV__ && (
              <View style={styles.debugContainer}>
                <Text style={styles.debugTitle}>Error Details:</Text>
                <Text style={styles.debugText}>{this.state.error.toString()}</Text>
                
                {this.state.errorInfo && (
                  <>
                    <Text style={styles.debugTitle}>Component Stack:</Text>
                    <Text style={styles.debugText}>{this.state.errorInfo.componentStack}</Text>
                  </>
                )}
              </View>
            )}

            <View style={styles.actions}>
              <CustomButton
                title="Try Again"
                onPress={this.handleRetry}
                variant="primary"
                icon="refresh"
                style={styles.retryButton}
              />
              
              {this.props.onReport && (
                <CustomButton
                  title="Report Issue"
                  onPress={() => this.props.onReport(this.state.error)}
                  variant="outline"
                  icon="bug-report"
                  style={styles.reportButton}
                />
              )}
            </View>
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}

// Hook-based error boundary for functional components
export const useErrorHandler = () => {
  const [error, setError] = React.useState(null);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const captureError = React.useCallback((error, errorInfo = {}) => {
    console.error('Error captured:', error, errorInfo);
    setError({error, errorInfo});
    
    // Log to error reporting service
    // Sentry.captureException(error, {contexts: errorInfo});
  }, []);

  return {error, resetError, captureError};
};

// HOC for wrapping components with error boundary
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  const WrappedComponent = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
};

// Network Error Handler
export const NetworkErrorHandler = ({error, onRetry, style = {}}) => {
  const getErrorMessage = () => {
    if (error?.code === 'NETWORK_ERROR') {
      return 'No internet connection. Please check your network and try again.';
    }
    if (error?.code === 'TIMEOUT_ERROR') {
      return 'Request timed out. Please try again.';
    }
    if (error?.status >= 500) {
      return 'Server error. Please try again later.';
    }
    if (error?.status === 404) {
      return 'The requested resource was not found.';
    }
    if (error?.status === 401) {
      return 'You are not authorized to access this resource.';
    }
    
    return error?.message || 'An error occurred. Please try again.';
  };

  return (
    <View style={[styles.networkErrorContainer, style]}>
      <Icon
        name={error?.code === 'NETWORK_ERROR' ? 'wifi-off' : 'error-outline'}
        size={48}
        color="#EF4444"
      />
      
      <Text style={styles.networkErrorTitle}>Connection Error</Text>
      
      <Text style={styles.networkErrorMessage}>
        {getErrorMessage()}
      </Text>

      <CustomButton
        title="Try Again"
        onPress={onRetry}
        variant="primary"
        icon="refresh"
        style={styles.networkRetryButton}
      />
    </View>
  );
};

// Validation Error Display
export const ValidationErrorDisplay = ({errors = [], style = {}}) => {
  if (!errors.length) return null;

  return (
    <View style={[styles.validationContainer, style]}>
      {errors.map((error, index) => (
        <View key={index} style={styles.validationError}>
          <Icon name="error" size={16} color="#EF4444" />
          <Text style={styles.validationErrorText}>{error}</Text>
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorContainer: {
    alignItems: 'center',
    maxWidth: 400,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
  },
  debugContainer: {
    backgroundColor: '#FEF2F2',
    padding: 16,
    borderRadius: 8,
    marginBottom: 24,
    width: '100%',
    maxHeight: 200,
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#DC2626',
    marginBottom: 8,
  },
  debugText: {
    fontSize: 12,
    color: '#991B1B',
    fontFamily: 'monospace',
    marginBottom: 12,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
    justifyContent: 'center',
  },
  retryButton: {
    flex: 1,
    maxWidth: 150,
  },
  reportButton: {
    flex: 1,
    maxWidth: 150,
  },
  networkErrorContainer: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#FEF2F2',
    borderRadius: 12,
    margin: 16,
  },
  networkErrorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#DC2626',
    marginTop: 12,
    marginBottom: 8,
  },
  networkErrorMessage: {
    fontSize: 14,
    color: '#7F1D1D',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 20,
  },
  networkRetryButton: {
    minWidth: 120,
  },
  validationContainer: {
    marginVertical: 8,
  },
  validationError: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#EF4444',
  },
  validationErrorText: {
    fontSize: 14,
    color: '#DC2626',
    marginLeft: 8,
    flex: 1,
  },
});

export default ErrorBoundary;