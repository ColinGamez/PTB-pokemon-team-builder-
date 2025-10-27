/**
 * Login Screen for Pokemon Team Builder Mobile App
 * Authentication interface with login and registration
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useApp} from '../context/AppContext';
import {AuthService} from '../services/AuthService';

const LoginScreen = ({navigation}) => {
  const {login, offlineMode} = useApp();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    // Clear errors when switching between login/register
    setErrors({});
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    });
  }, [isLogin]);

  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!isLogin && !formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (!isLogin && formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Email validation (required for both login and register)
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!isLogin && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    // Confirm password validation (register only)
    if (!isLogin && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAuth = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      if (isLogin) {
        // Login
        const user = await AuthService.login(formData.email, formData.password);
        await login(user);
        Alert.alert('Success', 'Welcome back!');
      } else {
        // Register
        const user = await AuthService.register(
          formData.username,
          formData.email,
          formData.password
        );
        await login(user);
        Alert.alert('Success', 'Account created successfully!');
      }
    } catch (error) {
      console.error('Auth error:', error);
      Alert.alert(
        'Authentication Error',
        error.message || 'Something went wrong. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleOfflineMode = () => {
    Alert.alert(
      'Offline Mode',
      'Continue without an account? Your data will be stored locally and synced when you connect.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Continue Offline',
          onPress: async () => {
            try {
              await login({
                id: 'offline-user',
                username: 'Offline Trainer',
                email: 'offline@local.com',
                isOffline: true,
              });
            } catch (error) {
              Alert.alert('Error', 'Failed to start offline mode');
            }
          },
        },
      ]
    );
  };

  const renderInput = (
    key,
    placeholder,
    icon,
    secureTextEntry = false,
    keyboardType = 'default'
  ) => (
    <View style={styles.inputContainer}>
      <View style={[styles.inputWrapper, errors[key] && styles.inputError]}>
        <Icon name={icon} size={20} color="#64748B" style={styles.inputIcon} />
        <TextInput
          style={styles.input}
          placeholder={placeholder}
          placeholderTextColor="#94A3B8"
          value={formData[key]}
          onChangeText={(text) => {
            setFormData({...formData, [key]: text});
            if (errors[key]) {
              setErrors({...errors, [key]: null});
            }
          }}
          secureTextEntry={secureTextEntry && !showPassword}
          keyboardType={keyboardType}
          autoCapitalize={key === 'email' ? 'none' : 'words'}
          autoCorrect={false}
        />
        {key === 'password' && (
          <TouchableOpacity
            onPress={() => setShowPassword(!showPassword)}
            style={styles.eyeIcon}>
            <Icon
              name={showPassword ? 'visibility-off' : 'visibility'}
              size={20}
              color="#64748B"
            />
          </TouchableOpacity>
        )}
      </View>
      {errors[key] && <Text style={styles.errorText}>{errors[key]}</Text>}
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <LinearGradient
        colors={['#3B82F6', '#1D4ED8', '#1E40AF']}
        style={styles.gradient}>
        
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled">
          
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logoContainer}>
              <Icon name="catching-pokemon" size={64} color="white" />
            </View>
            <Text style={styles.title}>Pokemon Team Builder</Text>
            <Text style={styles.subtitle}>
              {isLogin ? 'Welcome back, Trainer!' : 'Join the Pokemon community!'}
            </Text>
          </View>

          {/* Form */}
          <View style={styles.formContainer}>
            <View style={styles.form}>
              {!isLogin && renderInput('username', 'Username', 'person')}
              
              {renderInput('email', 'Email', 'email', false, 'email-address')}
              
              {renderInput('password', 'Password', 'lock', true)}
              
              {!isLogin && renderInput('confirmPassword', 'Confirm Password', 'lock', true)}

              {/* Submit Button */}
              <TouchableOpacity
                style={[styles.submitButton, loading && styles.submitButtonDisabled]}
                onPress={handleAuth}
                disabled={loading}>
                {loading ? (
                  <ActivityIndicator color="white" size="small" />
                ) : (
                  <>
                    <Text style={styles.submitButtonText}>
                      {isLogin ? 'Sign In' : 'Create Account'}
                    </Text>
                    <Icon name="arrow-forward" size={20} color="white" />
                  </>
                )}
              </TouchableOpacity>

              {/* Switch Mode */}
              <TouchableOpacity
                style={styles.switchButton}
                onPress={() => setIsLogin(!isLogin)}>
                <Text style={styles.switchButtonText}>
                  {isLogin
                    ? "Don't have an account? "
                    : 'Already have an account? '}
                  <Text style={styles.switchButtonLink}>
                    {isLogin ? 'Sign Up' : 'Sign In'}
                  </Text>
                </Text>
              </TouchableOpacity>

              {/* Offline Mode */}
              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>OR</Text>
                <View style={styles.dividerLine} />
              </View>

              <TouchableOpacity
                style={styles.offlineButton}
                onPress={handleOfflineMode}>
                <Icon name="cloud-off" size={20} color="#64748B" />
                <Text style={styles.offlineButtonText}>Continue Offline</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Features Preview */}
          <View style={styles.featuresContainer}>
            <Text style={styles.featuresTitle}>What you can do:</Text>
            <View style={styles.featuresList}>
              <View style={styles.featureItem}>
                <Icon name="group-add" size={16} color="rgba(255,255,255,0.8)" />
                <Text style={styles.featureText}>Build competitive teams</Text>
              </View>
              <View style={styles.featureItem}>
                <Icon name="flash-on" size={16} color="rgba(255,255,255,0.8)" />
                <Text style={styles.featureText}>Battle simulation</Text>
              </View>
              <View style={styles.featureItem}>
                <Icon name="swap-horiz" size={16} color="rgba(255,255,255,0.8)" />
                <Text style={styles.featureText}>Trading system</Text>
              </View>
              <View style={styles.featureItem}>
                <Icon name="cloud-sync" size={16} color="rgba(255,255,255,0.8)" />
                <Text style={styles.featureText}>Cross-device sync</Text>
              </View>
            </View>
          </View>

          {/* Connection Status */}
          {offlineMode && (
            <View style={styles.connectionStatus}>
              <Icon name="cloud-off" size={16} color="#F59E0B" />
              <Text style={styles.connectionText}>No internet connection</Text>
            </View>
          )}
        </ScrollView>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingVertical: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    textAlign: 'center',
  },
  formContainer: {
    marginBottom: 32,
  },
  form: {
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderRadius: 20,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 16,
    paddingVertical: 4,
  },
  inputError: {
    borderColor: '#EF4444',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#1E293B',
    paddingVertical: 12,
  },
  eyeIcon: {
    padding: 4,
  },
  errorText: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 4,
    marginLeft: 4,
  },
  submitButton: {
    backgroundColor: '#3B82F6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  switchButton: {
    alignItems: 'center',
    paddingVertical: 8,
    marginBottom: 20,
  },
  switchButtonText: {
    fontSize: 14,
    color: '#64748B',
  },
  switchButtonLink: {
    color: '#3B82F6',
    fontWeight: '600',
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E2E8F0',
  },
  dividerText: {
    fontSize: 12,
    color: '#94A3B8',
    marginHorizontal: 16,
  },
  offlineButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    backgroundColor: '#F8FAFC',
  },
  offlineButtonText: {
    color: '#64748B',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
  },
  featuresContainer: {
    marginBottom: 24,
  },
  featuresTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.9)',
    marginBottom: 12,
    textAlign: 'center',
  },
  featuresList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 8,
    marginVertical: 4,
  },
  featureText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
    marginLeft: 4,
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(245, 158, 11, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'center',
  },
  connectionText: {
    fontSize: 12,
    color: '#F59E0B',
    fontWeight: '500',
    marginLeft: 4,
  },
});

export default LoginScreen;