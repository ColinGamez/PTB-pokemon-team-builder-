"""
Battle state management for Pokemon battles.
Tracks Pokemon status, health, and battle conditions.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import random

from ..core.pokemon import Pokemon, ShadowPokemon
from ..core.types import PokemonType
from ..core.pokemon import PokemonNature


class BattleStatus(Enum):
    """Pokemon battle status conditions."""
    NORMAL = "normal"
    SLEEP = "sleep"
    POISON = "poison"
    BURN = "burn"
    FREEZE = "freeze"
    PARALYSIS = "paralysis"
    CONFUSION = "confusion"
    FLINCH = "flinch"
    LEECH_SEED = "leech_seed"
    CURSE = "curse"
    NIGHTMARE = "nightmare"
    BIND = "bind"
    WRAP = "wrap"
    CLAMP = "clamp"
    FIRE_SPIN = "fire_spin"
    MAGMA_STORM = "magma_storm"
    SAND_TOMB = "sand_tomb"
    INFESTATION = "infestation"
    THUNDER_CAGE = "thunder_cage"
    WHIRLPOOL = "whirlpool"
    DRAGON_RAGE = "dragon_rage"
    SONIC_BOOM = "sonic_boom"
    SEISMIC_TOSS = "seismic_toss"
    NIGHT_SHADE = "night_shade"
    PSYWAVE = "psywave"


class WeatherCondition(Enum):
    """Weather conditions affecting battles."""
    CLEAR = "clear"
    SUNNY = "sunny"
    RAINY = "rainy"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    FOGGY = "foggy"
    STRONG_WINDS = "strong_winds"


class TerrainCondition(Enum):
    """Terrain conditions affecting battles."""
    NORMAL = "normal"
    ELECTRIC = "electric"
    GRASSY = "grassy"
    MISTY = "misty"
    PSYCHIC = "psychic"


@dataclass
class PokemonBattleState:
    """Represents a Pokemon's state during battle."""
    
    pokemon: Pokemon
    current_hp: int
    max_hp: int
    status: BattleStatus = BattleStatus.NORMAL
    status_turns: int = 0
    confusion_turns: int = 0
    stat_modifiers: Dict[str, int] = field(default_factory=lambda: {
        'attack': 0, 'defense': 0, 'special_attack': 0, 
        'special_defense': 0, 'speed': 0, 'accuracy': 0, 'evasion': 0
    })
    temporary_effects: Set[str] = field(default_factory=set)
    last_move_used: Optional[str] = None
    move_pp: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize move PP and other battle-specific attributes."""
        self.max_hp = self.pokemon.stats.hp
        self.current_hp = self.max_hp
        
        # Initialize move PP (simplified - in real implementation this would come from move data)
        for move in self.pokemon.moves:
            self.move_pp[move] = 10  # Default PP for moves
    
    def is_fainted(self) -> bool:
        """Check if Pokemon is fainted."""
        return self.current_hp <= 0
    
    def can_battle(self) -> bool:
        """Check if Pokemon can participate in battle."""
        return not self.is_fainted() and self.status != BattleStatus.SLEEP
    
    def get_effective_stat(self, stat_name: str) -> int:
        """Get effective stat value considering modifiers."""
        base_stat = getattr(self.pokemon.stats, stat_name, 0)
        
        # Apply stat modifiers
        modifier = self.stat_modifiers.get(stat_name, 0)
        if modifier > 0:
            # Positive modifiers: +1 = 1.5x, +2 = 2x, +3 = 2.5x, +4 = 3x, +5 = 3.5x, +6 = 4x
            multiplier = (2 + modifier) / 2
        elif modifier < 0:
            # Negative modifiers: -1 = 2/3x, -2 = 1/2x, -3 = 2/5x, -4 = 1/3x, -5 = 2/7x, -6 = 1/4x
            multiplier = 2 / (2 - modifier)
        else:
            multiplier = 1.0
        
        return int(base_stat * multiplier)
    
    def apply_damage(self, damage: int) -> int:
        """Apply damage to the Pokemon and return actual damage dealt."""
        actual_damage = min(damage, self.current_hp)
        self.current_hp = max(0, self.current_hp - damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal the Pokemon and return actual healing done."""
        actual_healing = min(amount, self.max_hp - self.current_hp)
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return actual_healing
    
    def apply_status(self, new_status: BattleStatus) -> bool:
        """Apply a status condition to the Pokemon."""
        if self.status != BattleStatus.NORMAL:
            return False  # Already has a status
        
        self.status = new_status
        self.status_turns = 0
        return True
    
    def update_status_turns(self):
        """Update status condition duration."""
        if self.status != BattleStatus.NORMAL:
            self.status_turns += 1
            
            # Some status conditions wear off over time
            if self.status == BattleStatus.SLEEP and self.status_turns >= 3:
                self.status = BattleStatus.NORMAL
                self.status_turns = 0
            elif self.status == BattleStatus.CONFUSION and self.confusion_turns >= 4:
                self.status = BattleStatus.NORMAL
                self.confusion_turns = 0
    
    def has_move_pp(self, move_name: str) -> bool:
        """Check if a move has PP remaining."""
        return self.move_pp.get(move_name, 0) > 0
    
    def use_move(self, move_name: str) -> bool:
        """Use a move, consuming PP."""
        if not self.has_move_pp(move_name):
            return False
        
        self.move_pp[move_name] -= 1
        self.last_move_used = move_name
        return True
    
    def get_health_percentage(self) -> float:
        """Get current health as a percentage."""
        if self.max_hp == 0:
            return 0.0
        return (self.current_hp / self.max_hp) * 100
    
    def get_status_description(self) -> str:
        """Get human-readable status description."""
        if self.status == BattleStatus.NORMAL:
            return f"HP: {self.current_hp}/{self.max_hp} ({self.get_health_percentage():.1f}%)"
        else:
            return f"HP: {self.current_hp}/{self.max_hp} ({self.get_health_percentage():.1f}%) - {self.status.value.title()}"
    
    def __str__(self) -> str:
        return f"{self.pokemon.name} - {self.get_status_description()}"


@dataclass
class BattleState:
    """Represents the overall state of a battle."""
    
    player_team: List[PokemonBattleState]
    opponent_team: List[PokemonBattleState]
    current_turn: int = 1
    weather: WeatherCondition = WeatherCondition.CLEAR
    weather_turns: int = 0
    terrain: TerrainCondition = TerrainCondition.NORMAL
    terrain_turns: int = 0
    battle_log: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize battle state."""
        if not self.player_team:
            raise ValueError("Player team cannot be empty")
        if not self.opponent_team:
            raise ValueError("Opponent team cannot be empty")
    
    def get_active_pokemon(self, is_player: bool) -> Optional[PokemonBattleState]:
        """Get the currently active Pokemon for a side."""
        team = self.player_team if is_player else self.opponent_team
        for pokemon in team:
            if pokemon.can_battle():
                return pokemon
        return None
    
    def get_team_status(self, is_player: bool) -> str:
        """Get status summary for a team."""
        team = self.player_team if is_player else self.opponent_team
        active_count = sum(1 for p in team if p.can_battle())
        total_count = len(team)
        
        return f"{active_count}/{total_count} Pokemon active"
    
    def add_battle_log(self, message: str):
        """Add a message to the battle log."""
        self.battle_log.append(f"Turn {self.current_turn}: {message}")
    
    def update_weather(self):
        """Update weather conditions."""
        if self.weather != WeatherCondition.CLEAR:
            self.weather_turns += 1
            
            # Weather effects wear off after 5 turns
            if self.weather_turns >= 5:
                self.weather = WeatherCondition.CLEAR
                self.weather_turns = 0
                self.add_battle_log(f"Weather cleared up!")
    
    def update_terrain(self):
        """Update terrain conditions."""
        if self.terrain != TerrainCondition.NORMAL:
            self.terrain_turns += 1
            
            # Terrain effects wear off after 5 turns
            if self.terrain_turns >= 5:
                self.terrain = TerrainCondition.NORMAL
                self.terrain_turns = 0
                self.add_battle_log(f"Terrain returned to normal!")
    
    def is_battle_over(self) -> bool:
        """Check if the battle is over."""
        player_active = any(p.can_battle() for p in self.player_team)
        opponent_active = any(p.can_battle() for p in self.opponent_team)
        
        return not player_active or not opponent_active
    
    def get_winner(self) -> Optional[bool]:
        """Get the winner of the battle (True for player, False for opponent, None if ongoing)."""
        if not self.is_battle_over():
            return None
        
        player_active = any(p.can_battle() for p in self.player_team)
        opponent_active = any(p.can_battle() for p in self.opponent_team)
        
        if player_active and not opponent_active:
            return True  # Player wins
        elif opponent_active and not player_active:
            return False  # Opponent wins
        else:
            return None  # Draw or error
    
    def get_battle_summary(self) -> str:
        """Get a summary of the current battle state."""
        player_status = self.get_team_status(True)
        opponent_status = self.get_team_status(False)
        
        summary = [
            f"Battle Status - Turn {self.current_turn}",
            f"Player: {player_status}",
            f"Opponent: {opponent_status}",
            f"Weather: {self.weather.value.title()}",
            f"Terrain: {self.terrain.value.title()}"
        ]
        
        return "\n".join(summary)
