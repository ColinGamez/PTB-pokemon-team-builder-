"""
Pokemon stats system with comprehensive validation and calculation methods.
Includes EV, IV, and stat calculation for all game eras.
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class StatType(Enum):
    """Pokemon stat types."""
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"


@dataclass
class BaseStats:
    """Base stats for a Pokemon species."""
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    def __post_init__(self):
        """Validate base stats are within valid ranges."""
        for stat_name, value in self.__dict__.items():
            if not isinstance(value, int):
                raise ValueError(f"{stat_name} must be an integer, got {type(value)}")
            if value < 1 or value > 255:
                raise ValueError(f"{stat_name} must be between 1 and 255, got {value}")
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get a specific stat value."""
        return getattr(self, stat_type.value)
    
    def get_total(self) -> int:
        """Get total base stat value."""
        return sum(self.__dict__.values())
    
    def get_average(self) -> float:
        """Get average base stat value."""
        return self.get_total() / 6.0
    
    def get_highest_stat(self) -> Tuple[StatType, int]:
        """Get the highest stat and its value."""
        stats = {StatType(key): value for key, value in self.__dict__.items()}
        highest_stat = max(stats.items(), key=lambda x: x[1])
        return highest_stat
    
    def get_lowest_stat(self) -> Tuple[StatType, int]:
        """Get the lowest stat and its value."""
        stats = {StatType(key): value for key, value in self.__dict__.items()}
        lowest_stat = min(stats.items(), key=lambda x: x[1])
        return lowest_stat


@dataclass
class EV:
    """Effort Values (0-255 per stat, max 510 total)."""
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0
    
    def __post_init__(self):
        """Validate EV values and total."""
        total = sum(self.__dict__.values())
        if total > 510:
            raise ValueError(f"Total EVs cannot exceed 510, got {total}")
        
        for stat_name, value in self.__dict__.items():
            if not isinstance(value, int):
                raise ValueError(f"{stat_name} EV must be an integer, got {type(value)}")
            if value < 0 or value > 255:
                raise ValueError(f"{stat_name} EV must be between 0 and 255, got {value}")
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get EV value for a specific stat."""
        return getattr(self, stat_type.value)
    
    def set_stat(self, stat_type: StatType, value: int) -> bool:
        """
        Set EV value for a specific stat.
        
        Args:
            stat_type: Stat to set
            value: New EV value
            
        Returns:
            True if successful, False if it would exceed total limit
        """
        current_total = self.get_total()
        current_stat_ev = self.get_stat(stat_type)
        new_total = current_total - current_stat_ev + value
        
        if new_total > 510:
            return False
        
        if value < 0 or value > 255:
            return False
        
        setattr(self, stat_type.value, value)
        return True
    
    def add_ev(self, stat_type: StatType, amount: int) -> bool:
        """
        Add EVs to a specific stat.
        
        Args:
            stat_type: Stat to add EVs to
            amount: Amount of EVs to add
            
        Returns:
            True if successful, False if it would exceed limits
        """
        current_ev = self.get_stat(stat_type)
        new_ev = current_ev + amount
        
        if new_ev > 255:
            return False
        
        current_total = self.get_total()
        if current_total + amount > 510:
            return False
        
        setattr(self, stat_type.value, new_ev)
        return True
    
    def get_total(self) -> int:
        """Get total EV value."""
        return sum(self.__dict__.values())
    
    def get_remaining(self) -> int:
        """Get remaining EVs that can be allocated."""
        return 510 - self.get_total()
    
    def is_maxed(self) -> bool:
        """Check if all EVs are allocated."""
        return self.get_total() == 510
    
    def reset(self):
        """Reset all EVs to 0."""
        for stat_name in self.__dict__.keys():
            setattr(self, stat_name, 0)
    
    def get_optimal_spread(self, primary_stat: StatType, secondary_stat: StatType) -> bool:
        """
        Set optimal EV spread for two stats (252/252/6).
        
        Args:
            primary_stat: Primary stat to max out
            secondary_stat: Secondary stat to max out
            
        Returns:
            True if successful
        """
        if primary_stat == secondary_stat:
            return False
        
        # Reset all EVs
        self.reset()
        
        # Set primary stat to 252
        setattr(self, primary_stat.value, 252)
        
        # Set secondary stat to 252
        setattr(self, secondary_stat.value, 252)
        
        # Set remaining 6 EVs to speed (common choice)
        remaining_stat = StatType.SPEED
        if remaining_stat in [primary_stat, secondary_stat]:
            # If speed is already maxed, put remaining EVs in HP
            remaining_stat = StatType.HP
        
        setattr(self, remaining_stat.value, 6)
        
        return True


@dataclass
class IV:
    """Individual Values (0-31 per stat)."""
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0
    
    def __post_init__(self):
        """Validate IV values."""
        for stat_name, value in self.__dict__.items():
            if not isinstance(value, int):
                raise ValueError(f"{stat_name} IV must be an integer, got {type(value)}")
            if value < 0 or value > 31:
                raise ValueError(f"{stat_name} IV must be between 0 and 31, got {value}")
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get IV value for a specific stat."""
        return getattr(self, stat_type.value)
    
    def set_stat(self, stat_type: StatType, value: int) -> bool:
        """
        Set IV value for a specific stat.
        
        Args:
            stat_type: Stat to set
            value: New IV value
            
        Returns:
            True if successful, False if value is invalid
        """
        if value < 0 or value > 31:
            return False
        
        setattr(self, stat_type.value, value)
        return True
    
    def get_total(self) -> int:
        """Get total IV value."""
        return sum(self.__dict__.values())
    
    def get_average(self) -> float:
        """Get average IV value."""
        return self.get_total() / 6.0
    
    def is_perfect(self) -> bool:
        """Check if all IVs are 31 (perfect)."""
        return all(value == 31 for value in self.__dict__.values())
    
    def is_zero(self) -> bool:
        """Check if all IVs are 0."""
        return all(value == 0 for value in self.__dict__.values())
    
    def get_perfect_count(self) -> int:
        """Get count of perfect (31) IVs."""
        return sum(1 for value in self.__dict__.values() if value == 31)
    
    def get_zero_count(self) -> int:
        """Get count of zero IVs."""
        return sum(1 for value in self.__dict__.values() if value == 0)
    
    def reset(self):
        """Reset all IVs to 0."""
        for stat_name in self.__dict__.keys():
            setattr(self, stat_name, 0)
    
    def set_perfect(self):
        """Set all IVs to 31 (perfect)."""
        for stat_name in self.__dict__.keys():
            setattr(self, stat_name, 31)


class Stats:
    """Comprehensive Pokemon stats system with calculation methods."""
    
    def __init__(
        self,
        base_stats: BaseStats,
        level: int = 100,
        evs: Optional[EV] = None,
        ivs: Optional[IV] = None,
        nature_modifiers: Optional[Dict[StatType, float]] = None
    ):
        """
        Initialize Pokemon stats with base stats and modifiers.
        
        Args:
            base_stats: Base stats for the species
            level: Pokemon's level (1-100)
            evs: Effort Values
            ivs: Individual Values
            nature_modifiers: Nature stat modifiers
        """
        if not isinstance(base_stats, BaseStats):
            raise ValueError("base_stats must be a BaseStats instance")
        
        if not isinstance(level, int) or level < 1 or level > 100:
            raise ValueError("Level must be between 1 and 100")
        
        self.base_stats = base_stats
        self.level = level
        self.evs = evs or EV()
        self.ivs = ivs or IV()
        self.nature_modifiers = nature_modifiers or {}
        
        # Calculate actual stats
        self._calculate_stats()
    
    def _calculate_stats(self):
        """Calculate actual Pokemon stats based on base stats, level, EVs, IVs, and nature."""
        self.stats = {}
        
        for stat_type in StatType:
            base_stat = self.base_stats.get_stat(stat_type)
            ev = self.evs.get_stat(stat_type)
            iv = self.ivs.get_stat(stat_type)
            
            # Apply nature modifier
            nature_modifier = self.nature_modifiers.get(stat_type, 1.0)
            
            # Calculate stat value
            if stat_type == StatType.HP:
                # HP formula: ((2 * Base + IV + EV/4) * Level / 100) + Level + 10
                stat_value = int(((2 * base_stat + iv + ev // 4) * self.level) // 100 + self.level + 10)
            else:
                # Other stats formula: ((2 * Base + IV + EV/4) * Level / 100 + 5) * Nature
                stat_value = int(((2 * base_stat + iv + ev // 4) * self.level) // 100 + 5)
                stat_value = int(stat_value * nature_modifier)
            
            self.stats[stat_type] = stat_value
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get calculated stat value."""
        return self.stats.get(stat_type, 0)
    
    def get_all_stats(self) -> Dict[StatType, int]:
        """Get all calculated stats."""
        return self.stats.copy()
    
    def get_total_stats(self) -> int:
        """Get sum of all calculated stats."""
        return sum(self.stats.values())
    
    def get_average_stats(self) -> float:
        """Get average of all calculated stats."""
        return self.get_total_stats() / 6.0
    
    def get_highest_stat(self) -> Tuple[StatType, int]:
        """Get the highest stat and its value."""
        highest_stat = max(self.stats.items(), key=lambda x: x[1])
        return highest_stat
    
    def get_lowest_stat(self) -> Tuple[StatType, int]:
        """Get the lowest stat and its value."""
        lowest_stat = min(self.stats.items(), key=lambda x: x[1])
        return lowest_stat
    
    def get_stat_percentage(self, stat_type: StatType, max_value: int = 255) -> float:
        """
        Get stat as a percentage of maximum possible value.
        
        Args:
            stat_type: Stat to get percentage for
            max_value: Maximum possible value for comparison
            
        Returns:
            Percentage as a float (0.0 to 1.0)
        """
        current_value = self.get_stat(stat_type)
        return current_value / max_value
    
    def recalculate_stats(self):
        """Recalculate stats (useful after changing EVs, IVs, or level)."""
        self._calculate_stats()
    
    def get_stat_summary(self) -> str:
        """Get a human-readable summary of all stats."""
        summary_lines = [f"Level {self.level} Pokemon Stats:"]
        
        for stat_type in StatType:
            stat_value = self.get_stat(stat_type)
            base_value = self.base_stats.get_stat(stat_type)
            ev_value = self.evs.get_stat(stat_type)
            iv_value = self.ivs.get_stat(stat_type)
            
            summary_lines.append(
                f"{stat_type.value.capitalize()}: {stat_value} "
                f"(Base: {base_value}, EV: {ev_value}, IV: {iv_value})"
            )
        
        return "\n".join(summary_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary for serialization."""
        return {
            'level': self.level,
            'base_stats': {
                'hp': self.base_stats.hp,
                'attack': self.base_stats.attack,
                'defense': self.base_stats.defense,
                'special_attack': self.base_stats.special_attack,
                'special_defense': self.base_stats.special_defense,
                'speed': self.base_stats.speed
            },
            'evs': {
                'hp': self.evs.hp,
                'attack': self.evs.attack,
                'defense': self.evs.defense,
                'special_attack': self.evs.special_attack,
                'special_defense': self.evs.special_defense,
                'speed': self.evs.speed
            },
            'ivs': {
                'hp': self.ivs.hp,
                'attack': self.ivs.attack,
                'defense': self.ivs.defense,
                'special_attack': self.ivs.special_attack,
                'special_defense': self.ivs.special_defense,
                'speed': self.ivs.speed
            },
            'calculated_stats': {
                'hp': self.stats[StatType.HP],
                'attack': self.stats[StatType.ATTACK],
                'defense': self.stats[StatType.DEFENSE],
                'special_attack': self.stats[StatType.SPECIAL_ATTACK],
                'special_defense': self.stats[StatType.SPECIAL_DEFENSE],
                'speed': self.stats[StatType.SPEED]
            },
            'nature_modifiers': {
                stat.value: modifier for stat, modifier in self.nature_modifiers.items()
            }
        }
    
    def __str__(self) -> str:
        """String representation of stats."""
        return f"Level {self.level} Pokemon - HP: {self.get_stat(StatType.HP)}, Atk: {self.get_stat(StatType.ATTACK)}, Def: {self.get_stat(StatType.DEFENSE)}"
    
    def __repr__(self) -> str:
        """Detailed representation of stats."""
        return f"Stats(level={self.level}, total={self.get_total_stats()})"


# Utility functions for stat operations
def calculate_stat_value(
    base_stat: int,
    level: int,
    ev: int,
    iv: int,
    nature_modifier: float = 1.0,
    is_hp: bool = False
) -> int:
    """
    Calculate a single stat value.
    
    Args:
        base_stat: Base stat value
        level: Pokemon level
        ev: Effort Value
        iv: Individual Value
        nature_modifier: Nature modifier (1.0 for neutral)
        is_hp: Whether this is the HP stat
        
    Returns:
        Calculated stat value
    """
    if is_hp:
        # HP formula
        stat_value = int(((2 * base_stat + iv + ev // 4) * level) // 100 + level + 10)
    else:
        # Other stats formula
        stat_value = int(((2 * base_stat + iv + ev // 4) * level) // 100 + 5)
        stat_value = int(stat_value * nature_modifier)
    
    return stat_value


def get_nature_modifiers(nature: str) -> Dict[StatType, float]:
    """
    Get stat modifiers for a specific nature.
    
    Args:
        nature: Nature name (lowercase)
        
    Returns:
        Dictionary of stat: modifier pairs
    """
    nature_modifiers = {
        'hardy': {},
        'lonely': {StatType.ATTACK: 1.1, StatType.DEFENSE: 0.9},
        'brave': {StatType.ATTACK: 1.1, StatType.SPEED: 0.9},
        'adamant': {StatType.ATTACK: 1.1, StatType.SPECIAL_ATTACK: 0.9},
        'naughty': {StatType.ATTACK: 1.1, StatType.SPECIAL_DEFENSE: 0.9},
        'bold': {StatType.DEFENSE: 1.1, StatType.ATTACK: 0.9},
        'docile': {},
        'relaxed': {StatType.DEFENSE: 1.1, StatType.SPEED: 0.9},
        'impish': {StatType.DEFENSE: 1.1, StatType.SPECIAL_ATTACK: 0.9},
        'lax': {StatType.DEFENSE: 1.1, StatType.SPECIAL_DEFENSE: 0.9},
        'timid': {StatType.SPEED: 1.1, StatType.ATTACK: 0.9},
        'hasty': {StatType.SPEED: 1.1, StatType.DEFENSE: 0.9},
        'serious': {},
        'jolly': {StatType.SPEED: 1.1, StatType.SPECIAL_ATTACK: 0.9},
        'naive': {StatType.SPEED: 1.1, StatType.SPECIAL_DEFENSE: 0.9},
        'modest': {StatType.SPECIAL_ATTACK: 1.1, StatType.ATTACK: 0.9},
        'mild': {StatType.SPECIAL_ATTACK: 1.1, StatType.DEFENSE: 0.9},
        'quiet': {StatType.SPECIAL_ATTACK: 1.1, StatType.SPEED: 0.9},
        'bashful': {},
        'rash': {StatType.SPECIAL_ATTACK: 1.1, StatType.SPECIAL_DEFENSE: 0.9},
        'calm': {StatType.SPECIAL_DEFENSE: 1.1, StatType.ATTACK: 0.9},
        'gentle': {StatType.SPECIAL_DEFENSE: 1.1, StatType.DEFENSE: 0.9},
        'sassy': {StatType.SPECIAL_DEFENSE: 1.1, StatType.SPEED: 0.9},
        'careful': {StatType.SPECIAL_DEFENSE: 1.1, StatType.SPECIAL_ATTACK: 0.9},
        'quirky': {}
    }
    
    return nature_modifiers.get(nature.lower(), {})


def validate_ev_allocation(evs: Dict[StatType, int]) -> bool:
    """
    Validate EV allocation.
    
    Args:
        evs: Dictionary of stat: EV pairs
        
    Returns:
        True if allocation is valid
    """
    total_evs = sum(evs.values())
    
    if total_evs > 510:
        return False
    
    for ev_value in evs.values():
        if ev_value < 0 or ev_value > 255:
            return False
    
    return True


def validate_iv_allocation(ivs: Dict[StatType, int]) -> bool:
    """
    Validate IV allocation.
    
    Args:
        ivs: Dictionary of stat: IV pairs
        
    Returns:
        True if allocation is valid
    """
    for iv_value in ivs.values():
        if iv_value < 0 or iv_value > 31:
            return False
    
    return True
