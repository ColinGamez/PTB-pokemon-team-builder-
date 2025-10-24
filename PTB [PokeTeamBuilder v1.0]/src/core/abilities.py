"""
Pokemon abilities system with comprehensive validation and game era support.
Includes abilities from all generations and special GameCube era mechanics.
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json


class AbilityCategory(Enum):
    """Ability categories for organization."""
    BATTLE = "battle"           # Battle-related effects
    FIELD = "field"             # Field/weather effects
    STAT_MODIFIER = "stat_modifier"  # Stat boosting/reducing
    STATUS = "status"           # Status condition effects
    MOVES = "moves"             # Move-related effects
    SPECIAL = "special"         # Unique/era-specific abilities


class AbilityTrigger(Enum):
    """When abilities activate."""
    ALWAYS = "always"           # Always active
    ON_ENTRY = "on_entry"       # When Pokemon enters battle
    ON_ATTACK = "on_attack"     # When Pokemon attacks
    ON_DEFEND = "on_defend"     # When Pokemon is attacked
    ON_FAINT = "on_faint"       # When Pokemon faints
    ON_WEATHER = "on_weather"   # Weather-dependent
    ON_STATUS = "on_status"     # Status-dependent


@dataclass
class AbilityEffect:
    """Ability effects and mechanics."""
    effect_type: str
    effect_value: float = 1.0
    effect_description: str = ""
    trigger: AbilityTrigger = AbilityTrigger.ALWAYS
    condition: Optional[str] = None  # Special condition for activation
    
    def __post_init__(self):
        """Validate effect parameters."""
        if not isinstance(self.effect_type, str) or not self.effect_type.strip():
            raise ValueError("Effect type must be a non-empty string")
        
        if not isinstance(self.effect_value, (int, float)):
            raise ValueError("Effect value must be a number")
        
        if not isinstance(self.effect_description, str):
            raise ValueError("Effect description must be a string")
        
        if not isinstance(self.trigger, AbilityTrigger):
            raise ValueError("Trigger must be a valid AbilityTrigger enum value")


class Ability:
    """Comprehensive Pokemon ability class with validation."""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: AbilityCategory,
        effects: Optional[List[AbilityEffect]] = None,
        game_era: str = "modern",
        is_hidden: bool = False,
        is_gamecube_specific: bool = False,
        activation_function: Optional[Callable] = None
    ):
        """
        Initialize a Pokemon ability with comprehensive validation.
        
        Args:
            name: Ability name
            description: Ability description
            category: Ability category
            effects: List of ability effects
            game_era: Game generation this ability is from
            is_hidden: Whether this is a hidden ability
            is_gamecube_specific: Whether this is GameCube era specific
            activation_function: Custom function for complex ability logic
        """
        # Validate basic parameters
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Ability name must be a non-empty string")
        
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Ability description must be a non-empty string")
        
        if not isinstance(category, AbilityCategory):
            raise ValueError("Category must be a valid AbilityCategory enum value")
        
        if not isinstance(game_era, str) or not game_era.strip():
            raise ValueError("Game era must be a non-empty string")
        
        if not isinstance(is_hidden, bool):
            raise ValueError("is_hidden must be a boolean")
        
        if not isinstance(is_gamecube_specific, bool):
            raise ValueError("is_gamecube_specific must be a boolean")
        
        # Set basic properties
        self.name = name.strip()
        self.description = description.strip()
        self.category = category
        self.game_era = game_era.strip()
        self.is_hidden = is_hidden
        self.is_gamecube_specific = is_gamecube_specific
        self.activation_function = activation_function
        
        # Set effects with validation
        if effects is None:
            effects = []
        if not isinstance(effects, list):
            raise ValueError("Effects must be a list")
        
        # Validate each effect
        for effect in effects:
            if not isinstance(effect, AbilityEffect):
                raise ValueError("Each effect must be an AbilityEffect instance")
        
        self.effects = effects
        
        # Validate ability consistency
        self._validate_ability_consistency()
    
    def _validate_ability_consistency(self):
        """Validate ability parameters for consistency."""
        # GameCube specific abilities should be from GameCube era
        if self.is_gamecube_specific and self.game_era != "gamecube":
            raise ValueError("GameCube specific abilities must be from GameCube era")
    
    def is_legal_for_era(self, target_era: str) -> bool:
        """
        Check if this ability is legal for the specified game era.
        
        Args:
            target_era: Target game era
            
        Returns:
            True if ability is legal for the era
        """
        # Era-specific ability legality
        era_restrictions = {
            "gamecube": ["gamecube"],  # GameCube era only
            "ds": ["gamecube", "ds"],  # DS era includes GameCube
            "3ds": ["gamecube", "ds", "3ds"],  # 3DS era includes previous
            "switch": ["gamecube", "ds", "3ds", "switch"]  # Switch era includes all
        }
        
        if target_era not in era_restrictions:
            return False
        
        # Check if ability era is allowed in target era
        if self.game_era not in era_restrictions[target_era]:
            return False
        
        return True
    
    def activate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activate the ability with given context.
        
        Args:
            context: Battle context (Pokemon, opponent, weather, etc.)
            
        Returns:
            Modified context with ability effects applied
        """
        if self.activation_function:
            return self.activation_function(context)
        
        # Default activation logic
        modified_context = context.copy()
        
        for effect in self.effects:
            modified_context = self._apply_effect(effect, modified_context)
        
        return modified_context
    
    def _apply_effect(self, effect: AbilityEffect, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a single ability effect to the context.
        
        Args:
            effect: Ability effect to apply
            context: Current battle context
            
        Returns:
            Modified context
        """
        modified_context = context.copy()
        
        if effect.effect_type == "stat_boost":
            # Apply stat boosting
            if "attacker_stats" in modified_context:
                stat_name = effect.condition or "attack"
                if stat_name in modified_context["attacker_stats"]:
                    modified_context["attacker_stats"][stat_name] *= effect.effect_value
        
        elif effect.effect_type == "type_immunity":
            # Grant type immunity
            if "defender_immunities" not in modified_context:
                modified_context["defender_immunities"] = []
            modified_context["defender_immunities"].append(effect.condition)
        
        elif effect.effect_type == "weather_boost":
            # Weather-based stat boost
            if "weather" in modified_context and modified_context["weather"] == effect.condition:
                if "attacker_stats" in modified_context:
                    for stat in ["attack", "special_attack"]:
                        if stat in modified_context["attacker_stats"]:
                            modified_context["attacker_stats"][stat] *= effect.effect_value
        
        return modified_context
    
    def get_effect_summary(self) -> str:
        """
        Get a summary of the ability's effects.
        
        Returns:
            Human-readable effect summary
        """
        if not self.effects:
            return "No specific effects"
        
        effect_descriptions = []
        for effect in self.effects:
            if effect.effect_value != 1.0:
                effect_descriptions.append(f"{effect.effect_type}: {effect.effect_value}x")
            else:
                effect_descriptions.append(effect.effect_type)
        
        return f"Effects: {', '.join(effect_descriptions)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ability to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'game_era': self.game_era,
            'is_hidden': self.is_hidden,
            'is_gamecube_specific': self.is_gamecube_specific,
            'effects': [effect.__dict__ for effect in self.effects]
        }
    
    def __str__(self) -> str:
        """String representation of the ability."""
        hidden_text = " (Hidden)" if self.is_hidden else ""
        return f"{self.name}{hidden_text} - {self.category.value}"
    
    def __repr__(self) -> str:
        """Detailed representation of the ability."""
        return f"Ability(name='{self.name}', category={self.category.value}, era={self.game_era})"


# Predefined abilities for different eras
class StandardAbilities:
    """Standard abilities available in most games."""
    
    @staticmethod
    def create_standard_abilities() -> Dict[str, Ability]:
        """Create standard abilities dictionary."""
        abilities = {}
        
        # Basic stat-boosting abilities
        abilities["Intimidate"] = Ability(
            name="Intimidate",
            description="Lowers the opponent's Attack stat when this Pokemon enters battle",
            category=AbilityCategory.STAT_MODIFIER,
            effects=[
                AbilityEffect(
                    effect_type="stat_reduction",
                    effect_value=0.67,
                    effect_description="Reduces opponent's Attack by 33%",
                    trigger=AbilityTrigger.ON_ENTRY
                )
            ],
            game_era="modern"
        )
        
        abilities["Levitate"] = Ability(
            name="Levitate",
            description="This Pokemon is immune to Ground-type moves",
            category=AbilityCategory.STATUS,
            effects=[
                AbilityEffect(
                    effect_type="type_immunity",
                    effect_value=0.0,
                    effect_description="Immune to Ground-type moves",
                    trigger=AbilityTrigger.ALWAYS,
                    condition="ground"
                )
            ],
            game_era="modern"
        )
        
        abilities["Swift Swim"] = Ability(
            name="Swift Swim",
            description="Doubles Speed in rain",
            category=AbilityCategory.FIELD,
            effects=[
                AbilityEffect(
                    effect_type="weather_boost",
                    effect_value=2.0,
                    effect_description="Speed doubled in rain",
                    trigger=AbilityTrigger.ON_WEATHER,
                    condition="rain"
                )
            ],
            game_era="modern"
        )
        
        return abilities


class GameCubeAbilities:
    """GameCube era specific abilities."""
    
    @staticmethod
    def create_gamecube_abilities() -> Dict[str, Ability]:
        """Create GameCube era abilities dictionary."""
        abilities = {}
        
        # Shadow-specific abilities
        abilities["Shadow Boost"] = Ability(
            name="Shadow Boost",
            description="Increases the power of Shadow moves by 50%",
            category=AbilityCategory.MOVES,
            effects=[
                AbilityEffect(
                    effect_type="move_power_boost",
                    effect_value=1.5,
                    effect_description="Shadow moves deal 50% more damage",
                    trigger=AbilityTrigger.ON_ATTACK,
                    condition="shadow_move"
                )
            ],
            game_era="gamecube",
            is_gamecube_specific=True
        )
        
        abilities["Purification"] = Ability(
            name="Purification",
            description="Gradually purifies Shadow Pokemon in battle",
            category=AbilityCategory.SPECIAL,
            effects=[
                AbilityEffect(
                    effect_type="purification_progress",
                    effect_value=0.1,
                    effect_description="Increases purification progress each turn",
                    trigger=AbilityTrigger.ON_ATTACK
                )
            ],
            game_era="gamecube",
            is_gamecube_specific=True
        )
        
        abilities["Shadow Shield"] = Ability(
            name="Shadow Shield",
            description="Reduces damage from non-Shadow moves by 25%",
            category=AbilityCategory.STAT_MODIFIER,
            effects=[
                AbilityEffect(
                    effect_type="damage_reduction",
                    effect_value=0.75,
                    effect_description="Takes 25% less damage from non-Shadow moves",
                    trigger=AbilityTrigger.ON_DEFEND,
                    condition="non_shadow_move"
                )
            ],
            game_era="gamecube",
            is_gamecube_specific=True
        )
        
        return abilities


# Global abilities registry
ABILITIES_REGISTRY = {}

def initialize_abilities():
    """Initialize the global abilities registry."""
    global ABILITIES_REGISTRY
    
    # Add standard abilities
    ABILITIES_REGISTRY.update(StandardAbilities.create_standard_abilities())
    
    # Add GameCube era abilities
    ABILITIES_REGISTRY.update(GameCubeAbilities.create_gamecube_abilities())


def get_ability(name: str) -> Optional[Ability]:
    """
    Get an ability by name from the registry.
    
    Args:
        name: Ability name
        
    Returns:
        Ability instance or None if not found
    """
    return ABILITIES_REGISTRY.get(name)


def get_abilities_by_era(game_era: str) -> List[Ability]:
    """
    Get all abilities legal for the specified game era.
    
    Args:
        game_era: Target game era
        
    Returns:
        List of legal abilities
    """
    return [ability for ability in ABILITIES_REGISTRY.values() if ability.is_legal_for_era(game_era)]


def get_abilities_by_category(category: AbilityCategory) -> List[Ability]:
    """
    Get all abilities of a specific category.
    
    Args:
        category: Ability category
        
    Returns:
        List of abilities in the category
    """
    return [ability for ability in ABILITIES_REGISTRY.values() if ability.category == category]


# Initialize abilities when module is imported
initialize_abilities()
