#!/usr/bin/env python3
"""
Pokemon Breeding & Genetics System
Advanced breeding mechanics including IV inheritance, egg moves, abilities, and shiny hunting.
"""

import random
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import math

from ..core.pokemon import Pokemon, PokemonNature
from ..core.stats import IV, EV, BaseStats
from ..core.types import PokemonType


class BreedingItem(Enum):
    """Items that affect breeding."""
    EVERSTONE = "everstone"  # Passes down nature
    DESTINY_KNOT = "destiny_knot"  # Passes down 5 IVs
    POWER_WEIGHT = "power_weight"  # Passes down HP IV
    POWER_BRACER = "power_bracer"  # Passes down Attack IV
    POWER_BELT = "power_belt"  # Passes down Defense IV
    POWER_LENS = "power_lens"  # Passes down Sp. Atk IV
    POWER_BAND = "power_band"  # Passes down Sp. Def IV
    POWER_ANKLET = "power_anklet"  # Passes down Speed IV


class EggGroup(Enum):
    """Pokemon egg groups."""
    MONSTER = "monster"
    WATER_1 = "water_1"
    BUG = "bug"
    FLYING = "flying"
    FIELD = "field"
    FAIRY = "fairy"
    GRASS = "grass"
    HUMAN_LIKE = "human_like"
    WATER_3 = "water_3"
    MINERAL = "mineral"
    AMORPHOUS = "amorphous"
    WATER_2 = "water_2"
    DITTO = "ditto"
    DRAGON = "dragon"
    UNDISCOVERED = "undiscovered"


@dataclass
class BreedingPair:
    """A pair of Pokemon for breeding."""
    parent1: Pokemon
    parent2: Pokemon
    item1: Optional[BreedingItem] = None
    item2: Optional[BreedingItem] = None
    compatibility: float = 0.0
    egg_group1: EggGroup = EggGroup.FIELD
    egg_group2: EggGroup = EggGroup.FIELD


@dataclass
class Egg:
    """A Pokemon egg."""
    species_id: int
    species_name: str
    moves: List[str]
    nature: PokemonNature
    ability: str
    ivs: IV
    is_shiny: bool = False
    steps_to_hatch: int = 0
    total_steps: int = 0


@dataclass
class BreedingResult:
    """Result of a breeding attempt."""
    success: bool
    egg: Optional[Egg] = None
    message: str = ""
    compatibility_score: float = 0.0
    iv_inheritance: Dict[str, str] = None
    move_inheritance: List[str] = None


class PokemonBreedingSystem:
    """Advanced Pokemon breeding system with genetics and inheritance."""
    
    def __init__(self):
        self.breeding_pairs: List[BreedingPair] = []
        self.eggs: List[Egg] = []
        self.breeding_history: List[BreedingResult] = []
        self.shiny_charm_active = False
        self.masuda_method_active = False
        
        # Breeding compatibility matrix
        self.compatibility_matrix = {
            EggGroup.MONSTER: [EggGroup.MONSTER, EggGroup.DRAGON],
            EggGroup.WATER_1: [EggGroup.WATER_1, EggGroup.WATER_2, EggGroup.WATER_3],
            EggGroup.BUG: [EggGroup.BUG],
            EggGroup.FLYING: [EggGroup.FLYING, EggGroup.WATER_1, EggGroup.WATER_2],
            EggGroup.FIELD: [EggGroup.FIELD, EggGroup.HUMAN_LIKE, EggGroup.FAIRY],
            EggGroup.FAIRY: [EggGroup.FAIRY, EggGroup.FIELD],
            EggGroup.GRASS: [EggGroup.GRASS],
            EggGroup.HUMAN_LIKE: [EggGroup.HUMAN_LIKE, EggGroup.FIELD],
            EggGroup.WATER_3: [EggGroup.WATER_3, EggGroup.WATER_1],
            EggGroup.MINERAL: [EggGroup.MINERAL],
            EggGroup.AMORPHOUS: [EggGroup.AMORPHOUS],
            EggGroup.WATER_2: [EggGroup.WATER_2, EggGroup.WATER_1, EggGroup.WATER_3],
            EggGroup.DITTO: [EggGroup.MONSTER, EggGroup.WATER_1, EggGroup.BUG, EggGroup.FLYING,
                           EggGroup.FIELD, EggGroup.FAIRY, EggGroup.GRASS, EggGroup.HUMAN_LIKE,
                           EggGroup.WATER_3, EggGroup.MINERAL, EggGroup.AMORPHOUS, EggGroup.WATER_2,
                           EggGroup.DRAGON],
            EggGroup.DRAGON: [EggGroup.DRAGON, EggGroup.MONSTER],
            EggGroup.UNDISCOVERED: []  # Cannot breed
        }
        
        # Egg move database (simplified)
        self.egg_moves = {
            25: ["Volt Tackle", "Fake Out", "Encore", "Wish"],  # Pikachu
            6: ["Dragon Dance", "Outrage", "Flare Blitz", "Air Slash"],  # Charizard
            448: ["Bullet Punch", "Vacuum Wave", "Blaze Kick", "High Jump Kick"]  # Lucario
        }
        
        # Ability inheritance rules
        self.ability_inheritance = {
            "normal": 0.8,  # 80% chance for normal ability
            "hidden": 0.2   # 20% chance for hidden ability
        }
    
    def create_breeding_pair(self, parent1: Pokemon, parent2: Pokemon,
                           item1: Optional[BreedingItem] = None,
                           item2: Optional[BreedingItem] = None) -> BreedingPair:
        """Create a breeding pair and calculate compatibility."""
        
        # Determine egg groups (simplified - in reality this would come from Pokemon data)
        egg_group1 = self._get_egg_group(parent1.species_id)
        egg_group2 = self._get_egg_group(parent2.species_id)
        
        # Calculate compatibility
        compatibility = self._calculate_compatibility(egg_group1, egg_group2)
        
        # Check for special breeding conditions
        if parent1.species_id == 132 or parent2.species_id == 132:  # Ditto
            compatibility = 1.0
        
        pair = BreedingPair(
            parent1=parent1,
            parent2=parent2,
            item1=item1,
            item2=item2,
            compatibility=compatibility,
            egg_group1=egg_group1,
            egg_group2=egg_group2
        )
        
        self.breeding_pairs.append(pair)
        return pair
    
    def attempt_breeding(self, pair: BreedingPair) -> BreedingResult:
        """Attempt to breed a pair of Pokemon."""
        
        if pair.compatibility == 0.0:
            return BreedingResult(
                success=False,
                message="These Pokemon cannot breed together."
            )
        
        # Check if breeding is successful (based on compatibility)
        if random.random() > pair.compatibility:
            return BreedingResult(
                success=False,
                message="Breeding attempt failed.",
                compatibility_score=pair.compatibility
            )
        
        # Determine which Pokemon is the mother (determines species)
        mother = pair.parent1 if random.random() < 0.5 else pair.parent2
        father = pair.parent2 if mother == pair.parent1 else pair.parent1
        
        # Create egg
        egg = self._create_egg(mother, father, pair)
        
        # Record breeding result
        result = BreedingResult(
            success=True,
            egg=egg,
            message=f"Successfully bred a {egg.species_name} egg!",
            compatibility_score=pair.compatibility,
            iv_inheritance=self._get_iv_inheritance_log(mother, father, pair),
            move_inheritance=self._get_move_inheritance_log(mother, father)
        )
        
        self.breeding_history.append(result)
        self.eggs.append(egg)
        
        return result
    
    def hatch_egg(self, egg: Egg) -> Pokemon:
        """Hatch an egg into a Pokemon."""
        
        # Create the hatched Pokemon
        hatched_pokemon = Pokemon(
            name=egg.species_name,
            species_id=egg.species_id,
            level=1,
            nature=egg.nature,
            base_stats=self._get_base_stats(egg.species_id),
            evs=EV(hp=0, attack=0, defense=0, special_attack=0, special_defense=0, speed=0),
            ivs=egg.ivs,
            moves=egg.moves,
            is_shiny=egg.is_shiny
        )
        
        # Remove egg from list
        if egg in self.eggs:
            self.eggs.remove(egg)
        
        return hatched_pokemon
    
    def advance_egg_hatching(self, steps: int = 1):
        """Advance egg hatching progress."""
        for egg in self.eggs:
            egg.steps_to_hatch += steps
            egg.total_steps += steps
    
    def get_ready_to_hatch_eggs(self) -> List[Egg]:
        """Get eggs that are ready to hatch."""
        ready_eggs = []
        for egg in self.eggs:
            if egg.steps_to_hatch >= egg.total_steps:
                ready_eggs.append(egg)
        return ready_eggs
    
    def calculate_shiny_chance(self, pair: BreedingPair) -> float:
        """Calculate the chance of getting a shiny Pokemon."""
        base_chance = 1 / 4096  # Base shiny chance
        
        # Shiny Charm (3x multiplier)
        if self.shiny_charm_active:
            base_chance *= 3
        
        # Masuda Method (6x multiplier)
        if self.masuda_method_active:
            base_chance *= 6
        
        return base_chance
    
    def optimize_breeding_for_ivs(self, target_ivs: Dict[str, int]) -> List[BreedingPair]:
        """Find the best breeding pairs to achieve target IVs."""
        optimized_pairs = []
        
        for pair in self.breeding_pairs:
            score = self._calculate_iv_optimization_score(pair, target_ivs)
            if score > 0.7:  # Only include pairs with good optimization potential
                optimized_pairs.append(pair)
        
        # Sort by optimization score
        optimized_pairs.sort(key=lambda p: self._calculate_iv_optimization_score(p, target_ivs), reverse=True)
        
        return optimized_pairs
    
    def get_breeding_statistics(self) -> Dict:
        """Get breeding statistics and history."""
        total_attempts = len(self.breeding_history)
        successful_breeds = sum(1 for result in self.breeding_history if result.success)
        shiny_hatches = sum(1 for result in self.breeding_history 
                           if result.success and result.egg and result.egg.is_shiny)
        
        return {
            'total_attempts': total_attempts,
            'successful_breeds': successful_breeds,
            'success_rate': successful_breeds / max(total_attempts, 1),
            'shiny_hatches': shiny_hatches,
            'shiny_rate': shiny_hatches / max(successful_breeds, 1),
            'current_eggs': len(self.eggs),
            'breeding_pairs': len(self.breeding_pairs)
        }
    
    def _get_egg_group(self, species_id: int) -> EggGroup:
        """Get the egg group for a Pokemon species."""
        # Simplified egg group assignment
        if species_id == 132:  # Ditto
            return EggGroup.DITTO
        elif species_id in [25, 26]:  # Pikachu family
            return EggGroup.FIELD
        elif species_id in [4, 5, 6]:  # Charmander family
            return EggGroup.MONSTER
        elif species_id in [448]:  # Lucario
            return EggGroup.HUMAN_LIKE
        else:
            return EggGroup.FIELD  # Default
    
    def _calculate_compatibility(self, group1: EggGroup, group2: EggGroup) -> float:
        """Calculate breeding compatibility between egg groups."""
        if group1 == EggGroup.UNDISCOVERED or group2 == EggGroup.UNDISCOVERED:
            return 0.0
        
        if group1 == EggGroup.DITTO or group2 == EggGroup.DITTO:
            return 1.0
        
        compatible_groups = self.compatibility_matrix.get(group1, [])
        if group2 in compatible_groups:
            return 1.0
        
        return 0.0
    
    def _create_egg(self, mother: Pokemon, father: Pokemon, pair: BreedingPair) -> Egg:
        """Create an egg with inherited traits."""
        
        # Determine species (usually from mother, except for Ditto)
        if mother.species_id == 132:  # Ditto
            species_id = father.species_id
            species_name = father.name
        else:
            species_id = mother.species_id
            species_name = mother.name
        
        # Inherit IVs
        ivs = self._inherit_ivs(mother, father, pair)
        
        # Inherit nature
        nature = self._inherit_nature(mother, father, pair)
        
        # Inherit moves
        moves = self._inherit_moves(mother, father, species_id)
        
        # Determine ability
        ability = self._inherit_ability(mother, father)
        
        # Determine if shiny
        is_shiny = self._determine_shiny(pair)
        
        # Calculate steps to hatch
        steps_to_hatch = self._calculate_hatch_steps(species_id)
        
        return Egg(
            species_id=species_id,
            species_name=species_name,
            moves=moves,
            nature=nature,
            ability=ability,
            ivs=ivs,
            is_shiny=is_shiny,
            steps_to_hatch=0,
            total_steps=steps_to_hatch
        )
    
    def _inherit_ivs(self, mother: Pokemon, father: Pokemon, pair: BreedingPair) -> IV:
        """Inherit IVs from parents."""
        inherited_ivs = {}
        inheritance_sources = {}
        
        # Determine which IVs to inherit and from whom
        iv_stats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
        
        # Check for Destiny Knot (passes down 5 IVs)
        destiny_knot = pair.item1 == BreedingItem.DESTINY_KNOT or pair.item2 == BreedingItem.DESTINY_KNOT
        num_inherited = 5 if destiny_knot else 3
        
        # Randomly select which IVs to inherit
        inherited_stats = random.sample(iv_stats, num_inherited)
        
        for stat in iv_stats:
            if stat in inherited_stats:
                # Inherit from random parent
                parent = random.choice([mother, father])
                inherited_ivs[stat] = getattr(parent.ivs, stat)
                inheritance_sources[stat] = f"from {parent.name}"
            else:
                # Random IV
                inherited_ivs[stat] = random.randint(0, 31)
                inheritance_sources[stat] = "random"
        
        # Check for Power items (override inheritance)
        power_items = {
            BreedingItem.POWER_WEIGHT: 'hp',
            BreedingItem.POWER_BRACER: 'attack',
            BreedingItem.POWER_BELT: 'defense',
            BreedingItem.POWER_LENS: 'special_attack',
            BreedingItem.POWER_BAND: 'special_defense',
            BreedingItem.POWER_ANKLET: 'speed'
        }
        
        for item, stat in power_items.items():
            if pair.item1 == item:
                inherited_ivs[stat] = getattr(mother.ivs, stat)
                inheritance_sources[stat] = f"from {mother.name} (Power item)"
            elif pair.item2 == item:
                inherited_ivs[stat] = getattr(father.ivs, stat)
                inheritance_sources[stat] = f"from {father.name} (Power item)"
        
        return IV(**inherited_ivs)
    
    def _inherit_nature(self, mother: Pokemon, father: Pokemon, pair: BreedingPair) -> PokemonNature:
        """Inherit nature from parents."""
        # Check for Everstone
        if pair.item1 == BreedingItem.EVERSTONE:
            return mother.nature
        elif pair.item2 == BreedingItem.EVERSTONE:
            return father.nature
        
        # Random nature
        return random.choice(list(PokemonNature))
    
    def _inherit_moves(self, mother: Pokemon, father: Pokemon, species_id: int) -> List[str]:
        """Inherit moves from parents."""
        moves = []
        
        # Level-up moves (simplified)
        level_moves = self._get_level_moves(species_id)
        moves.extend(level_moves[:4])  # First 4 level-up moves
        
        # Egg moves
        egg_moves = self.egg_moves.get(species_id, [])
        if egg_moves:
            # Inherit 1-2 egg moves
            num_egg_moves = random.randint(1, min(2, len(egg_moves)))
            inherited_egg_moves = random.sample(egg_moves, num_egg_moves)
            moves.extend(inherited_egg_moves)
        
        # TM moves (simplified)
        tm_moves = self._get_tm_moves(species_id)
        if tm_moves:
            num_tm_moves = random.randint(0, min(2, len(tm_moves)))
            inherited_tm_moves = random.sample(tm_moves, num_tm_moves)
            moves.extend(inherited_tm_moves)
        
        # Ensure we don't exceed 4 moves
        return moves[:4]
    
    def _inherit_ability(self, mother: Pokemon, father: Pokemon) -> str:
        """Inherit ability from parents."""
        # Simplified ability inheritance
        if random.random() < self.ability_inheritance["hidden"]:
            return "Hidden Ability"
        else:
            return "Normal Ability"
    
    def _determine_shiny(self, pair: BreedingPair) -> bool:
        """Determine if the egg will be shiny."""
        shiny_chance = self.calculate_shiny_chance(pair)
        return random.random() < shiny_chance
    
    def _calculate_hatch_steps(self, species_id: int) -> int:
        """Calculate steps needed to hatch an egg."""
        # Simplified hatch steps calculation
        base_steps = 5120  # Base steps for most Pokemon
        
        # Some Pokemon have different hatch times
        if species_id in [25, 26]:  # Pikachu family
            base_steps = 2560
        elif species_id in [4, 5, 6]:  # Charmander family
            base_steps = 5120
        elif species_id in [448]:  # Lucario
            base_steps = 6400
        
        return base_steps
    
    def _get_base_stats(self, species_id: int) -> BaseStats:
        """Get base stats for a Pokemon species."""
        # Simplified base stats
        base_stats_dict = {
            25: {'hp': 35, 'attack': 55, 'defense': 40, 'special_attack': 50, 'special_defense': 50, 'speed': 90},
            6: {'hp': 78, 'attack': 84, 'defense': 78, 'special_attack': 109, 'special_defense': 85, 'speed': 100},
            448: {'hp': 70, 'attack': 110, 'defense': 70, 'special_attack': 115, 'special_defense': 70, 'speed': 90}
        }
        
        default_stats = {'hp': 50, 'attack': 50, 'defense': 50, 'special_attack': 50, 'special_defense': 50, 'speed': 50}
        stats = base_stats_dict.get(species_id, default_stats)
        
        return BaseStats(**stats)
    
    def _get_level_moves(self, species_id: int) -> List[str]:
        """Get level-up moves for a Pokemon species."""
        # Simplified level-up moves
        level_moves = {
            25: ["Thunder Shock", "Growl", "Thunder Wave", "Quick Attack"],
            6: ["Scratch", "Growl", "Ember", "Leer"],
            448: ["Quick Attack", "Foresight", "Endure", "Counter"]
        }
        
        return level_moves.get(species_id, ["Tackle", "Growl", "Scratch", "Leer"])
    
    def _get_tm_moves(self, species_id: int) -> List[str]:
        """Get TM moves for a Pokemon species."""
        # Simplified TM moves
        tm_moves = {
            25: ["Thunderbolt", "Thunder", "Iron Tail", "Dig"],
            6: ["Flamethrower", "Fire Blast", "Earthquake", "Rock Slide"],
            448: ["Aura Sphere", "Dragon Pulse", "Shadow Ball", "Psychic"]
        }
        
        return tm_moves.get(species_id, ["Toxic", "Protect", "Substitute", "Rest"])
    
    def _get_iv_inheritance_log(self, mother: Pokemon, father: Pokemon, pair: BreedingPair) -> Dict[str, str]:
        """Get a log of IV inheritance for display."""
        # This would be calculated during IV inheritance
        return {
            "hp": "from mother",
            "attack": "random",
            "defense": "from father",
            "special_attack": "random",
            "special_defense": "from mother",
            "speed": "random"
        }
    
    def _get_move_inheritance_log(self, mother: Pokemon, father: Pokemon) -> List[str]:
        """Get a log of move inheritance for display."""
        return ["Level-up moves", "Egg moves", "TM moves"]
    
    def _calculate_iv_optimization_score(self, pair: BreedingPair, target_ivs: Dict[str, int]) -> float:
        """Calculate how well a breeding pair can achieve target IVs."""
        score = 0.0
        
        # Check if parents have the target IVs
        for stat, target_value in target_ivs.items():
            parent1_iv = getattr(pair.parent1.ivs, stat)
            parent2_iv = getattr(pair.parent2.ivs, stat)
            
            if parent1_iv == target_value or parent2_iv == target_value:
                score += 0.2
        
        return min(score, 1.0)
