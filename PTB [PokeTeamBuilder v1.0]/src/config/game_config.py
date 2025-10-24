"""
Game configuration and constants for Pokemon Team Builder.
Centralizes all game-specific data and settings.
"""

import os
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path

# Base directory for data files
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

class GameConfig:
    """Centralized game configuration and constants."""
    
    # Database paths
    POKEMON_DATABASE = DATA_DIR / "pokemon.json"
    MOVES_DATABASE = DATA_DIR / "moves.json"
    ABILITIES_DATABASE = DATA_DIR / "abilities.json"
    TYPES_DATABASE = DATA_DIR / "types.json"
    
    # Type effectiveness chart (comprehensive)
    TYPE_EFFECTIVENESS_CHART = {
        'normal': {
            'rock': 0.5, 'ghost': 0.0, 'steel': 0.5
        },
        'fire': {
            'fire': 0.5, 'water': 0.5, 'grass': 2.0, 'ice': 2.0, 
            'bug': 2.0, 'rock': 0.5, 'dragon': 0.5, 'steel': 2.0
        },
        'water': {
            'fire': 2.0, 'water': 0.5, 'grass': 0.5, 'ground': 2.0, 
            'rock': 2.0, 'dragon': 0.5
        },
        'grass': {
            'fire': 0.5, 'water': 2.0, 'grass': 0.5, 'poison': 0.5, 
            'flying': 0.5, 'bug': 0.5, 'rock': 2.0, 'ground': 2.0, 
            'dragon': 0.5, 'steel': 0.5
        },
        'electric': {
            'water': 2.0, 'grass': 0.5, 'ground': 0.0, 'flying': 2.0, 
            'dragon': 0.5, 'electric': 0.5
        },
        'ice': {
            'fire': 0.5, 'water': 0.5, 'grass': 2.0, 'ice': 0.5, 
            'ground': 2.0, 'flying': 2.0, 'dragon': 2.0, 'steel': 0.5
        },
        'fighting': {
            'normal': 2.0, 'ice': 2.0, 'poison': 0.5, 'flying': 0.5, 
            'psichic': 0.5, 'bug': 0.5, 'rock': 2.0, 'ghost': 0.0, 
            'dark': 2.0, 'steel': 2.0, 'fairy': 0.5
        },
        'poison': {
            'grass': 2.0, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 
            'ghost': 0.5, 'steel': 0.0, 'fairy': 2.0
        },
        'ground': {
            'fire': 2.0, 'grass': 0.5, 'electric': 2.0, 'poison': 2.0, 
            'flying': 0.0, 'bug': 0.5, 'rock': 2.0, 'steel': 2.0
        },
        'flying': {
            'electric': 0.5, 'grass': 2.0, 'ice': 0.5, 'fighting': 2.0, 
            'bug': 2.0, 'rock': 0.5, 'steel': 0.5
        },
        'psychic': {
            'fighting': 2.0, 'poison': 2.0, 'psychic': 0.5, 'dark': 0.0, 
            'steel': 0.5
        },
        'bug': {
            'fire': 0.5, 'grass': 2.0, 'fighting': 0.5, 'poison': 0.5, 
            'flying': 0.5, 'psychic': 2.0, 'ghost': 0.5, 'dark': 2.0, 
            'steel': 0.5, 'fairy': 0.5
        },
        'rock': {
            'fire': 2.0, 'ice': 2.0, 'fighting': 0.5, 'ground': 0.5, 
            'flying': 2.0, 'bug': 2.0, 'steel': 0.5
        },
        'ghost': {
            'normal': 0.0, 'psychic': 2.0, 'ghost': 2.0, 'dark': 0.5
        },
        'dragon': {
            'dragon': 2.0, 'steel': 0.5, 'fairy': 0.0
        },
        'dark': {
            'fighting': 0.5, 'psychic': 2.0, 'ghost': 2.0, 'dark': 0.5, 
            'fairy': 0.5
        },
        'steel': {
            'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'ice': 2.0, 
            'rock': 2.0, 'steel': 0.5, 'fairy': 2.0
        },
        'fairy': {
            'fire': 0.5, 'fighting': 2.0, 'poison': 0.5, 'dragon': 2.0, 
            'dark': 2.0, 'steel': 0.5
        },
        'shadow': {
            'normal': 1.5, 'psychic': 2.0, 'ghost': 1.5, 'dark': 0.5, 
            'shadow': 0.5
        }
    }
    
    # Battle constants
    CRITICAL_HIT_CHANCE = 0.0625  # 6.25%
    STAB_MULTIPLIER = 1.5
    MAX_POKEMON_LEVEL = 100
    MIN_POKEMON_LEVEL = 1
    MAX_EV_TOTAL = 510
    MAX_EV_SINGLE = 255
    MAX_IV_VALUE = 31
    MIN_IV_VALUE = 0
    
    # Weather multipliers
    WEATHER_MULTIPLIERS = {
        'sunny': {'fire': 1.5, 'water': 0.5},
        'rainy': {'water': 1.5, 'fire': 0.5},
        'sandstorm': {'rock': 1.5},
        'hail': {'ice': 1.5}
    }
    
    # Terrain multipliers
    TERRAIN_MULTIPLIERS = {
        'electric': {'electric': 1.3},
        'grassy': {'grass': 1.3},
        'misty': {'dragon': 0.5},
        'psychic': {'psychic': 1.3}
    }
    
    # Era-specific features
    ERA_FEATURES = {
        'gamecube': {
            'shadow_pokemon': True,
            'max_pokemon_id': 386,
            'formats': ['single', 'double'],
            'special_mechanics': ['Shadow Pokemon', 'Purification']
        },
        'wii': {
            'shadow_pokemon': False,
            'max_pokemon_id': 493,
            'formats': ['single', 'double'],
            'special_mechanics': ['WiFi Battles', 'Battle Revolution']
        },
        'ds': {
            'shadow_pokemon': False,
            'max_pokemon_id': 649,
            'formats': ['single', 'double', 'triple', 'rotation'],
            'special_mechanics': ['Physical/Special Split', 'Hidden Abilities']
        },
        'switch': {
            'shadow_pokemon': False,
            'max_pokemon_id': 1008,
            'formats': ['single', 'double'],
            'special_mechanics': ['Dynamax', 'Terastallization']
        }
    }
    
    @classmethod
    def get_type_effectiveness(cls, attack_type: str, defend_type: str) -> float:
        """Get type effectiveness from centralized chart."""
        attack_lower = attack_type.lower()
        defend_lower = defend_type.lower()
        
        if attack_lower in cls.TYPE_EFFECTIVENESS_CHART:
            return cls.TYPE_EFFECTIVENESS_CHART[attack_lower].get(defend_lower, 1.0)
        
        return 1.0
    
    @classmethod
    def get_era_features(cls, era: str) -> Dict[str, Any]:
        """Get features for a specific era."""
        return cls.ERA_FEATURES.get(era.lower(), {})
    
    @classmethod
    def ensure_data_directories(cls):
        """Ensure all data directories exist."""
        DATA_DIR.mkdir(exist_ok=True)
        CONFIG_DIR.mkdir(exist_ok=True)

class LoggingConfig:
    """Logging configuration."""
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = BASE_DIR / "logs" / "ptb.log"
    
    @classmethod
    def setup_logging(cls):
        """Setup logging configuration."""
        import logging
        from pathlib import Path
        
        # Create logs directory
        cls.LOG_FILE.parent.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )

class DatabaseConfig:
    """Database configuration and initialization."""
    
    @classmethod
    def initialize_databases(cls):
        """Initialize all databases with default data."""
        GameConfig.ensure_data_directories()
        
        # Initialize Pokemon database
        if not GameConfig.POKEMON_DATABASE.exists():
            cls._create_pokemon_database()
            
        # Initialize moves database
        if not GameConfig.MOVES_DATABASE.exists():
            cls._create_moves_database()
            
        # Initialize abilities database
        if not GameConfig.ABILITIES_DATABASE.exists():
            cls._create_abilities_database()
    
    @classmethod
    def _create_pokemon_database(cls):
        """Create basic Pokemon database."""
        pokemon_data = {
            "1": {
                "name": "Bulbasaur",
                "types": ["grass", "poison"],
                "base_stats": {"hp": 45, "attack": 49, "defense": 49, "special_attack": 65, "special_defense": 65, "speed": 45},
                "abilities": ["Overgrow", "Chlorophyll"],
                "moves": ["Tackle", "Growl", "Vine Whip", "Poison Powder", "Sleep Powder", "Razor Leaf", "Solar Beam"]
            },
            "4": {
                "name": "Charmander",
                "types": ["fire"],
                "base_stats": {"hp": 39, "attack": 52, "defense": 43, "special_attack": 60, "special_defense": 50, "speed": 65},
                "abilities": ["Blaze", "Solar Power"],
                "moves": ["Scratch", "Growl", "Ember", "Fire Fang", "Flame Wheel", "Fire Blast", "Dragon Claw"]
            },
            "7": {
                "name": "Squirtle",
                "types": ["water"],
                "base_stats": {"hp": 44, "attack": 48, "defense": 65, "special_attack": 50, "special_defense": 64, "speed": 43},
                "abilities": ["Torrent", "Rain Dish"],
                "moves": ["Tackle", "Tail Whip", "Water Gun", "Bubble", "Surf", "Ice Beam", "Hydro Pump"]
            },
            "25": {
                "name": "Pikachu",
                "types": ["electric"],
                "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special_attack": 50, "special_defense": 50, "speed": 90},
                "abilities": ["Static", "Lightning Rod"],
                "moves": ["Thunder Shock", "Tail Whip", "Thunder Wave", "Quick Attack", "Thunder", "Thunderbolt", "Agility"]
            }
        }
        
        with open(GameConfig.POKEMON_DATABASE, 'w') as f:
            json.dump(pokemon_data, f, indent=2)
    
    @classmethod
    def _create_moves_database(cls):
        """Create basic moves database."""
        moves_data = {
            "Tackle": {
                "type": "normal",
                "category": "physical",
                "power": 40,
                "accuracy": 100,
                "pp": 35,
                "description": "A physical attack in which the user charges and slams into the target."
            },
            "Thunder Shock": {
                "type": "electric",
                "category": "special",
                "power": 40,
                "accuracy": 100,
                "pp": 30,
                "description": "A jolt of electricity crashes down on the target."
            },
            "Shadow Rush": {
                "type": "shadow",
                "category": "physical",
                "power": 55,
                "accuracy": 100,
                "pp": 20,
                "description": "A shadow move that may cause the target to flinch.",
                "is_shadow_move": True,
                "game_era": "gamecube"
            },
            "Fire Blast": {
                "type": "fire",
                "category": "special",
                "power": 110,
                "accuracy": 85,
                "pp": 5,
                "description": "The target is attacked with an intense blast of all-consuming fire."
            },
            "Surf": {
                "type": "water",
                "category": "special",
                "power": 90,
                "accuracy": 100,
                "pp": 15,
                "description": "The user attacks everything around it by swamping its surroundings with a giant wave."
            }
        }
        
        with open(GameConfig.MOVES_DATABASE, 'w') as f:
            json.dump(moves_data, f, indent=2)
    
    @classmethod
    def _create_abilities_database(cls):
        """Create basic abilities database."""
        abilities_data = {
            "Overgrow": {
                "description": "Powers up Grass-type moves when the Pokemon's HP is low.",
                "category": "moves",
                "trigger": "hp_low"
            },
            "Blaze": {
                "description": "Powers up Fire-type moves when the Pokemon's HP is low.",
                "category": "moves",
                "trigger": "hp_low"
            },
            "Torrent": {
                "description": "Powers up Water-type moves when the Pokemon's HP is low.",
                "category": "moves",
                "trigger": "hp_low"
            },
            "Static": {
                "description": "The Pokemon may cause paralysis when it's hit by a physical move.",
                "category": "status",
                "trigger": "physical_contact"
            },
            "Shadow Boost": {
                "description": "Increases the power of Shadow moves by 50%.",
                "category": "moves",
                "game_era": "gamecube",
                "is_gamecube_specific": True
            }
        }
        
        with open(GameConfig.ABILITIES_DATABASE, 'w') as f:
            json.dump(abilities_data, f, indent=2)

# Initialize configuration on import
GameConfig.ensure_data_directories()
LoggingConfig.setup_logging()