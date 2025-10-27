/**
 * Metro Configuration for Optimized Bundling
 * Enhanced with performance optimizations and custom resolvers
 */

const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');
const {
  resolver: {assetExts, sourceExts},
} = getDefaultConfig(__dirname);

/**
 * Metro configuration object
 * @type {import('metro-config').MetroConfig}
 */
const config = {
  // Transform configuration
  transformer: {
    // Enable inline requires for performance
    inlineRequires: true,
    
    // Asset registry path for custom assets
    assetRegistryPath: 'react-native/Libraries/Image/AssetRegistry',
    
    // Enable minification in production
    minifierConfig: {
      mangle: {
        keep_fnames: true,
      },
      output: {
        ascii_only: true,
        quote_style: 3,
        wrap_iife: true,
      },
      sourceMap: {
        includeSources: false,
      },
      toplevel: false,
      warnings: false,
      ie8: false,
      keep_fnames: true,
    },
    
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },
  
  // Resolver configuration
  resolver: {
    // Asset extensions (images, fonts, etc.)
    assetExts: [...assetExts, 'bin', 'txt', 'jpg', 'png', 'json', 'svg'],
    
    // Source extensions (JavaScript, TypeScript, etc.)
    sourceExts: [...sourceExts, 'js', 'json', 'ts', 'tsx', 'jsx'],
    
    // Platform extensions
    platforms: ['ios', 'android', 'native', 'web'],
    
    // Node modules to include in bundling
    nodeModulesPaths: [
      './node_modules',
      '../node_modules',
    ],
    
    // Custom resolvers for better performance
    resolverMainFields: ['react-native', 'browser', 'main'],
    
    // Disable symlink resolution for faster builds
    useWatchman: true,
    
    // Custom asset resolution
    assetResolutions: ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi'],
  },
  
  // Server configuration
  server: {
    // Port for Metro bundler
    port: 8081,
    
    // Enable HTTPS for development (optional)
    useGlobalHotkey: true,
    
    // Enhance logs
    enhanceLogs: true,
  },
  
  // Watcher configuration for file changes
  watchFolders: [
    // Add additional folders to watch
    './src',
    './assets',
  ],
  
  // Reset Metro cache for consistent builds
  resetCache: true,
  
  // Exclude unnecessary files from bundling
  blacklistRE: /\/(build|\.git|node_modules\/.*\/node_modules)\/.*/,
  
  // Serializer configuration
  serializer: {
    // Custom serializers for specific file types
    getModulesRunBeforeMainModule: () => [
      require.resolve('react-native/Libraries/Core/InitializeCore'),
    ],
    
    // Process module filter for excluding unnecessary modules
    processModuleFilter: (module) => {
      // Exclude test files from production bundles
      if (module.path.includes('__tests__') || 
          module.path.includes('.test.') ||
          module.path.includes('.spec.')) {
        return false;
      }
      return true;
    },
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);