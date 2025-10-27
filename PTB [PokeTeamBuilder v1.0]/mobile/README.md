# 📱 Pokemon Team Builder Mobile App

A comprehensive React Native mobile application for building and managing Pokemon teams across different game formats.

## ✨ Features

### 🎯 Core Features
- **Team Building**: Create and customize Pokemon teams with full stat management
- **Battle Simulation**: Real-time battle simulator with AI opponents
- **Breeding Calculator**: Advanced breeding mechanics and genetics calculator  
- **Trading Hub**: Cross-platform trading with Nintendo consoles
- **Profile Management**: User statistics, achievements, and preferences
- **Offline Mode**: Full functionality without internet connection

### 🏆 Advanced Features
- **Multiple Battle Formats**: Singles, Doubles, VGC, OU, UU, RU, NU
- **AI Trainers**: Various difficulty levels and battle strategies
- **Tournament System**: Create and participate in tournaments
- **Team Analysis**: Type coverage, stat distribution, and weakness analysis
- **Multiplayer**: Real-time battles with other trainers
- **Save File Import**: Import teams from Pokemon games

### 🎨 UI/UX Polish
- **Modern Design**: Material Design 3 principles with Pokemon theming
- **Smooth Animations**: 60fps animations and micro-interactions
- **Responsive Layout**: Optimized for phones and tablets
- **Dark/Light Mode**: Automatic theme switching
- **Accessibility**: Full screen reader and keyboard navigation support

## Installation

### Prerequisites
- Node.js 18+ 
- React Native CLI
- Xcode (for iOS development)
- Android Studio (for Android development)

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd mobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **iOS Setup**
   ```bash
   cd ios && pod install && cd ..
   ```

4. **Android Setup**
   - Ensure Android SDK is installed
   - Create virtual device or connect physical device

5. **Start Metro Bundler**
   ```bash
   npx react-native start
   ```

6. **Run the application**
   ```bash
   # iOS
   npx react-native run-ios
   
   # Android
   npx react-native run-android
   ```

## Project Structure

```
mobile/
├── src/
│   ├── components/        # Reusable UI components
│   ├── screens/          # Application screens
│   ├── services/         # API and data services
│   ├── context/          # React Context providers
│   ├── utils/            # Utility functions
│   └── App.js            # Main application component
├── android/              # Android-specific configurations
├── ios/                  # iOS-specific configurations
├── assets/               # Images and static assets
└── package.json          # Dependencies and scripts
```

## Key Dependencies

### Navigation & UI
- `@react-navigation/native` - Navigation framework
- `@react-navigation/bottom-tabs` - Bottom tab navigation
- `@react-navigation/stack` - Stack navigation
- `react-native-vector-icons` - Icon library
- `react-native-linear-gradient` - Gradient components

### Data & Storage
- `@react-native-async-storage/async-storage` - Local storage
- `axios` - HTTP client for API calls
- `socket.io-client` - Real-time communication

### Platform Integration
- `react-native-permissions` - Device permissions
- `@react-native-community/netinfo` - Network status
- `react-native-device-info` - Device information

## Configuration

### API Integration
Configure the API endpoint in `src/services/ApiService.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Offline Mode
The app automatically detects network status and switches to offline mode when needed. All data is cached locally and synchronized when connection is restored.

## Building for Production

### Android APK
```bash
cd android
./gradlew assembleRelease
```

### iOS Archive
```bash
cd ios
xcodebuild -workspace PokemonTeamBuilder.xcworkspace -scheme PokemonTeamBuilder archive
```

## Features in Detail

### Team Builder
- Pokemon selection from comprehensive database
- Team format support (Singles, Doubles, VGC, etc.)
- Move, ability, and item customization
- EV/IV training interface
- Team analysis and optimization

### Battle System
- AI battle simulation
- Multiple difficulty levels
- Battle history tracking
- Damage calculation engine
- Type effectiveness system

### Trading Hub
- Cross-platform trading support
- Trade request system
- Real-time messaging
- Trade history and ratings
- Security verification

### Breeding Calculator
- Compatibility checking
- IV inheritance calculation
- Egg move prediction
- Nature inheritance
- Breeding time estimation

## Development

### Running Tests
```bash
npm test
```

### Code Style
The project uses ESLint and Prettier for code formatting:
```bash
npm run lint
npm run format
```

### Debugging
- Enable React Native Debugger
- Use Flipper for advanced debugging
- Check Metro bundler logs for build issues

## Deployment

### App Store (iOS)
1. Archive the app in Xcode
2. Upload to App Store Connect
3. Submit for review

### Google Play Store (Android)
1. Generate signed APK
2. Upload to Google Play Console
3. Submit for review

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and support:
- Check the troubleshooting guide
- Review existing GitHub issues
- Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- Core team building functionality
- Battle simulation system
- Trading hub integration
- Breeding calculator
- Offline support with sync
- Cross-platform compatibility

---

**Pokemon Team Builder Mobile** - Build, Battle, Trade, and Breed Pokemon like never before!