"""
Core Pokemon mechanics and base classes.
Contains the fundamental Pokemon data structures and battle mechanics.
"""

from .pokemon import Pokemon, ShadowPokemon
from .stats import Stats, EV, IV
from .moves import Move, MoveCategory
from .abilities import Ability
from .types import PokemonType, TypeEffectiveness

__all__ = [
    'Pokemon', 'ShadowPokemon',
    'Stats', 'EV', 'IV',
    'Move', 'MoveCategory',
    'Ability',
    'PokemonType', 'TypeEffectiveness'
]
