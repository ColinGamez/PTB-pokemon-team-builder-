# Pokemon Team Builder (PTB) v1.0

A comprehensive Pokemon team building and trading platform supporting games from GameCube era through modern Switch titles.

## Features

### Game Support
- **GameCube**: Pokemon Colosseum, XD: Gale of Darkness, Pokemon Box
- **Wii**: Pokemon Battle Revolution, Pokemon Ranch
- **DS**: Diamond/Pearl/Platinum, HeartGold/SoulSilver, Black/White, Black2/White2
- **3DS**: X/Y, Omega Ruby/Alpha Sapphire, Sun/Moon, Ultra Sun/Ultra Moon
- **Switch**: Let's Go Pikachu/Eevee, Sword/Shield, BDSP, Legends Arceus, Scarlet/Violet

### Core Features
- Advanced team builder with game-specific mechanics
- Shadow Pokemon system (GameCube era)
- Pokemon legality validation
- Multiple trading method support
- Comprehensive Pokemon database
- Battle simulator integration
- Social Community Hub with user profiles and team sharing
- Tournament management system
- Admin Panel for user and content management

### Trading Methods
- Local trading
- WiFi trading (older games)
- GTS/Wonder Trade
- Link Trade bots (Switch era)
- Shadow Pokemon transfer (GameCube)

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize databases: `python initialize_databases.py`
4. (Optional) Initialize social database: `python initialize_social_database.py`
5. Run the GUI application: `python run_gui.py`

### Backend Server (for Email Verification)

The backend server handles user registration and email verification:

1. **Quick Start (Demo Mode)**
   ```bash
   python start_backend.py
   ```
   - Emails saved to `logs/email_verifications.txt`
   - No SMTP configuration needed

2. **Production Setup (Real Emails)**
   ```bash
   # Copy configuration template
   copy .env.example .env
   
   # Edit .env with your SMTP credentials
   notepad .env
   
   # Start server
   python start_backend.py
   ```

3. **Windows Easy Start**
   ```bash
   start_backend.bat
   ```

See [BACKEND_README.md](BACKEND_README.md) for detailed backend documentation.

## Project Structure

```
PTB/
├── src/
│   ├── core/           # Core Pokemon classes and mechanics
│   ├── games/          # Game-specific implementations
│   ├── ui/             # User interface components
│   ├── trading/        # Trading system implementations
│   └── data/           # Pokemon database and game data
├── tests/              # Unit tests
├── docs/               # Documentation
└── main.py             # Main application entry point
```

## Development Status

Currently building GameCube era foundation with Shadow Pokemon mechanics.

## Admin Panel

The Admin Panel provides comprehensive tools for managing the platform:

**Access:** Click "🔒 Admin Panel" button in the main application

**Admin PIN:** `050270` (⚠️ Keep secure!)

**Features:**
- 📊 Dashboard with system statistics
- 👥 User management (search, verify, delete, ban)
- 📝 Content moderation
- 📈 Detailed analytics
- 💾 Database backup and maintenance
- ⚙️ System settings and configuration

**Documentation:**
- [ADMIN_PANEL_GUIDE.md](ADMIN_PANEL_GUIDE.md) - Complete admin documentation
- [ADMIN_QUICK_REFERENCE.md](ADMIN_QUICK_REFERENCE.md) - Quick reference guide

**Security:** See ADMIN_PANEL_GUIDE.md for PIN security and production deployment.
