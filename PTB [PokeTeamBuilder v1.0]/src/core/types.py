"""
Pokemon types system with comprehensive type effectiveness calculations.
Includes support for all generations including GameCube era Shadow types.
"""

from typing import List, Dict, Tuple
from enum import Enum
import json


class PokemonType(Enum):
    """All Pokemon types including GameCube era Shadow type."""
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"
    SHADOW = "shadow"  # GameCube era specific


class TypeEffectiveness:
    """Comprehensive type effectiveness calculator with all generations."""
    
    # Complete type effectiveness chart (Gen 1-9 + GameCube Shadow)
    TYPE_CHART = {
        PokemonType.NORMAL: {
            PokemonType.ROCK: 0.5,
            PokemonType.GHOST: 0.0,
            PokemonType.STEEL: 0.5
        },
        PokemonType.FIRE: {
            PokemonType.FIRE: 0.5,
            PokemonType.WATER: 0.5,
            PokemonType.GRASS: 2.0,
            PokemonType.ICE: 2.0,
            PokemonType.BUG: 2.0,
            PokemonType.ROCK: 0.5,
            PokemonType.DRAGON: 0.5,
            PokemonType.STEEL: 2.0
        },
        PokemonType.WATER: {
            PokemonType.FIRE: 2.0,
            PokemonType.WATER: 0.5,
            PokemonType.GRASS: 0.5,
            PokemonType.GROUND: 2.0,
            PokemonType.ROCK: 2.0,
            PokemonType.DRAGON: 0.5
        },
        PokemonType.ELECTRIC: {
            PokemonType.WATER: 2.0,
            PokemonType.ELECTRIC: 0.5,
            PokemonType.GRASS: 0.5,
            PokemonType.GROUND: 0.0,
            PokemonType.FLYING: 2.0,
            PokemonType.DRAGON: 0.5
        },
        PokemonType.GRASS: {
            PokemonType.FIRE: 0.5,
            PokemonType.WATER: 2.0,
            PokemonType.GRASS: 0.5,
            PokemonType.POISON: 0.5,
            PokemonType.GROUND: 2.0,
            PokemonType.FLYING: 0.5,
            PokemonType.BUG: 0.5,
            PokemonType.ROCK: 2.0,
            PokemonType.DRAGON: 0.5,
            PokemonType.STEEL: 0.5
        },
        PokemonType.ICE: {
            PokemonType.FIRE: 0.5,
            PokemonType.WATER: 0.5,
            PokemonType.GRASS: 2.0,
            PokemonType.ICE: 0.5,
            PokemonType.GROUND: 2.0,
            PokemonType.FLYING: 2.0,
            PokemonType.DRAGON: 2.0,
            PokemonType.STEEL: 0.5
        },
        PokemonType.FIGHTING: {
            PokemonType.NORMAL: 2.0,
            PokemonType.ICE: 2.0,
            PokemonType.POISON: 0.5,
            PokemonType.GROUND: 0.5,
            PokemonType.FLYING: 0.5,
            PokemonType.PSYCHIC: 0.5,
            PokemonType.BUG: 0.5,
            PokemonType.ROCK: 2.0,
            PokemonType.GHOST: 0.0,
            PokemonType.STEEL: 2.0,
            PokemonType.FAIRY: 0.5
        },
        PokemonType.POISON: {
            PokemonType.GRASS: 2.0,
            PokemonType.POISON: 0.5,
            PokemonType.GROUND: 0.5,
            PokemonType.ROCK: 0.5,
            PokemonType.GHOST: 0.5,
            PokemonType.STEEL: 0.0,
            PokemonType.FAIRY: 2.0
        },
        PokemonType.GROUND: {
            PokemonType.FIRE: 2.0,
            PokemonType.ELECTRIC: 2.0,
            PokemonType.GRASS: 0.5,
            PokemonType.POISON: 2.0,
            PokemonType.FLYING: 0.0,
            PokemonType.BUG: 0.5,
            PokemonType.ROCK: 2.0,
            PokemonType.STEEL: 2.0
        },
        PokemonType.FLYING: {
            PokemonType.ELECTRIC: 0.5,
            PokemonType.GRASS: 2.0,
            PokemonType.FIGHTING: 2.0,
            PokemonType.BUG: 2.0,
            PokemonType.ROCK: 0.5,
            PokemonType.STEEL: 0.5
        },
        PokemonType.PSYCHIC: {
            PokemonType.FIGHTING: 2.0,
            PokemonType.POISON: 2.0,
            PokemonType.PSYCHIC: 0.5,
            PokemonType.DARK: 0.0,
            PokemonType.STEEL: 0.5
        },
        PokemonType.BUG: {
            PokemonType.FIRE: 0.5,
            PokemonType.GRASS: 2.0,
            PokemonType.FIGHTING: 0.5,
            PokemonType.POISON: 0.5,
            PokemonType.FLYING: 0.5,
            PokemonType.PSYCHIC: 2.0,
            PokemonType.GHOST: 0.5,
            PokemonType.STEEL: 0.5,
            PokemonType.FAIRY: 0.5
        },
        PokemonType.ROCK: {
            PokemonType.FIRE: 2.0,
            PokemonType.ICE: 2.0,
            PokemonType.FIGHTING: 0.5,
            PokemonType.GROUND: 0.5,
            PokemonType.FLYING: 2.0,
            PokemonType.BUG: 2.0,
            PokemonType.STEEL: 0.5
        },
        PokemonType.GHOST: {
            PokemonType.NORMAL: 0.0,
            PokemonType.PSYCHIC: 2.0,
            PokemonType.GHOST: 2.0,
            PokemonType.DARK: 0.5
        },
        PokemonType.DRAGON: {
            PokemonType.DRAGON: 2.0,
            PokemonType.STEEL: 0.5,
            PokemonType.FAIRY: 0.0
        },
        PokemonType.DARK: {
            PokemonType.FIGHTING: 0.5,
            PokemonType.PSYCHIC: 2.0,
            PokemonType.GHOST: 2.0,
            PokemonType.DARK: 0.5,
            PokemonType.FAIRY: 0.5
        },
        PokemonType.STEEL: {
            PokemonType.FIRE: 0.5,
            PokemonType.WATER: 0.5,
            PokemonType.ELECTRIC: 0.5,
            PokemonType.ICE: 2.0,
            PokemonType.ROCK: 2.0,
            PokemonType.STEEL: 0.5,
            PokemonType.FAIRY: 2.0
        },
        PokemonType.FAIRY: {
            PokemonType.FIGHTING: 2.0,
            PokemonType.POISON: 0.5,
            PokemonType.DRAGON: 2.0,
            PokemonType.DARK: 2.0,
            PokemonType.STEEL: 0.5
        },
        # GameCube era Shadow type
        PokemonType.SHADOW: {
            PokemonType.NORMAL: 1.5,
            PokemonType.PSYCHIC: 2.0,
            PokemonType.GHOST: 1.5,
            PokemonType.DARK: 0.5,
            PokemonType.SHADOW: 0.5  # Shadow vs Shadow is not very effective
        }
    }
    
    @classmethod
    def calculate_effectiveness(
        cls,
        attack_type: PokemonType,
        defender_types: List[PokemonType]
    ) -> Tuple[float, List[str]]:
        """
        Calculate type effectiveness of an attack against defender types.
        
        Args:
            attack_type: Type of the attacking move
            defender_types: List of defender's types (can be 1 or 2)
            
        Returns:
            Tuple of (effectiveness_multiplier, effectiveness_description)
        """
        if not defender_types:
            return 1.0, ["No type information"]
        
        total_effectiveness = 1.0
        effectiveness_descriptions = []
        
        for defender_type in defender_types:
            if attack_type in cls.TYPE_CHART and defender_type in cls.TYPE_CHART[attack_type]:
                multiplier = cls.TYPE_CHART[attack_type][defender_type]
                total_effectiveness *= multiplier
                
                if multiplier == 0.0:
                    effectiveness_descriptions.append(f"It has no effect on {defender_type.value} types")
                elif multiplier == 0.5:
                    effectiveness_descriptions.append(f"It's not very effective against {defender_type.value} types")
                elif multiplier == 2.0:
                    effectiveness_descriptions.append(f"It's super effective against {defender_type.value} types")
                else:
                    effectiveness_descriptions.append(f"Normal effectiveness against {defender_type.value} types")
            else:
                effectiveness_descriptions.append(f"Normal effectiveness against {defender_type.value} types")
        
        return total_effectiveness, effectiveness_descriptions
    
    @classmethod
    def get_effectiveness_text(cls, effectiveness: float) -> str:
        """
        Get human-readable text for effectiveness values.
        
        Args:
            effectiveness: Effectiveness multiplier
            
        Returns:
            Human-readable effectiveness description
        """
        if effectiveness == 0.0:
            return "No Effect"
        elif effectiveness < 0.5:
            return "Very Ineffective"
        elif effectiveness < 1.0:
            return "Not Very Effective"
        elif effectiveness == 1.0:
            return "Normal"
        elif effectiveness < 2.0:
            return "Super Effective"
        elif effectiveness < 4.0:
            return "Very Effective"
        else:
            return "Extremely Effective"
    
    @classmethod
    def get_weaknesses(cls, pokemon_types: List[PokemonType]) -> Dict[PokemonType, float]:
        """
        Get all weaknesses for a Pokemon with given types.
        
        Args:
            pokemon_types: List of Pokemon's types
            
        Returns:
            Dictionary of type: effectiveness for all attacking types
        """
        weaknesses = {}
        
        for attack_type in PokemonType:
            effectiveness, _ = cls.calculate_effectiveness(attack_type, pokemon_types)
            if effectiveness > 1.0:
                weaknesses[attack_type] = effectiveness
        
        return weaknesses
    
    @classmethod
    def get_resistances(cls, pokemon_types: List[PokemonType]) -> Dict[PokemonType, float]:
        """
        Get all resistances for a Pokemon with given types.
        
        Args:
            pokemon_types: List of Pokemon's types
            
        Returns:
            Dictionary of type: effectiveness for all attacking types
        """
        resistances = {}
        
        for attack_type in PokemonType:
            effectiveness, _ = cls.calculate_effectiveness(attack_type, pokemon_types)
            if effectiveness < 1.0 and effectiveness > 0.0:
                resistances[attack_type] = effectiveness
        
        return resistances
    
    @classmethod
    def get_immunities(cls, pokemon_types: List[PokemonType]) -> List[PokemonType]:
        """
        Get all immunities for a Pokemon with given types.
        
        Args:
            pokemon_types: List of Pokemon's types
            
        Returns:
            List of types that have no effect
        """
        immunities = []
        
        for attack_type in PokemonType:
            effectiveness, _ = cls.calculate_effectiveness(attack_type, pokemon_types)
            if effectiveness == 0.0:
                immunities.append(attack_type)
        
        return immunities
    
    @classmethod
    def get_type_combinations(cls) -> List[Tuple[PokemonType, PokemonType]]:
        """
        Get all possible dual-type combinations.
        
        Returns:
            List of valid dual-type combinations
        """
        combinations = []
        types_list = list(PokemonType)
        
        for i, type1 in enumerate(types_list):
            for type2 in types_list[i+1:]:
                combinations.append((type1, type2))
        
        return combinations
    
    @classmethod
    def get_best_offensive_types(cls) -> List[PokemonType]:
        """
        Get types that are super effective against the most other types.
        
        Returns:
            List of types ordered by offensive effectiveness
        """
        type_scores = {}
        
        for attack_type in PokemonType:
            score = 0
            for defender_type in PokemonType:
                if attack_type in cls.TYPE_CHART and defender_type in cls.TYPE_CHART[attack_type]:
                    if cls.TYPE_CHART[attack_type][defender_type] > 1.0:
                        score += 1
            
            type_scores[attack_type] = score
        
        # Sort by score (highest first)
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        return [pokemon_type for pokemon_type, _ in sorted_types]
    
    @classmethod
    def get_best_defensive_types(cls) -> List[PokemonType]:
        """
        Get types that resist the most other types.
        
        Returns:
            List of types ordered by defensive effectiveness
        """
        type_scores = {}
        
        for defender_type in PokemonType:
            score = 0
            for attack_type in PokemonType:
                if attack_type in cls.TYPE_CHART and defender_type in cls.TYPE_CHART[attack_type]:
                    if cls.TYPE_CHART[attack_type][defender_type] < 1.0:
                        score += 1
            
            type_scores[defender_type] = score
        
        # Sort by score (highest first)
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        return [pokemon_type for pokemon_type, _ in sorted_types]
    
    @classmethod
    def is_shadow_type_legal(cls, game_era: str) -> bool:
        """
        Check if Shadow type is legal in the specified game era.
        
        Args:
            game_era: Target game era
            
        Returns:
            True if Shadow type is legal
        """
        shadow_legal_eras = ["gamecube", "ds", "3ds", "switch"]
        return game_era in shadow_legal_eras
    
    @classmethod
    def get_era_supported_types(cls, game_era: str) -> List[PokemonType]:
        """
        Get all types supported in the specified game era.
        
        Args:
            game_era: Target game era
            
        Returns:
            List of supported types
        """
        all_types = list(PokemonType)
        
        if not cls.is_shadow_type_legal(game_era):
            all_types.remove(PokemonType.SHADOW)
        
        return all_types


# Utility functions for type operations
def get_type_from_string(type_string: str) -> PokemonType:
    """
    Convert string to PokemonType enum.
    
    Args:
        type_string: String representation of type
        
    Returns:
        PokemonType enum value
        
    Raises:
        ValueError: If type string is invalid
    """
    try:
        return PokemonType(type_string.lower())
    except ValueError:
        raise ValueError(f"Invalid Pokemon type: {type_string}")


def get_types_from_strings(type_strings: List[str]) -> List[PokemonType]:
    """
    Convert list of strings to PokemonType enums.
    
    Args:
        type_strings: List of string representations of types
        
    Returns:
        List of PokemonType enum values
        
    Raises:
        ValueError: If any type string is invalid
    """
    return [get_type_from_string(type_str) for type_str in type_strings]


def get_type_effectiveness_summary(attack_type: PokemonType, defender_types: List[PokemonType]) -> str:
    """
    Get a summary of type effectiveness.
    
    Args:
        attack_type: Type of the attacking move
        defender_types: List of defender's types
        
    Returns:
        Human-readable effectiveness summary
    """
    effectiveness, descriptions = TypeEffectiveness.calculate_effectiveness(attack_type, defender_types)
    effectiveness_text = TypeEffectiveness.get_effectiveness_text(effectiveness)
    
    summary = f"{attack_type.value.capitalize()} vs {', '.join([t.value for t in defender_types])}: {effectiveness_text} (x{effectiveness})"
    
    if descriptions:
        summary += f"\nDetails: {'; '.join(descriptions)}"
    
    return summary
