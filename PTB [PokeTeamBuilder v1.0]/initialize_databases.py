#!/usr/bin/env python3
"""
Initialize Pokemon Team Builder databases.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Initialize all databases."""
    try:
        from src.config.game_config import DatabaseConfig, GameConfig
        
        print("🎮 Initializing Pokemon Team Builder databases...")
        DatabaseConfig.initialize_databases()
        print("✅ Databases initialized successfully!")
        
        # Verify database files were created
        if GameConfig.POKEMON_DATABASE.exists():
            print(f"✅ Pokemon database created: {GameConfig.POKEMON_DATABASE}")
        
        if GameConfig.MOVES_DATABASE.exists():
            print(f"✅ Moves database created: {GameConfig.MOVES_DATABASE}")
        
        if GameConfig.ABILITIES_DATABASE.exists():
            print(f"✅ Abilities database created: {GameConfig.ABILITIES_DATABASE}")
        
        print("🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())