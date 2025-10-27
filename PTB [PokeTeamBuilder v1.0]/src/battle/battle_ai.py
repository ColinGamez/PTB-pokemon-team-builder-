"""
Battle AI system for Pokemon Team Builder.
Provides AI opponents with different difficulty levels and strategies.
"""

import random
import logging
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from enum import Enum

from ..core.pokemon import Pokemon, PokemonNature, PokemonStats, PokemonEV, PokemonIV
from ..teambuilder.team import PokemonTeam, TeamEra, TeamFormat
from ..battle.battle_engine import BattleEngine
from ..battle.battle_state import BattleState, PokemonBattleState

logger = logging.getLogger(__name__)

class AIPersonality(Enum):
    """AI personality types affecting battle decisions."""
    AGGRESSIVE = "aggressive"      # Prefers offensive moves
    DEFENSIVE = "defensive"        # Prefers defensive moves
    BALANCED = "balanced"          # Balanced strategy
    RANDOM = "random"             # Random decisions
    SMART = "smart"               # Analyzes type effectiveness
    GAMECUBE_SHADOW = "gamecube_shadow"  # GameCube era with shadow Pokemon

class AIDifficulty(Enum):
    """AI difficulty levels."""
    BEGINNER = "beginner"         # Simple strategies, some mistakes
    INTERMEDIATE = "intermediate"  # Good strategies, occasional mistakes
    ADVANCED = "advanced"         # Strong strategies, rare mistakes
    EXPERT = "expert"             # Optimal strategies, no mistakes

class BattleAI:
    """AI opponent for Pokemon battles."""
    
    def __init__(
        self,
        name: str,
        difficulty: AIDifficulty = AIDifficulty.INTERMEDIATE,
        personality: AIPersonality = AIPersonality.BALANCED,
        team: Optional[PokemonTeam] = None,
        description: str = ""
    ):
        self.name = name
        self.difficulty = difficulty
        self.personality = personality
        self.team = team or self._generate_team()
        self.battle_history = []
        self.description = description
        
        logger.info(f"Created AI opponent: {name} ({difficulty.value}, {personality.value})")
    
    def _generate_team(self) -> PokemonTeam:
        """Generate a team based on AI personality and difficulty."""
        # All imports handled at top of file
        
        # Create team
        team = PokemonTeam(
            name=f"{self.name}'s Team",
            format=TeamFormat.SINGLE,
            era=TeamEra.SWITCH,
            description=f"AI team with {self.personality.value} strategy"
        )
        
        # Generate Pokemon based on difficulty and personality
        pokemon_data = self._get_pokemon_pool()
        selected_pokemon = random.sample(pokemon_data, min(6, len(pokemon_data)))
        
        for pokemon_info in selected_pokemon:
            # Generate stats based on difficulty
            evs, ivs = self._generate_stats_for_difficulty()
            
            # Create Pokemon
            pokemon = Pokemon(
                name=pokemon_info['name'],
                species_id=pokemon_info['id'],
                level=self._get_level_for_difficulty(),
                nature=self._select_nature(pokemon_info),
                base_stats=PokemonStats(**pokemon_info['base_stats']),
                evs=evs,
                ivs=ivs,
                moves=self._select_moves(pokemon_info),
                ability=random.choice(pokemon_info.get('abilities', ['Unknown']))
            )
            
            team.add_pokemon(pokemon, item=self._select_item())
        
        logger.info(f"Generated AI team with {team.get_team_size()} Pokemon")
        return team
    
    def _get_pokemon_pool(self) -> List[Dict[str, Any]]:
        """Get Pokemon pool based on personality."""
        # Simplified Pokemon data - in real implementation would come from database
        all_pokemon = [
            {
                'name': 'Charizard', 'id': 6,
                'base_stats': {'hp': 78, 'attack': 84, 'defense': 78, 'special_attack': 109, 'special_defense': 85, 'speed': 100},
                'types': ['fire', 'flying'],
                'abilities': ['Blaze', 'Solar Power'],
                'moves': ['Fire Blast', 'Air Slash', 'Dragon Pulse', 'Solar Beam']
            },
            {
                'name': 'Blastoise', 'id': 9,
                'base_stats': {'hp': 79, 'attack': 83, 'defense': 100, 'special_attack': 85, 'special_defense': 105, 'speed': 78},
                'types': ['water'],
                'abilities': ['Torrent', 'Rain Dish'],
                'moves': ['Surf', 'Ice Beam', 'Earthquake', 'Focus Blast']
            },
            {
                'name': 'Venusaur', 'id': 3,
                'base_stats': {'hp': 80, 'attack': 82, 'defense': 83, 'special_attack': 100, 'special_defense': 100, 'speed': 80},
                'types': ['grass', 'poison'],
                'abilities': ['Overgrow', 'Chlorophyll'],
                'moves': ['Solar Beam', 'Sludge Bomb', 'Earthquake', 'Sleep Powder']
            },
            {
                'name': 'Alakazam', 'id': 65,
                'base_stats': {'hp': 55, 'attack': 50, 'defense': 45, 'special_attack': 135, 'special_defense': 95, 'speed': 120},
                'types': ['psychic'],
                'abilities': ['Synchronize', 'Inner Focus'],
                'moves': ['Psychic', 'Shadow Ball', 'Focus Blast', 'Thunder Wave']
            },
            {
                'name': 'Machamp', 'id': 68,
                'base_stats': {'hp': 90, 'attack': 130, 'defense': 80, 'special_attack': 65, 'special_defense': 85, 'speed': 55},
                'types': ['fighting'],
                'abilities': ['Guts', 'No Guard'],
                'moves': ['Close Combat', 'Stone Edge', 'Earthquake', 'Ice Punch']
            },
            {
                'name': 'Gengar', 'id': 94,
                'base_stats': {'hp': 60, 'attack': 65, 'defense': 60, 'special_attack': 130, 'special_defense': 75, 'speed': 110},
                'types': ['ghost', 'poison'],
                'abilities': ['Cursed Body', 'Levitate'],
                'moves': ['Shadow Ball', 'Sludge Bomb', 'Thunderbolt', 'Focus Blast']
            }
        ]
        
        # Filter based on personality
        if self.personality == AIPersonality.AGGRESSIVE:
            return [p for p in all_pokemon if p['base_stats']['attack'] > 100 or p['base_stats']['special_attack'] > 100]
        elif self.personality == AIPersonality.DEFENSIVE:
            return [p for p in all_pokemon if p['base_stats']['defense'] > 80 or p['base_stats']['special_defense'] > 80]
        else:
            return all_pokemon
    
    def _generate_stats_for_difficulty(self) -> Tuple[PokemonEV, PokemonIV]:
        """Generate EVs and IVs based on AI difficulty."""
        
        if self.difficulty == AIDifficulty.BEGINNER:
            # Random EVs, imperfect IVs
            ev_total = random.randint(200, 400)
            evs = PokemonEV(
                attack=random.randint(0, min(252, ev_total//2)),
                speed=random.randint(0, min(252, ev_total//2)),
                hp=random.randint(0, min(252, ev_total//4))
            )
            ivs = PokemonIV(
                hp=random.randint(15, 31),
                attack=random.randint(15, 31),
                defense=random.randint(15, 31),
                special_attack=random.randint(15, 31),
                special_defense=random.randint(15, 31),
                speed=random.randint(15, 31)
            )
        
        elif self.difficulty == AIDifficulty.INTERMEDIATE:
            # Decent EVs, good IVs
            evs = PokemonEV(attack=252, speed=252, hp=6)
            ivs = PokemonIV(
                hp=random.randint(25, 31),
                attack=random.randint(25, 31),
                defense=random.randint(20, 31),
                special_attack=random.randint(25, 31),
                special_defense=random.randint(20, 31),
                speed=random.randint(25, 31)
            )
        
        else:  # ADVANCED or EXPERT
            # Optimal EVs and IVs
            evs = PokemonEV(attack=252, speed=252, hp=6)
            ivs = PokemonIV(hp=31, attack=31, defense=31, special_attack=31, special_defense=31, speed=31)
        
        return evs, ivs
    
    def _get_level_for_difficulty(self) -> int:
        """Get Pokemon level based on difficulty."""
        if self.difficulty == AIDifficulty.BEGINNER:
            return random.randint(40, 60)
        elif self.difficulty == AIDifficulty.INTERMEDIATE:
            return random.randint(60, 80)
        else:
            return random.randint(80, 100)
    
    def _select_nature(self, pokemon_info: Dict[str, Any]) -> 'PokemonNature':
        """Select nature based on Pokemon and difficulty."""
        from ..core.pokemon import PokemonNature
        
        if self.difficulty == AIDifficulty.BEGINNER:
            return random.choice(list(PokemonNature))
        
        # Select beneficial nature based on stats
        base_stats = pokemon_info['base_stats']
        
        if base_stats['attack'] > base_stats['special_attack']:
            # Physical attacker
            return random.choice([PokemonNature.ADAMANT, PokemonNature.JOLLY])
        else:
            # Special attacker
            return random.choice([PokemonNature.MODEST, PokemonNature.TIMID])
    
    def _select_moves(self, pokemon_info: Dict[str, Any]) -> List[str]:
        """Select moves for Pokemon."""
        available_moves = pokemon_info.get('moves', ['Tackle', 'Growl'])
        
        if self.difficulty == AIDifficulty.BEGINNER:
            return random.sample(available_moves, min(4, len(available_moves)))
        else:
            # Select the best moves available
            return available_moves[:4]
    
    def _select_item(self) -> Optional[str]:
        """Select held item based on difficulty."""
        if self.difficulty == AIDifficulty.BEGINNER:
            return None  # No items for beginners
        
        items = ['Leftovers', 'Choice Band', 'Choice Specs', 'Focus Sash', 'Life Orb']
        return random.choice(items) if random.random() > 0.3 else None
    
    def select_move(self, battle_state: BattleState, active_pokemon: PokemonBattleState) -> str:
        """Select a move for the AI Pokemon."""
        available_moves = active_pokemon.pokemon.moves
        
        if not available_moves:
            return "Struggle"
        
        # Apply personality-based decision making
        if self.personality == AIPersonality.RANDOM:
            return random.choice(available_moves)
        
        elif self.personality == AIPersonality.SMART:
            return self._select_smart_move(battle_state, active_pokemon, available_moves)
        
        elif self.personality == AIPersonality.AGGRESSIVE:
            return self._select_aggressive_move(battle_state, active_pokemon, available_moves)
        
        elif self.personality == AIPersonality.DEFENSIVE:
            return self._select_defensive_move(battle_state, active_pokemon, available_moves)
        
        else:  # BALANCED
            return self._select_balanced_move(battle_state, active_pokemon, available_moves)
    
    def _select_smart_move(self, battle_state: BattleState, active_pokemon: PokemonBattleState, moves: List[str]) -> str:
        """Select move based on type effectiveness analysis."""
        if not battle_state.opponent_team:
            return random.choice(moves)
        
        opponent_pokemon = battle_state.opponent_team[0]  # Assume single battle
        best_move = moves[0]
        best_effectiveness = 1.0
        
        for move in moves:
            # Get move type (simplified)
            move_type = self._guess_move_type(move)
            effectiveness = self._calculate_type_effectiveness(move_type, opponent_pokemon.pokemon.types)
            
            if effectiveness > best_effectiveness:
                best_effectiveness = effectiveness
                best_move = move
        
        logger.debug(f"AI selected {best_move} with {best_effectiveness}x effectiveness")
        return best_move
    
    def _select_aggressive_move(self, battle_state: BattleState, active_pokemon: PokemonBattleState, moves: List[str]) -> str:
        """Select aggressive attacking move."""
        # Prefer moves with "attack" terms
        aggressive_moves = [m for m in moves if any(term in m.lower() for term in ['attack', 'punch', 'blast', 'beam', 'rush'])]
        return random.choice(aggressive_moves) if aggressive_moves else random.choice(moves)
    
    def _select_defensive_move(self, battle_state: BattleState, active_pokemon: PokemonBattleState, moves: List[str]) -> str:
        """Select defensive move."""
        # Prefer defensive moves
        defensive_moves = [m for m in moves if any(term in m.lower() for term in ['heal', 'recover', 'protect', 'defend', 'barrier'])]
        return random.choice(defensive_moves) if defensive_moves else random.choice(moves)
    
    def _select_balanced_move(self, battle_state: BattleState, active_pokemon: PokemonBattleState, moves: List[str]) -> str:
        """Select balanced move based on multiple factors."""
        # Simple balanced selection - could be much more sophisticated
        if active_pokemon.current_hp < active_pokemon.pokemon.stats.hp // 2:
            # Low health - try defensive moves
            return self._select_defensive_move(battle_state, active_pokemon, moves)
        else:
            # Good health - be aggressive
            return self._select_aggressive_move(battle_state, active_pokemon, moves)
    
    def _guess_move_type(self, move_name: str) -> str:
        """Guess move type from name (simplified)."""
        move_lower = move_name.lower()
        
        type_hints = {
            'fire': ['fire', 'flame', 'burn', 'blast'],
            'water': ['water', 'surf', 'bubble', 'hydro'],
            'grass': ['grass', 'vine', 'leaf', 'solar'],
            'electric': ['thunder', 'electric', 'shock', 'bolt'],
            'ice': ['ice', 'freeze', 'blizzard'],
            'fighting': ['punch', 'kick', 'combat', 'fighting'],
            'psychic': ['psychic', 'psych', 'confusion'],
            'ghost': ['shadow', 'ghost', 'spirit'],
            'dragon': ['dragon', 'outrage'],
            'dark': ['dark', 'night', 'evil'],
            'steel': ['steel', 'iron', 'metal'],
            'fairy': ['fairy', 'charm', 'magic']
        }
        
        for type_name, hints in type_hints.items():
            if any(hint in move_lower for hint in hints):
                return type_name
        
        return 'normal'
    
    def _calculate_type_effectiveness(self, attack_type: str, defender_types: List) -> float:
        """Calculate type effectiveness."""
        from ..config.game_config import GameConfig
        
        total_effectiveness = 1.0
        for defender_type in defender_types:
            effectiveness = GameConfig.get_type_effectiveness(attack_type, defender_type.value)
            total_effectiveness *= effectiveness
        
        return total_effectiveness
    
    def should_switch_pokemon(self, battle_state: BattleState, current_pokemon: PokemonBattleState) -> bool:
        """Decide whether to switch Pokemon."""
        if self.difficulty == AIDifficulty.BEGINNER:
            return False  # Beginners don't switch
        
        # Switch if current Pokemon is at low health and we have alternatives
        if current_pokemon.current_hp < current_pokemon.pokemon.stats.hp // 4:
            available_pokemon = [p for p in battle_state.player_team if p.current_hp > 0 and p != current_pokemon]
            return len(available_pokemon) > 0
        
        return False
    
    def get_battle_cry(self) -> str:
        """Get AI battle cry based on personality."""
        cries = {
            AIPersonality.AGGRESSIVE: [
                "Let's battle with full force!",
                "I'll crush you with power!",
                "Prepare for an aggressive assault!"
            ],
            AIPersonality.DEFENSIVE: [
                "Defense is the best offense!",
                "I'll outlast you!",
                "Patience and strategy will win!"
            ],
            AIPersonality.SMART: [
                "Let me analyze your weaknesses...",
                "Strategy will prevail!",
                "I've calculated your defeat!"
            ],
            AIPersonality.RANDOM: [
                "Let's see what happens!",
                "Anything can happen in battle!",
                "Random chaos, here we go!"
            ],
            AIPersonality.GAMECUBE_SHADOW: [
                "The shadows will consume you!",
                "Feel the power of darkness!",
                "Shadow Pokemon, attack!"
            ]
        }
        
        personality_cries = cries.get(self.personality, ["Let's have a good battle!"])
        return random.choice(personality_cries)

class AIOpponentManager:
    """Manages AI opponents and their selection."""
    
    def __init__(self):
        self.opponents = {}
        self._create_default_opponents()
    
    def _create_default_opponents(self):
        """Create default AI opponents."""
        opponents_data = [
            {
                'name': 'Rookie Trainer',
                'difficulty': AIDifficulty.BEGINNER,
                'personality': AIPersonality.RANDOM,
                'description': 'A new trainer just starting their journey'
            },
            {
                'name': 'Battle Student',
                'difficulty': AIDifficulty.INTERMEDIATE,
                'personality': AIPersonality.BALANCED,
                'description': 'A trainer learning advanced strategies'
            },
            {
                'name': 'Strategy Expert',
                'difficulty': AIDifficulty.ADVANCED,
                'personality': AIPersonality.SMART,
                'description': 'An experienced trainer who analyzes every move'
            },
            {
                'name': 'Battle Master',
                'difficulty': AIDifficulty.EXPERT,
                'personality': AIPersonality.BALANCED,
                'description': 'A master trainer with perfect strategies'
            },
            {
                'name': 'Aggressive Challenger',
                'difficulty': AIDifficulty.ADVANCED,
                'personality': AIPersonality.AGGRESSIVE,
                'description': 'A trainer who believes in overwhelming offense'
            },
            {
                'name': 'Defensive Specialist',
                'difficulty': AIDifficulty.ADVANCED,
                'personality': AIPersonality.DEFENSIVE,
                'description': 'A trainer who excels at defensive strategies'
            },
            {
                'name': 'Shadow Master',
                'difficulty': AIDifficulty.EXPERT,
                'personality': AIPersonality.GAMECUBE_SHADOW,
                'description': 'A mysterious trainer wielding Shadow Pokemon'
            }
        ]
        
        for data in opponents_data:
            opponent = BattleAI(
                name=data['name'],
                difficulty=data['difficulty'],
                personality=data['personality']
            )
            opponent.description = data['description']
            self.opponents[data['name']] = opponent
        
        logger.info(f"Created {len(self.opponents)} AI opponents")
    
    def get_opponent(self, name: str) -> Optional[BattleAI]:
        """Get AI opponent by name."""
        return self.opponents.get(name)
    
    def get_available_opponents(self) -> List[Dict[str, Any]]:
        """Get list of available AI opponents."""
        return [
            {
                'name': opponent.name,
                'difficulty': opponent.difficulty.value,
                'personality': opponent.personality.value,
                'description': getattr(opponent, 'description', 'An AI trainer'),
                'team_size': opponent.team.get_team_size()
            }
            for opponent in self.opponents.values()
        ]
    
    def get_random_opponent(self, difficulty: Optional[AIDifficulty] = None) -> BattleAI:
        """Get a random opponent, optionally filtered by difficulty."""
        available = list(self.opponents.values())
        
        if difficulty:
            available = [opp for opp in available if opp.difficulty == difficulty]
        
        if not available:
            available = list(self.opponents.values())
        
        return random.choice(available)
    
    def create_custom_opponent(
        self,
        name: str,
        difficulty: AIDifficulty,
        personality: AIPersonality,
        team: Optional[PokemonTeam] = None
    ) -> BattleAI:
        """Create a custom AI opponent."""
        opponent = BattleAI(name, difficulty, personality, team)
        self.opponents[name] = opponent
        logger.info(f"Created custom AI opponent: {name}")
        return opponent