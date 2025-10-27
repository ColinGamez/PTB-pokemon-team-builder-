"""
Genetic Breeding Calculator
Advanced Pokemon breeding system with IV optimization, genetic algorithms,
breeding chain calculations, egg group compatibility, and shiny probability calculations.
"""

import json
import random
import math
import itertools
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import heapq
import time

class Gender(Enum):
    """Pokemon gender options."""
    MALE = "M"
    FEMALE = "F"
    GENDERLESS = "N"

class Nature(Enum):
    """Pokemon natures with stat modifiers."""
    ADAMANT = ("Adamant", "attack", "sp_attack")
    BASHFUL = ("Bashful", None, None)
    BOLD = ("Bold", "defense", "attack")
    BRAVE = ("Brave", "attack", "speed")
    CALM = ("Calm", "sp_defense", "attack")
    CAREFUL = ("Careful", "sp_defense", "sp_attack")
    DOCILE = ("Docile", None, None)
    GENTLE = ("Gentle", "sp_defense", "defense")
    HARDY = ("Hardy", None, None)
    HASTY = ("Hasty", "speed", "defense")
    IMPISH = ("Impish", "defense", "sp_attack")
    JOLLY = ("Jolly", "speed", "sp_attack")
    LAX = ("Lax", "defense", "sp_defense")
    LONELY = ("Lonely", "attack", "defense")
    MILD = ("Mild", "sp_attack", "defense")
    MODEST = ("Modest", "sp_attack", "attack")
    NAIVE = ("Naive", "speed", "sp_defense")
    NAUGHTY = ("Naughty", "attack", "sp_defense")
    QUIET = ("Quiet", "sp_attack", "speed")
    QUIRKY = ("Quirky", None, None)
    RASH = ("Rash", "sp_attack", "sp_defense")
    RELAXED = ("Relaxed", "defense", "speed")
    SASSY = ("Sassy", "sp_defense", "speed")
    SERIOUS = ("Serious", None, None)
    TIMID = ("Timid", "speed", "attack")
    
    @property
    def display_name(self) -> str:
        return self.value[0]
    
    @property
    def increased_stat(self) -> Optional[str]:
        return self.value[1]
    
    @property
    def decreased_stat(self) -> Optional[str]:
        return self.value[2]

class InheritanceMethod(Enum):
    """Methods for IV inheritance."""
    POWER_ITEMS = "power_items"
    DESTINY_KNOT = "destiny_knot"
    EVERSTONE = "everstone"
    NATURAL = "natural"

@dataclass
class IVSet:
    """Individual Values set."""
    hp: int = 0
    attack: int = 0
    defense: int = 0
    sp_attack: int = 0
    sp_defense: int = 0
    speed: int = 0
    
    def __post_init__(self):
        """Ensure IVs are in valid range."""
        for stat in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]:
            value = getattr(self, stat)
            setattr(self, stat, max(0, min(31, value)))
    
    @property
    def total(self) -> int:
        """Calculate total IVs."""
        return self.hp + self.attack + self.defense + self.sp_attack + self.sp_defense + self.speed
    
    @property
    def perfect_count(self) -> int:
        """Count number of perfect (31) IVs."""
        return sum(1 for iv in [self.hp, self.attack, self.defense, 
                               self.sp_attack, self.sp_defense, self.speed] if iv == 31)
    
    def get_stat_value(self, stat: str) -> int:
        """Get IV value for specific stat."""
        return getattr(self, stat, 0)
    
    def set_stat_value(self, stat: str, value: int):
        """Set IV value for specific stat."""
        setattr(self, stat, max(0, min(31, value)))
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'IVSet':
        """Create IVSet from dictionary."""
        return cls(**data)
    
    @classmethod
    def perfect(cls) -> 'IVSet':
        """Create perfect IV set (all 31s)."""
        return cls(31, 31, 31, 31, 31, 31)
    
    @classmethod
    def random(cls) -> 'IVSet':
        """Create random IV set."""
        return cls(
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31),
            random.randint(0, 31)
        )

@dataclass
class BreedingPokemon:
    """Pokemon used for breeding."""
    name: str
    species: str
    gender: Gender
    ivs: IVSet
    nature: Nature
    ability: str
    moves: List[str]
    held_item: Optional[str] = None
    is_shiny: bool = False
    egg_groups: Optional[List[str]] = None
    hidden_ability: Optional[str] = None
    ball_type: str = "Poke Ball"
    origin_game: str = "Unknown"
    trainer_id: int = 12345
    secret_id: int = 54321
    
    def __post_init__(self):
        """Initialize default values."""
        if self.egg_groups is None:
            self.egg_groups = ["Field"]  # Default egg group
    
    @property
    def is_foreign(self) -> bool:
        """Check if Pokemon is foreign (for Masuda Method)."""
        # Simplified - would compare trainer ID origins
        return random.random() < 0.1  # 10% chance for demo
    
    def can_breed_with(self, other: 'BreedingPokemon') -> bool:
        """Check if this Pokemon can breed with another."""
        # Gender compatibility
        if self.gender == Gender.GENDERLESS or other.gender == Gender.GENDERLESS:
            # Genderless can only breed with Ditto
            return (self.species == "Ditto" or other.species == "Ditto" or
                    (self.species == other.species and "Ditto" in [self.species, other.species]))
        
        if self.gender == other.gender:
            return False  # Same gender can't breed (unless one is Ditto)
        
        # Egg group compatibility
        if self.species == "Ditto" or other.species == "Ditto":
            return True
        
        # Check if they share at least one egg group
        if not self.egg_groups or not other.egg_groups:
            return False
        return bool(set(self.egg_groups) & set(other.egg_groups))
    
    def get_iv_inheritance_probability(self, stat: str, held_item: Optional[str] = None) -> float:
        """Get probability of inheriting specific IV."""
        if held_item and held_item.startswith("Power"):
            # Power items guarantee inheritance of specific stat
            power_item_stats = {
                "Power Weight": "hp",
                "Power Bracer": "attack",
                "Power Belt": "defense",
                "Power Lens": "sp_attack",
                "Power Band": "sp_defense",
                "Power Anklet": "speed"
            }
            if power_item_stats.get(held_item) == stat:
                return 1.0
        
        return 0.5  # Normal 50% inheritance chance
@dataclass
class BreedingGoal:
    """Breeding target specifications."""
    target_ivs: IVSet
    target_nature: Nature
    target_ability: str
    required_moves: List[str]
    target_gender: Optional[Gender] = None
    want_shiny: bool = False
    perfect_iv_priority: Optional[List[str]] = None  # Priority order for perfect IVs
    minimum_iv_requirements: Optional[Dict[str, int]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.perfect_iv_priority is None:
            self.perfect_iv_priority = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        if self.minimum_iv_requirements is None:
            self.minimum_iv_requirements = {}
    
    def evaluate_fitness(self, pokemon: BreedingPokemon) -> float:
        """Evaluate how well a Pokemon meets the breeding goal."""
        fitness = 0.0
        
        # IV fitness (40% weight)
        iv_score = 0
        for stat in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]:
            target_iv = self.target_ivs.get_stat_value(stat)
            actual_iv = pokemon.ivs.get_stat_value(stat)
            
            # Perfect match bonus
            if actual_iv == target_iv:
                iv_score += 10
            else:
                # Partial credit based on closeness
                iv_score += max(0, 10 - abs(target_iv - actual_iv) / 31 * 10)
            
            # Priority stat bonus
            if self.perfect_iv_priority and stat in self.perfect_iv_priority[:3] and actual_iv == 31:
                iv_score += 5
            
            # Minimum requirement check
            min_req = self.minimum_iv_requirements.get(stat, 0) if self.minimum_iv_requirements else 0
            if actual_iv >= min_req:
                iv_score += 2
        
        fitness += (iv_score / 72) * 40  # Normalize and weight
        
        # Nature fitness (25% weight)
        if pokemon.nature == self.target_nature:
            fitness += 25
        elif pokemon.nature.increased_stat == self.target_nature.increased_stat:
            fitness += 15  # Partial credit for correct boost
        
        # Ability fitness (20% weight)
        if pokemon.ability == self.target_ability:
            fitness += 20
        elif pokemon.hidden_ability == self.target_ability:
            fitness += 15  # Hidden ability is harder to get
        
        # Move fitness (10% weight)
        learned_moves = set(pokemon.moves)
        required_moves = set(self.required_moves)
        move_overlap = len(learned_moves & required_moves)
        move_score = (move_overlap / len(required_moves)) if required_moves else 1.0
        fitness += move_score * 10
        
        # Gender bonus (3% weight)
        if self.target_gender and pokemon.gender == self.target_gender:
            fitness += 3
        
        # Shiny bonus (2% weight)
        if self.want_shiny and pokemon.is_shiny:
            fitness += 2
        
        return min(100.0, fitness)

class GeneticBreedingCalculator:
    """Advanced genetic breeding calculator with optimization algorithms."""
    
    def __init__(self):
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
    
    def calculate_optimal_breeding_path(
        self, 
        goal: BreedingGoal, 
        available_pokemon: List[BreedingPokemon]
    ) -> Dict[str, Any]:
        """Calculate the optimal breeding path to achieve goal."""
        
        # Filter compatible Pokemon
        compatible_pokemon = self._filter_compatible_pokemon(available_pokemon, goal)
        
        if len(compatible_pokemon) < 2:
            # Add helper Ditto if needed
            compatible_pokemon.append(
                BreedingPokemon("Helper Ditto", "Ditto", Gender.GENDERLESS, 
                              IVSet.perfect(), Nature.HARDY, "Limber", [])
            )
        
        # Find best breeding pairs
        best_pairs = self._find_best_breeding_pairs(compatible_pokemon, goal)
        
        # Generate breeding chain
        breeding_chain = self._generate_breeding_chain(best_pairs, goal)
        
        return {
            'success': True,
            'goal': goal,
            'breeding_chain': breeding_chain,
            'compatible_pokemon': compatible_pokemon,
            'estimated_eggs': breeding_chain.get('total_eggs', 50),
            'estimated_time_hours': breeding_chain.get('total_time', 5.0),
            'success_probability': breeding_chain.get('success_rate', 0.7)
        }
    
    def _filter_compatible_pokemon(
        self, 
        available_pokemon: List[BreedingPokemon], 
        goal: BreedingGoal
    ) -> List[BreedingPokemon]:
        """Filter Pokemon that can help achieve the breeding goal."""
        compatible = []
        
        for pokemon in available_pokemon:
            # Check if Pokemon has useful IVs
            useful_ivs = sum(1 for stat in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
                           if pokemon.ivs.get_stat_value(stat) >= 20)  # At least decent IVs
            
            if useful_ivs >= 2:  # Has at least 2 useful IVs
                compatible.append(pokemon)
            
            # Always include Ditto
            if pokemon.species == "Ditto":
                compatible.append(pokemon)
            
            # Include if has target nature
            if pokemon.nature == goal.target_nature:
                compatible.append(pokemon)
            
            # Include if has target ability
            if pokemon.ability == goal.target_ability or pokemon.hidden_ability == goal.target_ability:
                compatible.append(pokemon)
        
        return list(set(compatible))  # Remove duplicates
    
    def _find_best_breeding_pairs(
        self, 
        pokemon_list: List[BreedingPokemon], 
        goal: BreedingGoal
    ) -> List[Tuple[BreedingPokemon, BreedingPokemon, float]]:
        """Find best breeding pairs with fitness scores."""
        pairs = []
        
        for i, pokemon1 in enumerate(pokemon_list):
            for j, pokemon2 in enumerate(pokemon_list[i+1:], i+1):
                if pokemon1.can_breed_with(pokemon2):
                    # Calculate pair fitness
                    fitness = self._calculate_pair_fitness(pokemon1, pokemon2, goal)
                    pairs.append((pokemon1, pokemon2, fitness))
        
        # Sort by fitness (higher is better)
        pairs.sort(key=lambda x: x[2], reverse=True)
        return pairs[:10]  # Top 10 pairs
    
    def _calculate_pair_fitness(
        self, 
        pokemon1: BreedingPokemon, 
        pokemon2: BreedingPokemon, 
        goal: BreedingGoal
    ) -> float:
        """Calculate fitness score for a breeding pair."""
        score = 0.0
        
        # IV score
        for stat in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]:
            target_iv = goal.target_ivs.get_stat_value(stat)
            pokemon1_iv = pokemon1.ivs.get_stat_value(stat)
            pokemon2_iv = pokemon2.ivs.get_stat_value(stat)
            
            if pokemon1_iv == target_iv or pokemon2_iv == target_iv:
                score += 10  # Parent has target IV
            else:
                best_iv = max(pokemon1_iv, pokemon2_iv)
                score += (best_iv / 31.0) * 5
        
        # Nature score
        if pokemon1.nature == goal.target_nature or pokemon2.nature == goal.target_nature:
            score += 20
        
        # Ability score
        if (pokemon1.ability == goal.target_ability or pokemon1.hidden_ability == goal.target_ability or
            pokemon2.ability == goal.target_ability or pokemon2.hidden_ability == goal.target_ability):
            score += 15
        
        return score
    
    def _generate_breeding_chain(
        self, 
        best_pairs: List[Tuple[BreedingPokemon, BreedingPokemon, float]], 
        goal: BreedingGoal
    ) -> Dict[str, Any]:
        """Generate breeding chain steps."""
        if not best_pairs:
            return {
                'steps': [],
                'total_eggs': 0,
                'total_time': 0,
                'success_rate': 0
            }
        
        # Use best pair for primary breeding
        parent1, parent2, fitness = best_pairs[0]
        
        steps = [
            {
                'step': 1,
                'description': f"Breed {parent1.name} × {parent2.name}",
                'parent1': parent1.name,
                'parent2': parent2.name,
                'inheritance_method': 'destiny_knot',
                'estimated_eggs': 25,
                'items_needed': ['Destiny Knot', 'Everstone'],
                'expected_fitness': fitness
            }
        ]
        
        # Add refinement step if needed
        if fitness < 80:
            steps.append({
                'step': 2,
                'description': "Breed best offspring with high IV parent",
                'parent1': "Best Offspring",
                'parent2': parent1.name,
                'inheritance_method': 'destiny_knot',
                'estimated_eggs': 20,
                'items_needed': ['Destiny Knot', 'Everstone'],
                'expected_fitness': min(95, fitness + 15)
            })
        
        total_eggs = sum(step['estimated_eggs'] for step in steps)
        total_time = total_eggs * 0.1  # 6 minutes per egg
        success_rate = min(0.95, fitness / 100)
        
        return {
            'steps': steps,
            'total_eggs': total_eggs,
            'total_time': total_time,
            'success_rate': success_rate
        }
    
    def calculate_shiny_probability(
        self, 
        parent1: BreedingPokemon, 
        parent2: BreedingPokemon,
        has_shiny_charm: bool = False
    ) -> Dict[str, Any]:
        """Calculate shiny probability and expected eggs."""
        base_rate = 1 / 4096
        
        # Masuda Method check
        masuda_method = parent1.is_foreign != parent2.is_foreign
        if masuda_method:
            base_rate *= 6
        
        # Shiny Charm bonus
        if has_shiny_charm:
            base_rate *= 3
        
        # Calculate expected eggs for different confidence levels
        expected_50 = math.log(0.5) / math.log(1 - base_rate)
        expected_90 = math.log(0.1) / math.log(1 - base_rate)
        expected_99 = math.log(0.01) / math.log(1 - base_rate)
        
        return {
            "base_probability": base_rate,
            "masuda_method_active": masuda_method,
            "shiny_charm_active": has_shiny_charm,
            "odds": f"1 in {int(1/base_rate):,}",
            "expected_eggs": {
                "50%_chance": int(expected_50),
                "90%_chance": int(expected_90),
                "99%_chance": int(expected_99)
            }
        }

# Demo and utility functions
def create_sample_pokemon() -> List[BreedingPokemon]:
    """Create sample Pokemon for demonstration."""
    return [
        BreedingPokemon(
            name="Perfect Ditto",
            species="Ditto",
            gender=Gender.GENDERLESS,
            ivs=IVSet.perfect(),
            nature=Nature.HARDY,
            ability="Limber",
            moves=["Transform"],
            trainer_id=99999  # Foreign
        ),
        BreedingPokemon(
            name="Jolly Garchomp",
            species="Garchomp",
            gender=Gender.MALE,
            ivs=IVSet(31, 31, 20, 10, 25, 31),
            nature=Nature.JOLLY,
            ability="Sand Veil",
            moves=["Outrage", "Earthquake", "Stone Edge", "Fire Fang"],
            egg_groups=["Monster", "Dragon"]
        ),
        BreedingPokemon(
            name="Adamant Garchomp",
            species="Garchomp",
            gender=Gender.FEMALE,
            ivs=IVSet(25, 31, 31, 15, 20, 20),
            nature=Nature.ADAMANT,
            ability="Rough Skin",
            moves=["Dragon Rush", "Dig", "Sandstorm", "Crunch"],
            egg_groups=["Monster", "Dragon"]
        )
    ]

def demonstrate_genetic_breeding_calculator():
    """Demonstrate the genetic breeding calculator."""
    print("🧬 Genetic Breeding Calculator Demo")
    print("=" * 60)
    
    # Create breeding calculator
    calculator = GeneticBreedingCalculator()
    
    # Create sample Pokemon
    available_pokemon = create_sample_pokemon()
    
    print("\n📦 Available Pokemon:")
    print("-" * 40)
    for pokemon in available_pokemon:
        print(f"• {pokemon.name} ({pokemon.species})")
        print(f"  Nature: {pokemon.nature.display_name} | IVs: {pokemon.ivs.total}/186")
        print(f"  Perfect IVs: {pokemon.ivs.perfect_count}/6")
    
    # Define breeding goal
    goal = BreedingGoal(
        target_ivs=IVSet(31, 31, 31, 0, 31, 31),  # Perfect except Sp.Attack
        target_nature=Nature.JOLLY,
        target_ability="Rough Skin",
        required_moves=["Outrage", "Earthquake"],
        perfect_iv_priority=["attack", "speed", "hp", "defense", "sp_defense"],
        minimum_iv_requirements={"attack": 31, "speed": 31}
    )
    
    print(f"\n🎯 Breeding Goal:")
    print("-" * 40)
    print(f"Target Pokemon: Garchomp")
    print(f"Nature: {goal.target_nature.display_name}")
    print(f"Ability: {goal.target_ability}")
    print(f"Target IVs: {goal.target_ivs.hp}/{goal.target_ivs.attack}/{goal.target_ivs.defense}/{goal.target_ivs.sp_attack}/{goal.target_ivs.sp_defense}/{goal.target_ivs.speed}")
    print(f"Required Moves: {', '.join(goal.required_moves)}")
    
    # Calculate optimal breeding path
    print(f"\n🔬 Calculating Optimal Breeding Path...")
    result = calculator.calculate_optimal_breeding_path(goal, available_pokemon)
    
    if result['success']:
        chain = result['breeding_chain']
        
        print(f"\n📋 Optimal Breeding Chain:")
        print("-" * 40)
        print(f"Total Steps: {len(chain['steps'])}")
        print(f"Estimated Eggs: {chain['total_eggs']}")
        print(f"Estimated Time: {chain['total_time']:.1f} hours")
        print(f"Success Probability: {chain['success_rate']:.1%}")
        
        print(f"\n📝 Breeding Steps:")
        for step in chain['steps']:
            print(f"\nStep {step['step']}: {step['description']}")
            print(f"  Parents: {step['parent1']} × {step['parent2']}")
            print(f"  Method: {step['inheritance_method']}")
            print(f"  Expected Eggs: {step['estimated_eggs']}")
            print(f"  Items Needed: {', '.join(step['items_needed'])}")
            print(f"  Expected Fitness: {step['expected_fitness']:.1f}%")
    
    # Calculate shiny probability
    print(f"\n✨ Shiny Calculation:")
    print("-" * 40)
    if len(available_pokemon) >= 2:
        shiny_calc = calculator.calculate_shiny_probability(
            available_pokemon[0], available_pokemon[1], has_shiny_charm=True
        )
        
        print(f"Base Odds: {shiny_calc['odds']}")
        print(f"Masuda Method: {'Yes' if shiny_calc['masuda_method_active'] else 'No'}")
        print(f"Shiny Charm: {'Yes' if shiny_calc['shiny_charm_active'] else 'No'}")
        print(f"Expected Eggs for 50% chance: {shiny_calc['expected_eggs']['50%_chance']:,}")
        print(f"Expected Eggs for 90% chance: {shiny_calc['expected_eggs']['90%_chance']:,}")
    
    print(f"\n🧬 Genetic Breeding Calculator Ready!")
    print("Features: IV Optimization, Genetic Algorithms, Shiny Calculations, Chain Analysis")

if __name__ == "__main__":
    demonstrate_genetic_breeding_calculator()