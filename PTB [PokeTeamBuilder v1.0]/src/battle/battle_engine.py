"""
Battle engine for Pokemon battles.
Handles damage calculations, status effects, and battle mechanics.
"""

from typing import List, Dict, Optional, Tuple, Any
import random
import math
import logging
from functools import lru_cache

from .battle_state import BattleState, PokemonBattleState, BattleStatus, WeatherCondition, TerrainCondition
from ..core.types import PokemonType, TypeEffectiveness
from ..core.pokemon import Pokemon
from ..config.game_config import GameConfig

logger = logging.getLogger(__name__)


class BattleEngine:
    """Core battle mechanics engine."""
    
    def __init__(self):
        # Use centralized configuration
        self.critical_hit_chance = GameConfig.CRITICAL_HIT_CHANCE
        self.stab_multiplier = GameConfig.STAB_MULTIPLIER
        self.weather_multipliers = GameConfig.WEATHER_MULTIPLIERS
        self.terrain_multipliers = GameConfig.TERRAIN_MULTIPLIERS
        
        logger.info("Battle engine initialized with centralized configuration")
    
    def calculate_damage(
        self,
        attacker: PokemonBattleState,
        defender: PokemonBattleState,
        move_name: str,
        battle_state: BattleState,
        is_critical: bool = False
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate damage for a move.
        
        Args:
            attacker: The attacking Pokemon
            defender: The defending Pokemon
            move_name: Name of the move being used
            battle_state: Current battle state
            is_critical: Whether this is a critical hit
            
        Returns:
            Tuple of (damage, battle_info)
        """
        # Get move information (simplified - in real implementation this would come from move database)
        move_info = self._get_move_info(move_name)
        
        # Calculate base damage
        if move_info['category'] == 'physical':
            attack_stat = attacker.get_effective_stat('attack')
            defense_stat = defender.get_effective_stat('defense')
        else:  # special
            attack_stat = attacker.get_effective_stat('special_attack')
            defense_stat = defender.get_effective_stat('special_defense')
        
        # Base damage formula (simplified)
        base_damage = self._calculate_base_damage(
            attacker.pokemon.level,
            move_info['power'],
            attack_stat,
            defense_stat
        )
        
        # Apply modifiers
        modifiers = self._calculate_damage_modifiers(
            attacker, defender, move_info, battle_state, is_critical
        )
        
        # Calculate final damage
        final_damage = int(base_damage * modifiers['total_multiplier'])
        
        # Ensure minimum damage
        final_damage = max(1, final_damage)
        
        return final_damage, modifiers
    
    def _calculate_base_damage(
        self,
        level: int,
        power: int,
        attack: int,
        defense: int
    ) -> float:
        """Calculate base damage using the standard Pokemon formula."""
        # Standard damage formula: ((2 * Level / 5 + 2) * Power * Attack / Defense) / 50 + 2
        level_factor = (2 * level / 5 + 2)
        damage = (level_factor * power * attack / defense) / 50 + 2
        return damage
    
    def _calculate_damage_modifiers(
        self,
        attacker: PokemonBattleState,
        defender: PokemonBattleState,
        move_info: Dict[str, Any],
        battle_state: BattleState,
        is_critical: bool
    ) -> Dict[str, Any]:
        """Calculate all damage modifiers."""
        modifiers = {
            'stab': 1.0,
            'type_effectiveness': 1.0,
            'critical': 1.0,
            'weather': 1.0,
            'terrain': 1.0,
            'random': 1.0,
            'total_multiplier': 1.0
        }
        
        # STAB (Same Type Attack Bonus)
        if self._has_stab(attacker.pokemon, move_info['type']):
            modifiers['stab'] = self.stab_multiplier
        
        # Type effectiveness
        effectiveness = self._calculate_type_effectiveness(
            move_info['type'], defender.pokemon.types
        )
        modifiers['type_effectiveness'] = effectiveness
        
        # Critical hit
        if is_critical:
            modifiers['critical'] = 1.5
        
        # Weather effects
        weather_mult = self.weather_multipliers.get(battle_state.weather.value if battle_state.weather else "", {})
        if move_info['type'] in weather_mult:
            modifiers['weather'] = weather_mult[move_info['type']]
        
        # Terrain effects
        terrain_mult = self.terrain_multipliers.get(battle_state.terrain.value if battle_state.terrain else "", {})
        if move_info['type'] in terrain_mult:
            modifiers['terrain'] = terrain_mult[move_info['type']]
        
        # Random factor (85-100%)
        modifiers['random'] = random.uniform(0.85, 1.0)
        
        # Calculate total multiplier
        modifiers['total_multiplier'] = (
            modifiers['stab'] *
            modifiers['type_effectiveness'] *
            modifiers['critical'] *
            modifiers['weather'] *
            modifiers['terrain'] *
            modifiers['random']
        )
        
        return modifiers
    
    def _has_stab(self, pokemon: Pokemon, move_type: str) -> bool:
        """Check if Pokemon gets STAB bonus for a move type."""
        pokemon_types = [t.value.lower() for t in pokemon.types]
        return move_type.lower() in pokemon_types
    
    def _calculate_type_effectiveness(self, attack_type: str, defender_types: List[PokemonType]) -> float:
        """Calculate type effectiveness of an attack against defender types."""
        if not defender_types:
            return 1.0
        
        total_effectiveness = 1.0
        
        for defender_type in defender_types:
            # Simplified type effectiveness calculation
            # In real implementation, this would use the full type chart
            effectiveness = self._get_type_effectiveness(attack_type, defender_type.value)
            total_effectiveness *= effectiveness
        
        return total_effectiveness
    
    @lru_cache(maxsize=1000)
    def _get_type_effectiveness(self, attack_type: str, defender_type: str) -> float:
        """Get type effectiveness using centralized configuration with caching."""
        effectiveness = GameConfig.get_type_effectiveness(attack_type, defender_type)
        logger.debug(f"Type effectiveness: {attack_type} vs {defender_type} = {effectiveness}x")
        return effectiveness
    
    @lru_cache(maxsize=500)
    def _get_move_info(self, move_name: str) -> Dict[str, Any]:
        """Get move information from database with caching."""
        import json
        
        # Try to load from database first
        try:
            if GameConfig.MOVES_DATABASE.exists():
                with open(GameConfig.MOVES_DATABASE, 'r') as f:
                    moves_data = json.load(f)
                
                if move_name in moves_data:
                    move_info = moves_data[move_name].copy()
                    logger.debug(f"Loaded move {move_name} from database")
                    return move_info
        except Exception as e:
            logger.warning(f"Could not load move {move_name} from database: {e}")
        
        # Fallback to heuristic-based move detection
        move_name_lower = move_name.lower()
        
        # Default move info
        move_info = {
            'name': move_name,
            'type': 'normal',
            'category': 'physical',
            'power': 50,
            'accuracy': 100,
            'pp': 10,
            'description': 'A basic move'
        }
        
        # Type-based move detection
        if any(type_name in move_name_lower for type_name in ['fire', 'flame', 'burn']):
            move_info.update({'type': 'fire', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['water', 'surf', 'bubble']):
            move_info.update({'type': 'water', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['grass', 'vine', 'leaf']):
            move_info.update({'type': 'grass', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['electric', 'thunder', 'spark']):
            move_info.update({'type': 'electric', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['ice', 'freeze', 'frost']):
            move_info.update({'type': 'ice', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['fighting', 'punch', 'kick']):
            move_info.update({'type': 'fighting', 'category': 'physical'})
        elif any(type_name in move_name_lower for type_name in ['poison', 'sludge', 'acid']):
            move_info.update({'type': 'poison', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['ground', 'earth', 'quake']):
            move_info.update({'type': 'ground', 'category': 'physical'})
        elif any(type_name in move_name_lower for type_name in ['flying', 'wing', 'air']):
            move_info.update({'type': 'flying', 'category': 'physical'})
        elif any(type_name in move_name_lower for type_name in ['psychic', 'mind', 'tele']):
            move_info.update({'type': 'psychic', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['bug', 'insect', 'cocoon']):
            move_info.update({'type': 'bug', 'category': 'physical'})
        elif any(type_name in move_name_lower for type_name in ['rock', 'stone', 'boulder']):
            move_info.update({'type': 'rock', 'category': 'physical'})
        elif any(type_name in move_name_lower for type_name in ['ghost', 'shadow', 'spirit']):
            move_info.update({'type': 'ghost', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['dragon', 'dragon']):
            move_info.update({'type': 'dragon', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['dark', 'night', 'evil']):
            move_info.update({'type': 'dark', 'category': 'special'})
        elif any(type_name in move_name_lower for type_name in ['steel', 'iron', 'metal']):
            move_info.update({'type': 'steel', 'category': 'physical'})
        elif any(type_name in move_name_lower for type_name in ['fairy', 'magic', 'charm']):
            move_info.update({'type': 'fairy', 'category': 'special'})
        
        # Power adjustments based on move name
        if any(power_word in move_name_lower for power_word in ['blast', 'cannon', 'beam']):
            move_info['power'] = 120
        elif any(power_word in move_name_lower for power_word in ['punch', 'kick', 'slash']):
            move_info['power'] = 75
        elif any(power_word in move_name_lower for power_word in ['tackle', 'scratch', 'bite']):
            move_info['power'] = 40
        
        return move_info
    
    def check_critical_hit(self, attacker: PokemonBattleState, move_name: str) -> bool:
        """Check if a move results in a critical hit."""
        # Base critical hit chance
        chance = self.critical_hit_chance
        
        # High critical hit ratio moves
        high_crit_moves = ['slash', 'razor leaf', 'crabhammer', 'karate chop', 'cross chop']
        if any(crit_move in move_name.lower() for crit_move in high_crit_moves):
            chance *= 2
        
        # Focus Energy effect
        if 'focus_energy' in attacker.temporary_effects:
            chance *= 2
        
        return random.random() < chance
    
    def check_move_hit(self, move_name: str, accuracy_modifiers: Optional[Dict[str, float]] = None) -> bool:
        """Check if a move hits the target."""
        if accuracy_modifiers is None:
            accuracy_modifiers = {}
        
        # Get base accuracy
        move_info = self._get_move_info(move_name)
        base_accuracy = move_info['accuracy']
        
        # Apply accuracy modifiers
        final_accuracy = base_accuracy
        for modifier in accuracy_modifiers.values():
            final_accuracy *= modifier
        
        # Ensure accuracy is within bounds
        final_accuracy = max(1, min(100, final_accuracy))
        
        return random.randint(1, 100) <= final_accuracy
    
    def apply_status_effect(
        self,
        target: PokemonBattleState,
        status: BattleStatus,
        chance: float = 1.0
    ) -> bool:
        """Apply a status effect to a Pokemon."""
        if random.random() > chance:
            return False
        
        return target.apply_status(status)
    
    def update_battle_state(self, battle_state: BattleState):
        """Update battle state for the next turn."""
        battle_state.current_turn += 1
        
        # Update weather and terrain
        battle_state.update_weather()
        battle_state.update_terrain()
        
        # Update Pokemon status
        for pokemon in battle_state.player_team + battle_state.opponent_team:
            pokemon.update_status_turns()
    
    def get_battle_summary(self, battle_state: BattleState) -> str:
        """Get a comprehensive battle summary."""
        summary = [
            battle_state.get_battle_summary(),
            "",
            "Player Team:",
            *[f"  {pokemon}" for pokemon in battle_state.player_team],
            "",
            "Opponent Team:",
            *[f"  {pokemon}" for pokemon in battle_state.opponent_team]
        ]
        
        return "\n".join(summary)
