/**
 * CustomInput Component
 * Enhanced text input with validation and styling
 */

import React, {useState, useRef} from 'react';
import {
  View,
  TextInput,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const CustomInput = ({
  label,
  value = '',
  onChangeText,
  placeholder,
  error,
  disabled = false,
  secureTextEntry = false,
  keyboardType = 'default',
  multiline = false,
  numberOfLines = 1,
  maxLength,
  leftIcon,
  rightIcon,
  onRightIconPress,
  showPasswordToggle = false,
  required = false,
  style = {},
  inputStyle = {},
  labelStyle = {},
  containerStyle = {},
  validate,
  onBlur,
  onFocus,
  autoCapitalize = 'sentences',
  autoCorrect = true,
  returnKeyType = 'done',
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(!secureTextEntry);
  const [validationError, setValidationError] = useState('');
  
  const animatedValue = useRef(new Animated.Value(value ? 1 : 0)).current;
  const inputRef = useRef(null);

  const handleFocus = (e) => {
    setIsFocused(true);
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 200,
      useNativeDriver: false,
    }).start();
    onFocus?.(e);
  };

  const handleBlur = (e) => {
    setIsFocused(false);
    if (!value) {
      Animated.timing(animatedValue, {
        toValue: 0,
        duration: 200,
        useNativeDriver: false,
      }).start();
    }
    
    // Run validation
    if (validate && value) {
      const validationResult = validate(value);
      if (validationResult !== true) {
        setValidationError(validationResult);
      } else {
        setValidationError('');
      }
    }
    
    onBlur?.(e);
  };

  const handleChangeText = (text) => {
    onChangeText?.(text);
    // Clear validation error when user starts typing
    if (validationError) {
      setValidationError('');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const labelTop = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [20, 0],
  });

  const labelScale = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 0.8],
  });

  const labelColor = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: ['#9CA3AF', isFocused ? '#3B82F6' : '#6B7280'],
  });

  const borderColor = error || validationError
    ? '#EF4444'
    : isFocused
    ? '#3B82F6'
    : '#D1D5DB';

  const displayError = error || validationError;

  return (
    <View style={[styles.container, containerStyle]}>
      {/* Floating Label */}
      {label && (
        <Animated.Text
          style={[
            styles.label,
            labelStyle,
            {
              top: labelTop,
              transform: [{scale: labelScale}],
              color: labelColor,
            },
          ]}>
          {label}
          {required && <Text style={styles.required}> *</Text>}
        </Animated.Text>
      )}

      {/* Input Container */}
      <View
        style={[
          styles.inputContainer,
          {borderColor},
          disabled && styles.disabled,
          multiline && styles.multilineContainer,
          style,
        ]}>
        
        {/* Left Icon */}
        {leftIcon && (
          <Icon
            name={leftIcon}
            size={20}
            color={isFocused ? '#3B82F6' : '#6B7280'}
            style={styles.leftIcon}
          />
        )}

        {/* Text Input */}
        <TextInput
          ref={inputRef}
          style={[
            styles.input,
            multiline && styles.multilineInput,
            inputStyle,
          ]}
          value={value}
          onChangeText={handleChangeText}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={isFocused || !label ? placeholder : ''}
          placeholderTextColor="#9CA3AF"
          secureTextEntry={secureTextEntry && !showPassword}
          keyboardType={keyboardType}
          multiline={multiline}
          numberOfLines={numberOfLines}
          maxLength={maxLength}
          editable={!disabled}
          autoCapitalize={autoCapitalize}
          autoCorrect={autoCorrect}
          returnKeyType={returnKeyType}
          {...props}
        />

        {/* Right Icons */}
        <View style={styles.rightIconsContainer}>
          {/* Password Toggle */}
          {showPasswordToggle && secureTextEntry && (
            <TouchableOpacity
              onPress={togglePasswordVisibility}
              style={styles.iconButton}>
              <Icon
                name={showPassword ? 'visibility-off' : 'visibility'}
                size={20}
                color="#6B7280"
              />
            </TouchableOpacity>
          )}

          {/* Custom Right Icon */}
          {rightIcon && (
            <TouchableOpacity
              onPress={onRightIconPress}
              style={styles.iconButton}>
              <Icon
                name={rightIcon}
                size={20}
                color={isFocused ? '#3B82F6' : '#6B7280'}
              />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Character Count */}
      {maxLength && (
        <Text style={styles.characterCount}>
          {value.length}/{maxLength}
        </Text>
      )}

      {/* Error Message */}
      {displayError && (
        <Text style={styles.errorText}>
          {displayError}
        </Text>
      )}
    </View>
  );
};

// Specialized Input Components
export const PasswordInput = (props) => (
  <CustomInput
    {...props}
    secureTextEntry={true}
    showPasswordToggle={true}
    autoCapitalize="none"
    autoCorrect={false}
  />
);

export const EmailInput = (props) => (
  <CustomInput
    {...props}
    keyboardType="email-address"
    autoCapitalize="none"
    autoCorrect={false}
    validate={(email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email) || 'Please enter a valid email address';
    }}
  />
);

export const NumberInput = (props) => (
  <CustomInput
    {...props}
    keyboardType="numeric"
    validate={(value) => {
      const num = parseFloat(value);
      return !isNaN(num) || 'Please enter a valid number';
    }}
  />
);

const styles = StyleSheet.create({
  container: {
    marginBottom: 20,
  },
  label: {
    position: 'absolute',
    left: 12,
    zIndex: 1,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 4,
    fontSize: 16,
    fontWeight: '500',
  },
  required: {
    color: '#EF4444',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 12,
    paddingVertical: 16,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  multilineContainer: {
    alignItems: 'flex-start',
    paddingVertical: 12,
  },
  disabled: {
    backgroundColor: '#F9FAFB',
    opacity: 0.6,
  },
  leftIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#1F2937',
    paddingVertical: 0,
  },
  multilineInput: {
    textAlignVertical: 'top',
    paddingTop: 4,
  },
  rightIconsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconButton: {
    padding: 4,
    marginLeft: 8,
  },
  characterCount: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'right',
    marginTop: 4,
  },
  errorText: {
    fontSize: 14,
    color: '#EF4444',
    marginTop: 4,
  },
});

export default CustomInput;