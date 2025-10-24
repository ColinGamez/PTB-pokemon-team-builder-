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

### Trading Methods
- Local trading
- WiFi trading (older games)
- GTS/Wonder Trade
- Link Trade bots (Switch era)
- Shadow Pokemon transfer (GameCube)

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run the main application: `python main.py`

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
